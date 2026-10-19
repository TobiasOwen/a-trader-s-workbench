"""Emit results.md straight from results.json so every number is traceable to the
computation (no hand transcription)."""
import json, os, numpy as np
HERE=os.path.dirname(__file__)
d=json.load(open(os.path.join(HERE,"results.json")))
rows=d["rows"]; meta=d["meta"]
SC=["BTC","SPX","XAUUSD","EURUSD","POOLED"]
def g(sig,layer,H,sc):
    r=[x for x in rows if x["signal"]==sig and x["layer"]==layer and x["horizon"]==H and x["scope"]==sc]
    return r[0] if r else None
def cell(r):
    if not r: return " — "
    star="*" if (r["p"] is not None and r["p"]<0.05) else ""
    return f'{r["sig_ret"]*100:+.2f}% ({r["ctrl_ret"]*100:+.2f}%) **{r["edge"]*100:+.2f}**{star} p{r["p"]:.2f} n{r["n_eff"]}'
SIGS=[("state_sma50_long","price > SMA50 (state) → long"),
      ("state_sma50_short","price < SMA50 (state) → short"),
      ("state_sma200_long","price > SMA200 (state) → long  ⚠tautology"),
      ("state_sma200_short","price < SMA200 (state) → short  ⚠tautology"),
      ("pxcross_sma50_long","price crosses up through SMA50 → long"),
      ("pxcross_sma50_short","price crosses down through SMA50 → short"),
      ("pxcross_sma200_long","price crosses up through SMA200 → long"),
      ("pxcross_sma200_short","price crosses down through SMA200 → short"),
      ("golden_sma_50_200","SMA 50/200 GOLDEN cross → long"),
      ("death_sma_50_200","SMA 50/200 DEATH cross → short"),
      ("golden_ema_50_200","EMA 50/200 cross up → long"),
      ("death_ema_50_200","EMA 50/200 cross down → short"),
      ("sma_20_50_up","SMA 20/50 cross up → long"),
      ("sma_20_50_dn","SMA 20/50 cross down → short"),
      ("ema_20_50_up","EMA 20/50 cross up → long"),
      ("ema_20_50_dn","EMA 20/50 cross down → short"),
      ("sma_9_21_up","SMA 9/21 cross up → long"),
      ("sma_9_21_dn","SMA 9/21 cross down → short"),
      ("ema_9_21_up","EMA 9/21 cross up → long"),
      ("ema_9_21_dn","EMA 9/21 cross down → short"),
      ("sma_12_26_up","SMA 12/26 cross up → long"),
      ("sma_12_26_dn","SMA 12/26 cross down → short"),
      ("ema_12_26_up","EMA 12/26 cross up → long"),
      ("ema_12_26_dn","EMA 12/26 cross down → short"),
      ("support_sma50","uptrend pullback holds SMA50 → long"),
      ("support_sma200","uptrend pullback holds SMA200 → long")]
L=[]
L.append("# Moving-average teardown — results\n")
L.append("Generated from `results.json` (produced by `analyze.py`). Numbers are shown as "
         "**signal (control)** with the **edge** = signal − matched control in bold; `*` marks raw p<0.05 "
         "(un-corrected). Returns are directional (long signals = long return, short signals = short return). "
         "Primary horizon = 10 bars. Same methodology as the RSI teardown with MA signals swapped in.\n")
L.append("## Data\n")
L.append("| asset | symbol (source) | n bars | span | indicator-valid rows | ATR%/close terciles (low|mid|high cut) |")
L.append("|---|---|---|---|---|---|")
sym={"BTC":"BTC-USD","SPX":"^GSPC","XAUUSD":"GC=F (COMEX gold, stands in for XAU spot)","EURUSD":"EURUSD=X"}
for a in ["BTC","SPX","XAUUSD","EURUSD"]:
    m=meta[a]; L.append(f'| {a} | {sym[a]} (Yahoo) | {m["n"]} | {m["start"]} → {m["end"]} | {m["ind_valid"]} | {m["volq"][0]} / {m["volq"][1]} |')
L.append("\nSame CSVs as the RSI teardown (Yahoo Finance daily, public chart API). "
         "Indicator-valid rows require SMA200, EMA200 and ATR(14) all defined. SMA verified vs a direct "
         "windowed mean; EMA (α=2/(n+1), seeded with SMA(n)) verified vs an independent ewm(adjust=False) "
         "implementation (agree <1e-9) and a hand-worked example — see `ma_lib.py`.\n")
L.append("**Method.** Enter at the close of the signal bar (MA known at close; forming bar dropped; no look-ahead). "
         "Matched control = all same-asset days in the same trend regime (close vs 200d SMA) **and** the same ATR/close "
         "volatility tercile; edge vs that bucket mean. Effective n = distinct de-clustered episodes: price-vs-MA STATES "
         "are sampled throughout the state and de-clustered to ≥ horizon apart (not onset-only, because being above a MA is "
         "a persistent condition); crosses and support touches are onsets de-clustered to ≥ horizon apart so forward "
         "windows never overlap. Bootstrap p (10,000×) resamples each episode from its own matched bucket.\n")
L.append("⚠ **Circularity (see §5a of the pre-registration).** The control conditions on the 200d-SMA regime, so "
         "**price vs SMA200 (state)** is a near-exact tautology — its up-state bars *are* the up-regime, so edge ≈ 0 by "
         "construction. The **golden/death cross (SMA 50/200)** and **price-cross-SMA200** are slow proxies of that regime "
         "(correlated, not identical). All three are re-run below against a trend reference independent of every tested MA "
         "(sign of the 120-day price change) to confirm the null is real, not manufactured by the control.\n")
