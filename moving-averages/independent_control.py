"""Circularity robustness (pre-registration §5a, option a).

The primary matched control conditions on the 200d-SMA regime. Three tested signals ARE
that regime or a close proxy: price>SMA200 (state), the golden/death cross (SMA 50/200),
and price-cross-SMA200. For those, re-run the matched control with a trend reference that
is INDEPENDENT of every tested MA: regime = sign of the 120-day price change
(close[t]/close[t-120] - 1). Vol tercile unchanged. If the edge is still ~0 under this
independent reference, the null is real, not an artifact of the control absorbing the signal.
Primary horizon 10, naive layer, per asset + pooled.
"""
import numpy as np
from analyze import build, base_events, decluster, dir_arrays, ASSETS

H = 10
LOOKBACK = 120
B = 10000
rng = np.random.default_rng(424242)
DS = {a: build(a) for a in ASSETS}

# signals coincident with the 200d regime reference
TARGETS = [
    ("state_sma200_long",  "st_sma200_up", "long"),
    ("golden_sma_50_200",  "sma_50_200_u", "long"),
    ("death_sma_50_200",   "sma_50_200_d", "short"),
    ("pxcross_sma200_long","pxu_sma200",   "long"),
    ("pxcross_sma200_short","pxd_sma200",  "short"),
]


def indep_bucket(D):
    """regime from 120d momentum (independent of any tested MA) x vol tercile."""
    cl = D["cl"]; n = D["n"]; iv = D["ind_valid"]
    mom = np.full(n, np.nan)
    mom[LOOKBACK:] = cl[LOOKBACK:] / cl[:-LOOKBACK] - 1.0
    reg = np.where(mom > 0, 1, 0)
    valid = iv & ~np.isnan(mom)
    bkt = np.where(valid, reg * 3 + D["volbucket"], -1)
    return bkt, valid


def eval_indep(D, key, direction):
    bkt, valid = indep_bucket(D)
    dr, _, _, _ = dir_arrays(D, direction, H)
    vh = D["valid_h"][H]
    pools = {}
    for b in range(6):
        m = vh & valid & (bkt == b) & ~np.isnan(dr)
        pools[b] = dr[m]
    idx = base_events(D, key)
    idx = idx[vh[idx] & valid[idx]]
    idx = decluster(idx, H)
    idx = idx[~np.isnan(dr[idx])]
    if len(idx) == 0:
        return None
    b = bkt[idx]
    if np.any(b < 0) or any(len(pools[bb]) == 0 for bb in b):
        return None
    rets = dr[idx]
    ctrl = np.mean([pools[bb].mean() for bb in b])
    edge = rets.mean() - ctrl
    samp = np.empty((len(idx), B))
    for i, bb in enumerate(b):
        samp[i] = pools[bb][rng.integers(0, len(pools[bb]), B)]
    p = (np.abs(samp.mean(axis=0) - ctrl) >= abs(edge)).mean()
    return dict(n=len(idx), sig=rets.mean(), ctrl=ctrl, edge=edge, p=p, pools=pools, idx=idx, b=b, dr=dr)


print(f"Independent-reference control: regime = sign of {LOOKBACK}-day price change (NOT any tested MA).")
print(f"Primary horizon {H}, naive. Compare edge here vs the primary (200d-SMA) control.\n")
print(f"{'signal':22s} {'scope':8s} {'edge(indep)':>12s} {'p':>6s} {'n':>5s}")
for name, key, direction in TARGETS:
    pooled_rets=[]; pooled_ctrl=[]; pooled_pools=[]
    for a in ASSETS:
        r = eval_indep(DS[a], key, direction)
        if r is None:
            print(f"{name:22s} {a:8s} {'(thin)':>12s}")
            continue
        print(f"{name:22s} {a:8s} {r['edge']*100:+11.2f}% {r['p']:6.2f} {r['n']:5d}")
        for i, bb in enumerate(r["b"]):
            pooled_rets.append(r["dr"][r["idx"][i]]); pooled_ctrl.append(r["pools"][bb].mean()); pooled_pools.append(r["pools"][bb])
    if pooled_rets:
        pr=np.array(pooled_rets); pc=np.array(pooled_ctrl); edge=pr.mean()-pc.mean()
        samp=np.empty((len(pr),B))
        for i,p_ in enumerate(pooled_pools):
            samp[i]=p_[rng.integers(0,len(p_),B)]
        pp=(np.abs(samp.mean(axis=0)-pc.mean())>=abs(edge)).mean()
        print(f"{name:22s} {'POOLED':8s} {edge*100:+11.2f}% {pp:6.2f} {len(pr):5d}")
    print()
