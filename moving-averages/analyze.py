"""Moving-average graveyard teardown — full analysis engine.
Implements the LOCKED pre-registration (00-preregistration.md), which reuses the RSI
teardown's methodology verbatim with MA signals swapped in.

Every signal evaluated directionally (long / short), per-asset AND pooled, horizons
5/10/20 (primary 10), against a volatility+regime (close vs SMA200) matched control on
the same asset. Edge = signal mean return - matched control mean return. Effective n =
distinct de-clustered episodes. Bootstrap p via matched-bucket resampling.

Only build() + base_events() + the SIGNALS catalog differ from the RSI engine; the
matched control, effective-n, bootstrap, excursion and pooling code is identical.

Outputs: results.csv (tidy), results.json (nested), printed sanity summary.
"""
import csv, json, os, numpy as np
from ma_lib import sma, ema, atr_wilder

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "data")
ASSETS = ["BTC", "SPX", "XAUUSD", "EURUSD"]
HORIZONS = [5, 10, 20]
PRIMARY = 10
SMA_TREND = 200
ATR_LEN = 14
B = 10000
rng = np.random.default_rng(20261019)


def load(asset):
    dates, o, h, l, c = [], [], [], [], []
    for r in csv.DictReader(open(os.path.join(DATA, f"{asset}.csv"))):
        dates.append(r["date"]); o.append(float(r["open"])); h.append(float(r["high"]))
        l.append(float(r["low"])); c.append(float(r["close"]))
    return dates, np.array(o), np.array(h), np.array(l), np.array(c)


def build(asset):
    """Return a dict of per-bar arrays + precomputed forward/excursion metrics."""
    dates, o, hi, lo, cl = load(asset)
    n = len(cl)
    atr = atr_wilder(hi, lo, cl, ATR_LEN)
    atrpct = atr / cl

    MA = dict(
        sma9=sma(cl, 9), sma12=sma(cl, 12), sma20=sma(cl, 20), sma21=sma(cl, 21),
        sma26=sma(cl, 26), sma50=sma(cl, 50), sma200=sma(cl, 200),
        ema9=ema(cl, 9), ema12=ema(cl, 12), ema20=ema(cl, 20), ema21=ema(cl, 21),
        ema26=ema(cl, 26), ema50=ema(cl, 50), ema200=ema(cl, 200),
    )

    ret1 = np.concatenate([[0.0], cl[1:] / cl[:-1] - 1.0])

    # base validity: longest MAs used (sma200, ema200) + ATR, so every signal shares one
    # denominator (mirrors the RSI engine's rsi&trend&atr gate).
    ind_valid = ~np.isnan(MA["sma200"]) & ~np.isnan(MA["ema200"]) & ~np.isnan(atr) & (atr > 0)

    vv = atrpct[ind_valid]
    q1, q2 = np.nanquantile(vv, [1/3, 2/3])
    volbucket = np.full(n, -1)
    volbucket[ind_valid & (atrpct <= q1)] = 0
    volbucket[ind_valid & (atrpct > q1) & (atrpct <= q2)] = 1
    volbucket[ind_valid & (atrpct > q2)] = 2
    regime = np.where(cl > MA["sma200"], 1, 0)  # 1 up, 0 down (close vs 200d SMA)
    bucket = np.where(ind_valid, regime * 3 + volbucket, -1)

    fwd = {}; mfe_l = {}; mae_l = {}; mfe_s = {}; mae_s = {}
    hit_l = {}; hit_s = {}; valid_h = {}
    for H in HORIZONS:
        f = np.full(n, np.nan)
        ml = np.full(n, np.nan); al = np.full(n, np.nan)
        ms = np.full(n, np.nan); as_ = np.full(n, np.nan)
        hl = np.full(n, np.nan); hs = np.full(n, np.nan)
        vh = np.zeros(n, bool)
        for t in range(n):
            if t + H >= n:
                continue
            if not ind_valid[t]:
                continue
            f[t] = cl[t + H] / cl[t] - 1.0
            win_hi = hi[t+1:t+H+1]; win_lo = lo[t+1:t+H+1]
            a = atr[t]
            ml[t] = (win_hi.max() - cl[t]) / a
            al[t] = (win_lo.min() - cl[t]) / a
            ms[t] = (cl[t] - win_lo.min()) / a
            as_[t] = (cl[t] - win_hi.max()) / a
            hl[t] = _first_touch(win_hi, win_lo, cl[t] + a, cl[t] - a, long=True)
            hs[t] = _first_touch(win_hi, win_lo, cl[t] - a, cl[t] + a, long=False)
            vh[t] = True
        fwd[H] = f; mfe_l[H] = ml; mae_l[H] = al; mfe_s[H] = ms; mae_s[H] = as_
        hit_l[H] = hl; hit_s[H] = hs; valid_h[H] = vh

    D = dict(asset=asset, dates=dates, n=n, o=o, hi=hi, lo=lo, cl=cl,
             atr=atr, atrpct=atrpct, ret1=ret1,
             ind_valid=ind_valid, regime=regime, volbucket=volbucket, bucket=bucket,
             fwd=fwd, mfe_l=mfe_l, mae_l=mae_l, mfe_s=mfe_s, mae_s=mae_s,
             hit_l=hit_l, hit_s=hit_s, valid_h=valid_h, q1=q1, q2=q2)
    D.update(MA)
    return D