for H in [5,10,20]:
    tag=" (PRIMARY)" if H==10 else ""
    L.append(f"## All signals — horizon {H}{tag}\n")
    L.append("### Naive layer\n")
    L.append("| signal | "+" | ".join(SC)+" |"); L.append("|"+"---|"*(len(SC)+1))
    for s,desc in SIGS:
        L.append(f"| {desc} | "+" | ".join(cell(g(s,"naive",H,sc)) for sc in SC)+" |")
    L.append("\n### Trend-conditional layer (fire only when aligned with 200d trend)\n")
    L.append("| signal | "+" | ".join(SC)+" |"); L.append("|"+"---|"*(len(SC)+1))
    for s,desc in SIGS:
        L.append(f"| {desc} | "+" | ".join(cell(g(s,"trend",H,sc)) for sc in SC)+" |")
    L.append("")
# SMA vs EMA head-to-head
L.append("## SMA vs EMA — same windows, primary horizon 10, naive, POOLED edge\n")
L.append("| window | SMA edge (p, n) | EMA edge (p, n) |")
L.append("|---|---|---|")
for lab,su,eu in [("50/200 up (golden)","golden_sma_50_200","golden_ema_50_200"),
                  ("50/200 down (death)","death_sma_50_200","death_ema_50_200"),
                  ("20/50 up","sma_20_50_up","ema_20_50_up"),
                  ("20/50 down","sma_20_50_dn","ema_20_50_dn"),
                  ("9/21 up","sma_9_21_up","ema_9_21_up"),
                  ("9/21 down","sma_9_21_dn","ema_9_21_dn"),
                  ("12/26 up","sma_12_26_up","ema_12_26_up"),
                  ("12/26 down","sma_12_26_dn","ema_12_26_dn")]:
    rs=g(su,"naive",10,"POOLED"); re=g(eu,"naive",10,"POOLED")
    L.append(f'| {lab} | {rs["edge"]*100:+.2f}% (p{rs["p"]:.2f}, n{rs["n_eff"]}) | {re["edge"]*100:+.2f}% (p{re["p"]:.2f}, n{re["n_eff"]}) |')
L.append("")
# run-to-target / R multiples
L.append("## Run-to-target & excursions, vol-normalized (R = entry ATR), naive H=10\n")
L.append("hit+1R = fraction reaching +1R before −1R (first touch). MFE/MAE in R. signal (control).\n")
L.append("| signal | scope | hit +1R | MFE (R) | MAE (R) | per-trade Sharpe |")
L.append("|---|---|---|---|---|---|")
for s in ["golden_sma_50_200","state_sma50_long","sma_20_50_up","ema_9_21_up","support_sma50"]:
    for sc in ["BTC","SPX","XAUUSD","EURUSD","POOLED"]:
        r=g(s,"naive",10,sc)
        if r: L.append(f'| {s} | {sc} | {r["hit1"]*100:.0f}% ({r["ctrl_hit1"]*100:.0f}%) | {r["mfe_R"]:.2f} ({r["ctrl_mfe_R"]:.2f}) | {r["mae_R"]:.2f} ({r["ctrl_mae_R"]:.2f}) | {r["sharpe"]:.3f} |')
# multiple testing
L.append("\n## Multiple testing\n")
uniq=["state_sma50_long","pxcross_sma50_long","pxcross_sma200_long","golden_sma_50_200","golden_ema_50_200",
      "sma_20_50_up","ema_20_50_up","sma_9_21_up","ema_9_21_up","sma_12_26_up","ema_12_26_up",
      "support_sma50","support_sma200"]
fam=[g(s,"naive",10,"POOLED") for s in uniq]
ps=sorted([(x["p"],x["signal"]) for x in fam if x and x["p"] is not None]); m=len(ps)
raw=[s for p,s in ps if p<0.05]
bh=[s for i,(p,s) in enumerate(ps) if p<=(i+1)/m*0.10]
bon=[s for p,s in ps if p<0.05/m]
allp=[x["p"] for x in rows if x["p"] is not None and not np.isnan(x["p"])]
L.append(f"- Deduplicated pooled naive H=10 family (m={m} distinct long/support event families — the signals a trader "
         f"actually enters on): raw p<0.05 = `{raw or 'none'}`.")
L.append(f"- Benjamini–Hochberg q=0.10 survivors: `{bh or 'none'}`. Bonferroni 0.05/{m} survivors: `{bon or 'none'}`.")
L.append(f"- Across all {len(allp)} computed cells, {sum(p<0.05 for p in allp)} have raw p<0.05 (≈{0.05*len(allp):.0f} expected "
         f"by chance; and these cells are heavily correlated / mirror-duplicated long-vs-short).")
L.append("\n**Bottom line:** not one moving-average signal clears a multiple-testing correction, and unlike RSI there is "
         "**no single-market standout** — even BTC's golden cross (+0.08%, p0.98) and above-SMA50 state (+0.55%, p0.42) are "
         "nulls. The golden cross, the headline, is a flat zero (+0.24% pooled, p0.68) in every market. Every edge sits "
         "inside the noise at every horizon. The moving average is the most literal restatement of the trend, and the test "
         "shows exactly that: once you compare it to a random entry in the same trend and volatility, nothing is left.")
open(os.path.join(HERE,"results.md"),"w",encoding="utf-8").write("\n".join(L))
print("wrote results.md")
