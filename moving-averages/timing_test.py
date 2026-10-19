"""Did the signal pick the WHEN? (the reader's second objection)

"The cross told me when to buy; a random buy / buy-and-hold could have been earlier or later."
Correct — so judge the signal's ENTRY TIMING against the DISTRIBUTION of alternative timings,
holding the SAME duration each time (the actual golden->death / RSI>50 segment length L).

For every real long segment (enter at close of the signal bar, hold L bars until the opposite
signal), compare its return to buying and holding L bars starting at:
  (A) a random day ANYWHERE in the history  -> "could have bought any other time"
  (B) a random day in the SAME 200d-regime AND volatility tercile -> "same kind of market"
Pool across segments; bootstrap p on the difference (signal mean - control mean).

(A) still lets the signal look good just by being in uptrends (regime selection = trend).
(B) removes that, isolating whether the PRECISE timing carried anything.

Plus a placebo: shift every entry/exit by k bars and recompute the whole system's compounded
return. If +/-k barely moves it, the exact signal day was never the point.

Close-to-close, no look-ahead, no costs. Reuses the same data and the verified indicator libs.
"""
import os, csv, numpy as np
from ma_lib import sma, atr_wilder
from cross_system import rsi_wilder

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
ASSETS = ["BTC", "SPX", "XAUUSD", "EURUSD"]
rng = np.random.default_rng(20261019)
B = 5000


def load(a):
    c, h, l = [], [], []
    for r in csv.DictReader(open(os.path.join(DATA, f"{a}.csv"))):
        c.append(float(r["close"])); h.append(float(r["high"])); l.append(float(r["low"]))
    return np.array(c), np.array(h), np.array(l)


def long_segments(expo):
    """(start_index, length) for each maximal run of exposure==1."""
    segs = []; n = len(expo); i = 0
    while i < n:
        if expo[i] == 1:
            j = i
            while j < n and expo[j] == 1:
                j += 1
            segs.append((i, j - i)); i = j
        else:
            i += 1
    return segs


def build(a):
    c, hi, lo = load(a)
    n = len(c)
    s50 = sma(c, 50); s200 = sma(c, 200); rsi = rsi_wilder(c, 14)
    atr = atr_wilder(hi, lo, c, 14); atrpct = atr / c
    valid = ~np.isnan(s200) & ~np.isnan(atr) & (atr > 0)
    vv = atrpct[valid]; q1, q2 = np.nanquantile(vv, [1/3, 2/3])
    vb = np.full(n, -1)
    vb[valid & (atrpct <= q1)] = 0
    vb[valid & (atrpct > q1) & (atrpct <= q2)] = 1
    vb[valid & (atrpct > q2)] = 2
    regime = np.where(c > s200, 1, 0)
    bucket = np.where(valid, regime * 3 + vb, -1)
    return dict(c=c, n=n, s50=s50, s200=s200, rsi=rsi, valid=valid, bucket=bucket, regime=regime)


def timing_edge(D, expo, matched):
    """Return (signal_mean, ctrl_mean, edge, p, nseg) for same-duration entry timing.
    matched=True -> control days share the segment-start 200d-regime+vol bucket; else any day."""
    c = D["c"]; n = D["n"]; valid = D["valid"]; bucket = D["bucket"]
    segs = [(s, L) for (s, L) in long_segments(expo) if valid[s] and s + L < n]
    if not segs:
        return None
    sig = np.array([c[s + L] / c[s] - 1.0 for s, L in segs])
    if matched:
        pools = {b: np.where(valid & (bucket == b))[0] for b in range(6)}
    else:
        allv = np.where(valid)[0]
    ctrl_means = np.empty(len(segs)); samp = np.empty((len(segs), B))
    for i, (s, L) in enumerate(segs):
        if matched:
            pool = pools[bucket[s]]
        else:
            pool = allv
        pool = pool[pool + L < n]
        if len(pool) == 0:
            ctrl_means[i] = np.nan; samp[i] = np.nan; continue
        pr = c[pool + L] / c[pool] - 1.0
        ctrl_means[i] = pr.mean()
        samp[i] = pr[rng.integers(0, len(pr), B)]
    ok = ~np.isnan(ctrl_means)
    sig_m = sig[ok].mean(); ctrl_m = ctrl_means[ok].mean(); edge = sig_m - ctrl_m
    null = samp[ok].mean(axis=0)
    p = (np.abs(null - ctrl_m) >= abs(edge)).mean()
    return sig_m, ctrl_m, edge, p, int(ok.sum())


def shift_system(D, expo, k):
    """Whole-system compounded return with every entry/exit shifted by k bars."""
    c = D["c"]; ret = np.concatenate([[0.0], c[1:] / c[:-1] - 1.0])
    e = expo.astype(float).copy()
    if k > 0:
        e = np.concatenate([np.zeros(k), e[:-k]])
    elif k < 0:
        e = np.concatenate([e[-k:], np.zeros(-k)])
    e_lag = np.concatenate([[0.0], e[:-1]])
    return np.prod(1.0 + e_lag[1:] * ret[1:]) - 1.0


def expo_cross(D):
    e = (D["s50"] > D["s200"]).astype(float); e[np.isnan(D["s200"])] = 0.0; return e


def expo_rsi(D):
    e = (D["rsi"] > 50).astype(float); e[np.isnan(D["rsi"])] = 0.0; return e


SYS = [("GOLDEN/DEATH (SMA 50/200)", expo_cross), ("RSI-50 (RSI>50)", expo_rsi)]

for name, fn in SYS:
    print(f"\n===== {name}: did entering ON the signal beat a same-duration entry elsewhere? =====")
    print(f"{'asset':7s} | {'vs ANY-day random':>34s} | {'vs SAME regime+vol random':>40s}")
    print(f"{'':7s} | {'signal (ctrl)  edge   p   nseg':>34s} | {'signal (ctrl)  edge   p':>40s}")
    for a in ASSETS:
        D = build(a); e = fn(D)
        rA = timing_edge(D, e, matched=False)
        rB = timing_edge(D, e, matched=True)
        sA = f"{rA[0]*100:+.1f}% ({rA[1]*100:+.1f}%) {rA[2]*100:+.1f} p{rA[3]:.2f} n{rA[4]}"
        sB = f"{rB[0]*100:+.1f}% ({rB[1]*100:+.1f}%) {rB[2]*100:+.1f} p{rB[3]:.2f}"
        print(f"{a:7s} | {sA:>34s} | {sB:>40s}")

print("\n===== Placebo: shift every entry/exit by k bars; whole-system compounded return =====")
for name, fn in SYS:
    print(f"\n{name}:")
    print(f"{'asset':7s} " + " ".join(f"{'k='+str(k):>11s}" for k in [-20,-10,-5,0,5,10,20]))
    for a in ASSETS:
        D = build(a); e = fn(D)
        vals = [shift_system(D, e, k) for k in [-20,-10,-5,0,5,10,20]]
        print(f"{a:7s} " + " ".join(f"{v*100:10.0f}%" for v in vals))
print("\nIf the k=0 column is not special vs its neighbours, the exact signal day carried no timing info.")