def _first_touch(win_hi, win_lo, up_level, dn_level, long=True):
    """1.0 if +1R target touched before -1R stop, else 0.0. Same-bar tie -> stop first."""
    if long:
        for j in range(len(win_hi)):
            hit_up = win_hi[j] >= up_level
            hit_dn = win_lo[j] <= dn_level
            if hit_up and hit_dn:
                return 0.0
            if hit_up:
                return 1.0
            if hit_dn:
                return 0.0
        return 0.0
    else:
        tgt = up_level; stop = dn_level
        for j in range(len(win_hi)):
            hit_tgt = win_lo[j] <= tgt
            hit_stop = win_hi[j] >= stop
            if hit_tgt and hit_stop:
                return 0.0
            if hit_tgt:
                return 1.0
            if hit_stop:
                return 0.0
        return 0.0


# ---------- base event detection ----------
def state_bars(mask, ind_valid):
    """All valid in-state bars (NOT onset-only): price-above-MA is a persistent condition,
    so the state is sampled throughout and de-clustered by horizon downstream."""
    return np.where(mask & ind_valid)[0]


def cross_above(a, b):
    pa = np.concatenate([[np.nan], a[:-1]]); pb = np.concatenate([[np.nan], b[:-1]])
    return np.where((pa <= pb) & (a > b))[0]


def cross_below(a, b):
    pa = np.concatenate([[np.nan], a[:-1]]); pb = np.concatenate([[np.nan], b[:-1]])
    return np.where((pa >= pb) & (a < b))[0]


def decluster(idx, H):
    """greedy: keep first, skip events within H bars (non-overlapping fwd windows)."""
    out = []; last = -10**9
    for i in sorted(idx):
        if i - last >= H:
            out.append(i); last = i
    return np.array(out, dtype=int)


def base_events(D, key):
    cl = D["cl"]; iv = D["ind_valid"]
    # price vs MA — STATE (all in-state bars)
    if key == "st_sma50_up":   return state_bars(cl > D["sma50"], iv)
    if key == "st_sma50_dn":   return state_bars(cl < D["sma50"], iv)
    if key == "st_sma200_up":  return state_bars(cl > D["sma200"], iv)
    if key == "st_sma200_dn":  return state_bars(cl < D["sma200"], iv)
    # price crossing a MA — EVENT
    if key == "pxu_sma50":     return cross_above(cl, D["sma50"])
    if key == "pxd_sma50":     return cross_below(cl, D["sma50"])
    if key == "pxu_sma200":    return cross_above(cl, D["sma200"])
    if key == "pxd_sma200":    return cross_below(cl, D["sma200"])
    # MA-MA crosses (fast, slow), SMA and EMA
    if key == "sma_50_200_u":  return cross_above(D["sma50"], D["sma200"])
    if key == "sma_50_200_d":  return cross_below(D["sma50"], D["sma200"])
    if key == "ema_50_200_u":  return cross_above(D["ema50"], D["ema200"])
    if key == "ema_50_200_d":  return cross_below(D["ema50"], D["ema200"])
    if key == "sma_20_50_u":   return cross_above(D["sma20"], D["sma50"])
    if key == "sma_20_50_d":   return cross_below(D["sma20"], D["sma50"])
    if key == "ema_20_50_u":   return cross_above(D["ema20"], D["ema50"])
    if key == "ema_20_50_d":   return cross_below(D["ema20"], D["ema50"])
    if key == "sma_9_21_u":    return cross_above(D["sma9"], D["sma21"])
    if key == "sma_9_21_d":    return cross_below(D["sma9"], D["sma21"])
    if key == "ema_9_21_u":    return cross_above(D["ema9"], D["ema21"])
    if key == "ema_9_21_d":    return cross_below(D["ema9"], D["ema21"])
    if key == "sma_12_26_u":   return cross_above(D["sma12"], D["sma26"])
    if key == "sma_12_26_d":   return cross_below(D["sma12"], D["sma26"])
    if key == "ema_12_26_u":   return cross_above(D["ema12"], D["ema26"])
    if key == "ema_12_26_d":   return cross_below(D["ema12"], D["ema26"])
    # MA-as-support (uptrend pullback that holds)
    if key == "sup_sma50":
        m = (cl > D["sma200"]) & (cl >= D["sma50"]) & (D["lo"] <= D["sma50"] + 0.5 * D["atr"])
        return state_bars(m, iv)
    if key == "sup_sma200":
        m = (cl >= D["sma200"]) & (D["lo"] <= D["sma200"] + 0.5 * D["atr"])
        return state_bars(m, iv)
    raise ValueError(key)


