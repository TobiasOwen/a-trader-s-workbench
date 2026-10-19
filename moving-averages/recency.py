"""Recency robustness: does the MA conclusion hold in the era people actually trade?
Recompute key signals on the last 10y and 5y (vol terciles recomputed WITHIN each window
so the matched control is fair to that window), primary horizon 10, naive layer.
Indicators keep full-history warmup; only the analysis universe is windowed.
"""
import numpy as np, datetime as dt
from analyze import build, base_events, decluster, dir_arrays, ASSETS

H = 10
rng = np.random.default_rng(99)
TODAY = dt.date(2026, 10, 17)
WINDOWS = [("full", None), ("10y", TODAY.replace(year=TODAY.year-10)), ("5y", TODAY.replace(year=TODAY.year-5))]
KEYS = [
    ("golden_sma_50_200", "sma_50_200_u", "long"),
    ("death_sma_50_200", "sma_50_200_d", "short"),
    ("state_sma50_long", "st_sma50_up", "long"),
    ("sma_9_21_up", "sma_9_21_u", "long"),
    ("ema_9_21_up", "ema_9_21_u", "long"),
    ("support_sma50", "sup_sma50", "long"),
]
DS = {a: build(a) for a in ASSETS}
DATES = {a: np.array([dt.date.fromisoformat(d) for d in DS[a]["dates"]]) for a in ASSETS}
rng_B = 10000


def windowed_buckets(D, wmask):
    atrpct = D["atrpct"]; valid = D["valid_h"][H] & wmask
    vv = atrpct[valid]
    if len(vv) < 30:
        return None
    q1, q2 = np.nanquantile(vv, [1/3, 2/3])
    volb = np.full(D["n"], -1)
    volb[valid & (atrpct <= q1)] = 0
    volb[valid & (atrpct > q1) & (atrpct <= q2)] = 1
    volb[valid & (atrpct > q2)] = 2
    return np.where(valid, D["regime"]*3 + volb, -1)


def eval_window(D, key, direction, wmask):
    bkt = windowed_buckets(D, wmask)
    if bkt is None:
        return None
    dr, _, _, _ = dir_arrays(D, direction, H)
    pools = {}
    for b in range(6):
        m = D["valid_h"][H] & wmask & (bkt == b) & ~np.isnan(dr)
        pools[b] = dr[m]
    idx = base_events(D, key)
    idx = idx[wmask[idx] & D["valid_h"][H][idx]]
    idx = decluster(idx, H)
    idx = idx[~np.isnan(dr[idx])]
    if len(idx) < 3:
        return dict(n=len(idx), insufficient=True)
    rets = dr[idx]; b = bkt[idx]
    if np.any(b < 0) or any(len(pools[bb]) == 0 for bb in b):
        return dict(n=len(idx), insufficient=True)
    ctrl = np.mean([pools[bb].mean() for bb in b])
    edge = rets.mean() - ctrl
    samp = np.empty((len(idx), rng_B))
    for i, bb in enumerate(b):
        samp[i] = pools[bb][rng.integers(0, len(pools[bb]), rng_B)]
    p = (np.abs(samp.mean(axis=0) - ctrl) >= abs(edge)).mean()
    return dict(n=len(idx), sig=rets.mean(), ctrl=ctrl, edge=edge, p=p, win=(rets > 0).mean())


for name, key, direction in KEYS:
    print(f"### {name} [{direction}]  H={H}")
    print(f"  {'window':6s} {'BTC':>22s} {'SPX':>22s} {'XAUUSD':>22s} {'EURUSD':>22s} {'POOLED':>22s}")
    for wlabel, cutoff in WINDOWS:
        cells = {}; pooled_rets = []; pooled_ctrl = []; pooled_pools = []
        for a in ASSETS:
            D = DS[a]
            wmask = np.ones(D["n"], bool) if cutoff is None else (DATES[a] >= cutoff)
            r = eval_window(D, key, direction, wmask)
            if r is None or r.get("insufficient"):
                cells[a] = f"n={0 if r is None else r['n']}(thin)"
            else:
                cells[a] = f"{r['edge']*100:+.2f}({r['ctrl']*100:+.2f})p{r['p']:.2f}n{r['n']}"
            bkt = windowed_buckets(D, wmask)
            if bkt is not None:
                dr,_,_,_ = dir_arrays(D, direction, H)
                idx = base_events(D, key); idx = idx[wmask[idx] & D["valid_h"][H][idx]]; idx = decluster(idx, H)
                idx = idx[~np.isnan(dr[idx])]
                for i in idx:
                    bb = bkt[i]
                    m = D["valid_h"][H] & wmask & (bkt == bb) & ~np.isnan(dr)
                    if m.sum() and bb >= 0:
                        pooled_rets.append(dr[i]); pooled_ctrl.append(dr[m].mean()); pooled_pools.append(dr[m])
        if pooled_rets:
            pr = np.array(pooled_rets); pc = np.array(pooled_ctrl); edge = pr.mean() - pc.mean()
            samp = np.empty((len(pr), rng_B))
            for i, p_ in enumerate(pooled_pools):
                samp[i] = p_[rng.integers(0, len(p_), rng_B)]
            pp = (np.abs(samp.mean(axis=0) - pc.mean()) >= abs(edge)).mean()
            cells["POOLED"] = f"{edge*100:+.2f}({pc.mean()*100:+.2f})p{pp:.2f}n{len(pr)}"
        else:
            cells["POOLED"] = "-"
        print(f"  {wlabel:6s} {cells['BTC']:>22s} {cells['SPX']:>22s} {cells['XAUUSD']:>22s} {cells['EURUSD']:>22s} {cells['POOLED']:>22s}")
    print()
