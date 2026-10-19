"""The reader's objection, tested: an indicator traded as a HOLD-BETWEEN-SIGNALS position
system, not a fixed 10-day window.

Two systems:
  - GOLDEN/DEATH: long while SMA50 > SMA200, exit at the death cross.
  - RSI-50:       long while RSI(14) > 50, exit when it drops back under 50.
    (The 50 line is sold as "which side of the trend you're on" — the RSI analog of the cross.)

Each compared to:
  (a) buy & hold over the same window (what "makes way more money" is judged against),
  (b) a matched RANDOM-TIMING control: the same long stretches (same count, same lengths)
      placed at random points in the same history — identical time-in-market and segment
      structure, only the TIMING randomized. If the real signal doesn't beat random placement,
      the timing added nothing; the money is the trend's.

Close-to-close, entry/exit at the close of the signal bar, no look-ahead, no costs (favours the
system). Long/flat is primary; long/short (short the 'off' periods) also reported.
"""
import os, csv, datetime as dt, numpy as np
from ma_lib import sma

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
ASSETS = ["BTC", "SPX", "XAUUSD", "EURUSD"]
rng = np.random.default_rng(20261019)
NSIM = 5000


def rsi_wilder(close, length=14):
    close = np.asarray(close, float); n = len(close); rsi = np.full(n, np.nan)
    if n < length + 1:
        return rsi
    delta = np.diff(close)
    gain = np.where(delta > 0, delta, 0.0); loss = np.where(delta < 0, -delta, 0.0)
    ag = gain[:length].mean(); al = loss[:length].mean()
    def _r(ag, al):
        return 100.0 if al == 0 else 100.0 - 100.0 / (1.0 + ag / al)
    rsi[length] = _r(ag, al)
    for i in range(length + 1, n):
        ag = (ag * (length - 1) + gain[i - 1]) / length
        al = (al * (length - 1) + loss[i - 1]) / length
        rsi[i] = _r(ag, al)
    return rsi


def load(a):
    dates, c = [], []
    for r in csv.DictReader(open(os.path.join(DATA, f"{a}.csv"))):
        dates.append(r["date"]); c.append(float(r["close"]))
    return dates, np.array(c)


def maxdd(equity):
    peak = np.maximum.accumulate(equity)
    return (equity / peak - 1.0).min()


def runlengths(expo):
    runs = []; s = expo[0]; n = 1
    for x in expo[1:]:
        if x == s:
            n += 1
        else:
            runs.append((s, n)); s = x; n = 1
    runs.append((s, n)); return runs


def analyze_system(dates, c, expo, valid):
    ret = np.concatenate([[0.0], c[1:] / c[:-1] - 1.0])
    i0 = int(np.argmax(valid))
    e = expo[i0:].astype(float); e[np.isnan(c[i0:])] = 0.0
    r = ret[i0:]
    bh = np.prod(1.0 + r[1:]) - 1.0
    bh_dd = maxdd(np.cumprod(1.0 + r[1:]))
    e_lag = np.concatenate([[0.0], e[:-1]])
    sys_r = e_lag[1:] * r[1:]
    sys_tot = np.prod(1.0 + sys_r) - 1.0
    sys_dd = maxdd(np.cumprod(1.0 + sys_r))
    inmkt = e_lag[1:].mean()
    n_rt = int(((e[1:] == 1) & (e[:-1] == 0)).sum())
    pos = np.where(e > 0, 1.0, -1.0); pos_lag = np.concatenate([[0.0], pos[:-1]])
    ls_tot = np.prod(1.0 + pos_lag[1:] * r[1:]) - 1.0
    # random-timing control
    runs = runlengths(e.astype(int))
    long_lens = [n for st, n in runs if st == 1]
    flat_lens = [n for st, n in runs if st == 0]
    start_state = runs[0][0]
    sims = np.empty(NSIM)
    for k in range(NSIM):
        ll = rng.permutation(long_lens).tolist() if long_lens else []
        fl = rng.permutation(flat_lens).tolist() if flat_lens else []
        path = np.empty(len(e)); idx = 0; st = start_state; li = fi = 0
        while idx < len(e):
            if st == 1 and li < len(ll):
                L = ll[li]; li += 1; path[idx:idx + L] = 1.0
            elif st == 0 and fi < len(fl):
                L = fl[fi]; fi += 1; path[idx:idx + L] = 0.0
            else:
                path[idx:] = st; break
            idx += L; st = 1 - st
        path = path[:len(e)]
        pl = np.concatenate([[0.0], path[:-1]])
        sims[k] = np.prod(1.0 + pl[1:] * r[1:]) - 1.0
    return dict(bh=bh, bh_dd=bh_dd, sys=sys_tot, sys_dd=sys_dd, inmkt=inmkt, n_rt=n_rt,
                ls=ls_tot, rand_med=np.median(sims), pctile=(sims <= sys_tot).mean() * 100)


def run(name, expo_fn):
    print(f"\n===== {name} — hold-between-signals position system (close-to-close, no costs) =====")
    print(f"{'asset':7s} {'B&H tot':>13s} {'B&H maxDD':>9s} | {'SYS tot':>13s} {'SYS maxDD':>9s} {'%inMkt':>7s} {'#entries':>8s} "
          f"{'L/S tot':>13s} | {'rand med':>13s} {'beat rand':>9s}")
    for a in ASSETS:
        dates, c = load(a)
        expo, valid = expo_fn(c)
        r = analyze_system(dates, c, expo, valid)
        print(f"{a:7s} {r['bh']*100:12.0f}% {r['bh_dd']*100:8.0f}% | {r['sys']*100:12.0f}% {r['sys_dd']*100:8.0f}% "
              f"{r['inmkt']*100:6.0f}% {r['n_rt']:8d} {r['ls']*100:12.0f}% | {r['rand_med']*100:12.0f}% {r['pctile']:7.0f}%")


def expo_cross(c):
    s50 = sma(c, 50); s200 = sma(c, 200)
    valid = ~np.isnan(s200)
    e = (s50 > s200).astype(float); e[~valid] = 0.0
    return e, valid


def expo_rsi50(c):
    rsi = rsi_wilder(c, 14)
    valid = ~np.isnan(rsi)
    e = (rsi > 50).astype(float); e[~valid] = 0.0
    return e, valid


if __name__ == "__main__":
    print(f"Random-timing control = {NSIM} sims, same long segments/lengths, random placement.")
    run("GOLDEN/DEATH CROSS (SMA 50/200)", expo_cross)
    run("RSI-50 regime (long while RSI>50)", expo_rsi50)
    print("\nbeat rand = percentile of the ACTUAL system within the random-timing distribution.")
    print("~50% => the signal's timing added nothing beyond being long that fraction of the time.")
    print("B&H maxDD vs SYS maxDD = the one real benefit of the timing rule: smaller drawdown, not more return.")