# (name, base_key, direction, label)
SIGNALS = [
    ("state_sma50_long",   "st_sma50_up",  "long",  "price > SMA50 (state) -> long"),
    ("state_sma50_short",  "st_sma50_dn",  "short", "price < SMA50 (state) -> short"),
    ("state_sma200_long",  "st_sma200_up", "long",  "price > SMA200 (state) -> long [TAUTOLOGY]"),
    ("state_sma200_short", "st_sma200_dn", "short", "price < SMA200 (state) -> short [TAUTOLOGY]"),
    ("pxcross_sma50_long", "pxu_sma50",    "long",  "price crosses up through SMA50 -> long"),
    ("pxcross_sma50_short","pxd_sma50",    "short", "price crosses down through SMA50 -> short"),
    ("pxcross_sma200_long","pxu_sma200",   "long",  "price crosses up through SMA200 -> long"),
    ("pxcross_sma200_short","pxd_sma200",  "short", "price crosses down through SMA200 -> short"),
    ("golden_sma_50_200",  "sma_50_200_u", "long",  "SMA50 crosses above SMA200 (GOLDEN) -> long"),
    ("death_sma_50_200",   "sma_50_200_d", "short", "SMA50 crosses below SMA200 (DEATH) -> short"),
    ("golden_ema_50_200",  "ema_50_200_u", "long",  "EMA50 crosses above EMA200 -> long"),
    ("death_ema_50_200",   "ema_50_200_d", "short", "EMA50 crosses below EMA200 -> short"),
    ("sma_20_50_up",       "sma_20_50_u",  "long",  "SMA20 crosses above SMA50 -> long"),
    ("sma_20_50_dn",       "sma_20_50_d",  "short", "SMA20 crosses below SMA50 -> short"),
    ("ema_20_50_up",       "ema_20_50_u",  "long",  "EMA20 crosses above EMA50 -> long"),
    ("ema_20_50_dn",       "ema_20_50_d",  "short", "EMA20 crosses below EMA50 -> short"),
    ("sma_9_21_up",        "sma_9_21_u",   "long",  "SMA9 crosses above SMA21 -> long"),
    ("sma_9_21_dn",        "sma_9_21_d",   "short", "SMA9 crosses below SMA21 -> short"),
    ("ema_9_21_up",        "ema_9_21_u",   "long",  "EMA9 crosses above EMA21 -> long"),
    ("ema_9_21_dn",        "ema_9_21_d",   "short", "EMA9 crosses below EMA21 -> short"),
    ("sma_12_26_up",       "sma_12_26_u",  "long",  "SMA12 crosses above SMA26 -> long"),
    ("sma_12_26_dn",       "sma_12_26_d",  "short", "SMA12 crosses below SMA26 -> short"),
    ("ema_12_26_up",       "ema_12_26_u",  "long",  "EMA12 crosses above EMA26 -> long"),
    ("ema_12_26_dn",       "ema_12_26_d",  "short", "EMA12 crosses below EMA26 -> short"),
    ("support_sma50",      "sup_sma50",    "long",  "uptrend pullback holds SMA50 -> long"),
    ("support_sma200",     "sup_sma200",   "long",  "uptrend pullback holds SMA200 -> long"),
]


def dir_arrays(D, direction, H):
    if direction == "long":
        return D["fwd"][H], D["mfe_l"][H], D["mae_l"][H], D["hit_l"][H]
    else:
        return -D["fwd"][H], D["mfe_s"][H], D["mae_s"][H], D["hit_s"][H]


