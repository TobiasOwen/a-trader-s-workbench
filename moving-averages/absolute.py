"""Absolute P&L view: forget the matched control for a moment -- if someone just TOOK
these MA trades, did they make money? Compare to (a) a matched random entry in the same
spots and (b) buy-and-hold over the same window. Non-overlapping de-clustered episodes,
primary horizon 10 bars, trade taken in the signal's actual direction (short = short)."""
import numpy as np, datetime as dt
from analyze import build, base_events, decluster, dir_arrays, bucket_pools, ASSETS, SIGNALS
H = 10
DS = {a: build(a) for a in ASSETS}

def buyhold(D):
    v = D["ind_valid"]; i0 = np.argmax(v); c = D["cl"]
    tot = c[-1]/c[i0]-1
    yrs = (dt.date.fromisoformat(D["dates"][-1]) - dt.date.fromisoformat(D["dates"][i0])).days/365.25
    cagr = (1+tot)**(1/yrs)-1
    return tot, cagr, yrs

SIGS = {s[0]: s for s in SIGNALS}
WATCH = ["golden_sma_50_200","death_sma_50_200","state_sma50_long","sma_9_21_up",
         "ema_9_21_up","support_sma50"]

print(f"Horizon = {H} bars, trades taken in the signal's own direction, non-overlapping episodes.\n")
print("buy & hold over each asset's window:")
for a in ASSETS:
    tot,cagr,yrs = buyhold(DS[a])
    print(f"  {a:7s} total {tot*100:+10.1f}%  over {yrs:4.1f}y  (CAGR {cagr*100:+6.1f}%/yr)")
print()

for name in WATCH:
    sig = SIGS[name]; _,key,direction,desc = sig
    print(f"### {name}  [{direction}]  {desc}")
    print(f"{'scope':8s} {'trades':>6s} {'avg/trade':>10s} {'%win':>5s} {'compounded(seq)':>16s} {'random avg/trade':>17s}")
    for a in ASSETS:
        D = DS[a]
        idx = base_events(D, key)
        vh = D["valid_h"][H]
        idx = idx[np.isin(idx, np.where(vh)[0])]
        idx = decluster(idx, H)
        dr,_,_,_ = dir_arrays(D, direction, H)
        good = ~np.isnan(dr[idx]); idx = idx[good]
        if len(idx)==0:
            print(f"  {a:6s} (none)"); continue
        rets = dr[idx]; comp = np.prod(1+rets)-1
        pools = bucket_pools(D, direction, H); bkt = D["bucket"][idx]
        rand_avg = np.nanmean([pools[b].mean() for b in bkt])
        print(f"  {a:6s} {len(idx):6d} {rets.mean()*100:9.3f}% {(rets>0).mean()*100:4.0f}% "
              f"{comp*100:15.1f}% {rand_avg*100:16.3f}%")
    print()