def bucket_pools(D, direction, H):
    dr, _, _, _ = dir_arrays(D, direction, H)
    vh = D["valid_h"][H]; bkt = D["bucket"]
    pools = {}
    for b in range(6):
        m = vh & (bkt == b) & ~np.isnan(dr)
        pools[b] = dr[m]
    return pools


def evaluate(D, sig, H, trend_cond):
    name, key, direction, _ = sig
    idx = base_events(D, key)
    vh = D["valid_h"][H]
    idx = idx[np.isin(idx, np.where(vh)[0])]
    if trend_cond:
        want_up = (direction == "long")
        reg = D["regime"]
        idx = idx[reg[idx] == (1 if want_up else 0)]
    n_raw = len(idx)
    idx = decluster(idx, H)
    n_eff = len(idx)
    if n_eff == 0:
        return None
    dr, mfe, mae, hit = dir_arrays(D, direction, H)
    good = ~np.isnan(dr[idx]); idx = idx[good]
    n_eff = len(idx)
    if n_eff == 0:
        return None
    rets = dr[idx]
    bkt = D["bucket"][idx]
    pools = bucket_pools(D, direction, H)
    ctrl_mean_by_b = {b: (pools[b].mean() if len(pools[b]) else np.nan) for b in pools}
    ctrl_win_by_b = {b: ((pools[b] > 0).mean() if len(pools[b]) else np.nan) for b in pools}
    ctrl_ret = np.nanmean([ctrl_mean_by_b[b] for b in bkt])
    ctrl_win = np.nanmean([ctrl_win_by_b[b] for b in bkt])

    sig_ret = rets.mean()
    edge = sig_ret - ctrl_ret
    win = (rets > 0).mean()
    aw = rets[rets > 0].mean() if (rets > 0).any() else 0.0
    al = rets[rets < 0].mean() if (rets < 0).any() else 0.0
    sharpe = rets.mean() / rets.std(ddof=1) if n_eff > 1 and rets.std(ddof=1) > 0 else np.nan

    mfe_m = np.nanmean(mfe[idx]); mae_m = np.nanmean(mae[idx]); hit_m = np.nanmean(hit[idx])

    def bucket_mean_arr(arr):
        vals = []
        for b in bkt:
            m = D["valid_h"][H] & (D["bucket"] == b) & ~np.isnan(arr)
            vals.append(arr[m].mean() if m.any() else np.nan)
        return np.nanmean(vals)
    ctrl_mfe = bucket_mean_arr(mfe); ctrl_mae = bucket_mean_arr(mae); ctrl_hit = bucket_mean_arr(hit)

    pool_arrs = [pools[b] for b in bkt]
    if all(len(p) > 0 for p in pool_arrs):
        samp = np.empty((n_eff, B))
        for i, p in enumerate(pool_arrs):
            samp[i] = p[rng.integers(0, len(p), B)]
        null_means = samp.mean(axis=0)
        null_edge = null_means - ctrl_ret
        p_two = (np.abs(null_edge) >= abs(edge)).mean()
    else:
        p_two = np.nan

    return dict(signal=name, direction=direction, layer=("trend" if trend_cond else "naive"),
                horizon=H, n_raw=n_raw, n_eff=n_eff,
                sig_ret=sig_ret, ctrl_ret=ctrl_ret, edge=edge, p=p_two,
                win=win, ctrl_win=ctrl_win, avg_win=aw, avg_loss=al, sharpe=sharpe,
                mfe_R=mfe_m, mae_R=mae_m, ctrl_mfe_R=ctrl_mfe, ctrl_mae_R=ctrl_mae,
                hit1=hit_m, ctrl_hit1=ctrl_hit,
                idx=idx.tolist(), rets=rets.tolist(), bkt=bkt.tolist())


def evaluate_pooled(DS, sig, H, trend_cond):
    all_rets = []; all_ctrl = []; all_bkt_pool = []
    n_raw = 0; n_eff = 0
    mfe=[]; mae=[]; hit=[]; cmfe=[]; cmae=[]; chit=[]; cwin=[]; wins=[]
    name, key, direction, _ = sig
    for D in DS:
        r = evaluate(D, sig, H, trend_cond)
        if r is None:
            continue
        n_raw += r["n_raw"]; n_eff += r["n_eff"]
        all_rets.extend(r["rets"])
        pools = bucket_pools(D, direction, H)
        for b in r["bkt"]:
            all_ctrl.append(pools[b].mean())
            all_bkt_pool.append(pools[b])
        mfe.append(r["mfe_R"]*r["n_eff"]); mae.append(r["mae_R"]*r["n_eff"]); hit.append(r["hit1"]*r["n_eff"])
        cmfe.append(r["ctrl_mfe_R"]*r["n_eff"]); cmae.append(r["ctrl_mae_R"]*r["n_eff"]); chit.append(r["ctrl_hit1"]*r["n_eff"])
        cwin.append(r["ctrl_win"]*r["n_eff"]); wins.append(r["win"]*r["n_eff"])
    if n_eff == 0:
        return None
    rets = np.array(all_rets); ctrl = np.array(all_ctrl)
    sig_ret = rets.mean(); ctrl_ret = np.nanmean(ctrl); edge = sig_ret - ctrl_ret
    sharpe = rets.mean()/rets.std(ddof=1) if n_eff>1 and rets.std(ddof=1)>0 else np.nan
    win = (rets>0).mean()
    aw = rets[rets>0].mean() if (rets>0).any() else 0.0
    al = rets[rets<0].mean() if (rets<0).any() else 0.0
    if all(len(p)>0 for p in all_bkt_pool):
        samp = np.empty((n_eff, B))
        for i,p in enumerate(all_bkt_pool):
            samp[i]=p[rng.integers(0,len(p),B)]
        null_edge = samp.mean(axis=0) - ctrl_ret
        p_two = (np.abs(null_edge)>=abs(edge)).mean()
    else:
        p_two=np.nan
    W=n_eff
    return dict(signal=name, direction=direction, layer=("trend" if trend_cond else "naive"),
                horizon=H, n_raw=n_raw, n_eff=n_eff,
                sig_ret=sig_ret, ctrl_ret=ctrl_ret, edge=edge, p=p_two,
                win=win, ctrl_win=sum(cwin)/W, avg_win=aw, avg_loss=al, sharpe=sharpe,
                mfe_R=sum(mfe)/W, mae_R=sum(mae)/W, ctrl_mfe_R=sum(cmfe)/W, ctrl_mae_R=sum(cmae)/W,
                hit1=sum(hit)/W, ctrl_hit1=sum(chit)/W)


def main():
    print("building assets...")
    DS = []; meta = {}
    for a in ASSETS:
        D = build(a); DS.append(D)
        thr = 0.5 if a == "BTC" else 0.2
        ext = np.where(np.abs(D["ret1"]) > thr)[0]
        meta[a] = dict(n=D["n"], start=D["dates"][0], end=D["dates"][-1],
                       ind_valid=int(D["ind_valid"].sum()),
                       volq=[round(float(D["q1"]),5), round(float(D["q2"]),5)],
                       n_extreme=int(len(ext)))
        print(f"  {a}: n={D['n']} {D['dates'][0]}..{D['dates'][-1]} valid={int(D['ind_valid'].sum())} "
              f"volq={meta[a]['volq']} extreme(|r1|>{thr})={len(ext)}")

    rows = []
    for sig in SIGNALS:
        for tc in (False, True):
            for H in HORIZONS:
                for D in DS:
                    r = evaluate(D, sig, H, tc)
                    if r:
                        r2 = {k: v for k, v in r.items() if k not in ("idx","rets","bkt")}
                        r2["scope"] = D["asset"]; rows.append(r2)
                rp = evaluate_pooled(DS, sig, H, tc)
                if rp:
                    rp["scope"] = "POOLED"; rows.append(rp)

    cols = ["signal","direction","layer","scope","horizon","n_raw","n_eff",
            "sig_ret","ctrl_ret","edge","p","win","ctrl_win","avg_win","avg_loss",
            "sharpe","mfe_R","mae_R","ctrl_mfe_R","ctrl_mae_R","hit1","ctrl_hit1"]
    with open(os.path.join(HERE, "results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c) for c in cols})
    json.dump({"meta": meta, "rows": rows}, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=float)
    print(f"\nwrote {len(rows)} result rows -> results.csv / results.json")

    print(f"\n=== POOLED, naive, H={PRIMARY} (signal / control / edge / p / n_eff) ===")
    for r in rows:
        if r["scope"]=="POOLED" and r["layer"]=="naive" and r["horizon"]==PRIMARY:
            print(f"  {r['signal']:22s} {r['direction']:5s} {r['sig_ret']*100:7.3f}% ({r['ctrl_ret']*100:7.3f}%)  "
                  f"edge {r['edge']*100:+7.3f}%  p={r['p']:.3f}  n={r['n_eff']}")

if __name__ == "__main__":
    main()
