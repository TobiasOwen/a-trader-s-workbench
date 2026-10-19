---
type: summary
project: graveyard-article-02-MA
dated: 2026-10-19
primary_horizon: 10 daily bars
status: results-final
---

# Moving-average teardown — plain-language summary (article-ready)

**Hand this to the article draft. Every number here is produced by `analyze.py` from
`results.json` (and `independent_control.py` / `absolute.py` / `recency.py`); nothing is
invented. Full tables in `results.md`, design in `00-preregistration.md`.**

## What was tested (one paragraph)

Textbook moving averages — simple (SMA) and exponential (EMA, α = 2/(n+1) seeded with the
SMA), verified against an independent implementation and a hand-worked example before any
signal was run. Four markets, as much history as the source gives (same CSVs as the RSI test):
**BTC** (2014–2026), **S&P 500** (1970–2026), **Gold** (COMEX, 2000–2026), **EUR/USD**
(2003–2026). Signals tested: price above/below the SMA50 and SMA200 (the "I'm long while
price is over the line" state); price crossing those MAs; the **MA-on-MA crosses** — the
golden/death cross (50/200), plus 20/50, 9/21 and 12/26, each in **both SMA and EMA**; and
the **"moving average as support"** claim (a pullback that touches and holds the rising MA in
an uptrend). Each signal is compared not to zero but to a **matched random entry on the same
market** — same trend regime (above/below the 200-day average) and same volatility bucket,
same holding period. The edge is what's left of the signal after you subtract a coin-flip
entry made in the same conditions. Primary horizon: **10 trading days** (5 and 20 also
computed). Entries at the close the signal prints; forming bar dropped; no look-ahead.
"Effective n" counts **distinct de-clustered episodes**, not raw signal bars.

## The headline

**Not one moving-average signal beats a volatility-and-trend-matched random entry — in any
of the four markets, at any horizon.** The famous **golden cross** (SMA 50/200) comes out at
**+1.02% (+0.77%), edge +0.24%, p 0.68** pooled, and is a null in every single market
*including Bitcoin* (BTC +3.11% vs a matched +3.03% — edge **+0.08%, p 0.98**). This is a
**cleaner kill than RSI**: RSI at least had a BTC-only momentum standout; moving averages have
**no standout anywhere**. Across all 780 computed cells only 15 reach raw p < 0.05 — **fewer
than the ~39 you'd expect by chance** — and **nothing survives a multiple-testing correction**
(Benjamini–Hochberg or Bonferroni) at the pooled level. A moving average is the most literal
possible restatement of "price has been trending," and the test shows exactly that: strip out
the trend it was sitting in, and there is nothing left.

**Circularity, handled (pre-registered §5a).** The matched control already conditions on the
200-day trend, so "price above the SMA200" is a near-tautology — its up-days *are* the up-regime,
so the edge is ~0 by construction (**−0.05%, p 0.66**). That's not a bug; it's the thesis in its
purest form — the MA state literally *is* the trend label. To make sure the control wasn't
secretly manufacturing the null, every regime-coincident signal (price-vs-SMA200, golden/death
cross, price-cross-SMA200) was **re-run against a trend reference independent of every tested
MA** (the sign of the 120-day price change). The edges barely move — golden cross **+0.34%,
p 0.58**; price>SMA200 **−0.04%, p 0.73** — so the null is **real**, not an artifact.

## Signal by signal (primary horizon = 10 bars, shown `signal (control)`, edge, effective n)

### 1. Price vs the SMA200 (state) — "I'm long while price is above the 200-day"
- Pooled: **+0.63% (+0.68%), edge −0.05%**, p 0.66, n 2,167. *(⚠ near-tautology — see above.)*
- **Takeaway:** being above the 200-day pays what being in an uptrend pays — because it *is*
  the definition of an uptrend. The moving average adds no information to the regime it draws.

### 2. Price vs the SMA50 (state) — "long while above the 50-day"
- Pooled: **+0.61% (+0.60%), edge +0.01%**, p 0.90, n 2,131.
- Per market: BTC +2.81% (+2.26%) +0.55% p0.42 · SPX +0.34% (+0.38%) −0.04% p0.65 · Gold +0.38% (+0.51%) −0.13% p0.42 · EUR/USD −0.03% (+0.03%) −0.06% p0.48.
- **Takeaway:** a faster version of the same thing — a slightly quicker trend label, zero edge
  over a matched random long. Even in BTC the "+0.55%" is noise (p 0.42).

### 3. The golden cross (SMA 50/200 → long) — the headline claim
- Pooled: **+1.02% (+0.77%), edge +0.24%**, p 0.68, n 70. Null in **every** market: BTC +0.08% p0.98 · SPX +0.48% p0.39 · Gold −0.29% p0.74 · EUR/USD +0.44% p0.28.
- Holds under the independent-reference control (+0.34%, p0.58) and across horizons (edge +0.2–0.4%, never significant).
- **Takeaway:** the most famous signal in technical analysis. It fires in uptrends, so it
  "makes money" in rising markets — but a coin-flip entry in the same uptrend makes the same.
  The golden cross is a lagging restatement of the 200-day trend; it tells you nothing the
  trend didn't already.

### 4. The death cross (SMA 50/200 → short)
- Pooled: **−0.42% (−0.45%), edge +0.04%**, p 0.95, n 69. Null everywhere; in BTC the short
  actually makes a small profit because it keeps getting triggered mid-bull and stopping out flat.
- **Takeaway:** shorting the death cross is a wash against a matched random short, and loses
  money outright anywhere the market's base drift is up (see absolute P&L below).

### 5. Faster MA–MA crosses — 20/50, 9/21, 12/26 (SMA & EMA, both directions)
- All pooled nulls: 20/50 up +0.26% p0.32 (SMA) / −0.08% p0.78 (EMA); 9/21 up −0.13% p0.45 /
  −0.09% p0.66; 12/26 up +0.03% p0.87 / +0.06% p0.78. Every per-market cell null too.
- The only family member with raw p<0.05 anywhere is the SMA 9/21 **down**-cross short
  (+0.36%, p 0.04) — a short-side mirror that means the short *loses slightly less* than a
  matched short, not an edge; it dies under correction and isn't in the entry family.
- **Takeaway:** speeding the cross up just adds whipsaw. More trades, same zero edge.

### 6. SMA vs EMA — is the "faster" average better?
- Head-to-head on the same windows (pooled edge, primary horizon): 50/200 +0.24% SMA vs −0.05%
  EMA; 20/50 +0.26% vs −0.08%; 9/21 −0.13% vs −0.09%; 12/26 +0.03% vs +0.06%. **No consistent
  difference, both null.**
- **Takeaway:** the EMA is a faster SMA, not new information. Choosing one over the other is
  choosing a flavour of the same zero.

### 7. "The moving average as support" — the loudest claim, tested directly
- A pullback that touches within ½ an ATR of the rising SMA50 and closes back above it, in an
  uptrend. Pooled: **+0.40% (+0.61%), edge −0.22%**, p 0.19, n 815 — i.e. the bounce does
  *slightly worse* than a random long in the same uptrend.
- Per market: BTC +1.65% (+2.91%) **−1.26%** p0.37 · SPX +0.44% (+0.41%) +0.03% p0.82 · Gold
  +0.20% (+0.49%) −0.29% p0.25 · EUR/USD −0.20% (+0.08%) **−0.27% p0.04**. SMA200 support same
  story (edge −0.30%, p0.18, n416).
- **Takeaway:** "the MA held as support" is the single most-repeated chart claim, and it is a
  null-to-negative: touching the 50 and bouncing is no better — fractionally worse — than
  buying any random day in the same uptrend. The MA isn't support; the uptrend is.

## Vol-normalized "shape" (for the run-to-target visual)

In R-multiples (R = the day's ATR), the signal's path looks like the control's path. Golden
cross pooled reaches +1R before −1R **60% (control 54%)** with MFE **2.30R (2.06R)** — a hair
better and well inside the per-market scatter (BTC golden *under*performs: hit 36% vs 55%).
The above-SMA50 state is **54% (53%)**, MFE **1.99R (1.98R)** — indistinguishable. Support at
the SMA50 is **52% (53%)**, MFE **1.85R (1.97R)** — the bounce travels *less* far up than a
random entry. Nothing here separates the signal's trajectory from a matched coin flip's.

## "OK, it didn't beat random — but did it MAKE MONEY?" (absolute P&L)

The fair reader's question. Short answer: **the long signals made money the same way *holding*
made money — because the markets went up — and a coin-flip entry in the same spots made about
the same. The short (death-cross) signals lost money outright wherever a market trended. And in
the one market with no built-in uptrend (EUR/USD), the profit vanishes.** Same verdict as RSI,
reached through a different indicator.

**Buy & hold over each window, for scale:** SPX **+8,998%** (CAGR 8.4%/yr, 56y) · BTC
**+32,014%** (CAGR 64.9%, 11.5y) · Gold **+1,435%** (11.4%/yr) · EUR/USD **−6.7%** (−0.3%/yr).

| signal | market | avg/trade | %win | random avg/trade | took every trade, compounded |
|---|---|---|---|---|---|
| golden cross (long) | SPX | +0.90% | 68% | +0.42% | +27.5% over 28 trades |
| golden cross | BTC | +3.11% | 73% | +3.03% (≈identical) | +33.2% over 11 |
| golden cross | Gold | +0.28% | 60% | +0.57% (worse) | +4.1% over 15 |
| golden cross | EUR/USD | +0.47% | 69% | +0.03% | +7.6% over 16 |
| above-SMA50 (long) | SPX | +0.34% | 60% | +0.39% (≈identical) | +2,562% over 1,058 |
| above-SMA50 | BTC | +2.81% | 57% | +2.26% | +42,586% over 278 |
| above-SMA50 | EUR/USD | −0.03% | 49% | +0.03% | **−16.0%** |
| SMA 9/21 up (long) | SPX | +0.14% | 56% | +0.38% (worse) | +33.3% over 355 |
| SMA 9/21 up | EUR/USD | +0.00% | 53% | −0.00% | **−1.4%** |
| support-at-SMA50 (long) | SPX | +0.44% | 59% | +0.41% (≈identical) | +456% over 421 |
| support-at-SMA50 | EUR/USD | −0.20% | 46% | +0.08% | **−25.0%** |
| **death cross (short)** | SPX | −0.54% | 41% | −0.30% | **−15.8%** over 27 |
| death cross (short) | Gold | −1.43% | 44% | −0.51% | **−21.3%** over 16 |

**What this says, plainly.** (1) Long MA signals in a rising market "make money" — but so does
anything long: on SPX the golden cross makes +0.90%/trade over just 28 trades while buy-and-hold
made **+8,998%** doing nothing. (2) The win rates (56–73%) look like skill until you see the
matched random entry wins at nearly the same rate and avg/trade. (3) Strip the uptrend out
(EUR/USD) and every long MA signal bleeds: above-SMA50 −16%, 9/21 −1.4%, support −25%. (4) The
death-cross short loses money anywhere the market's drift is up. The money the moving average
"makes" is the trend's money.

## Recency check (last 10y / 5y) — `recency.py`

Does the conclusion hold in the era people actually trade, not back to 1970? Vol terciles
recomputed within each window so the control stays fair. Primary horizon 10, pooled edge vs
matched control:
- **Golden cross:** full +0.24 (p0.68) → 10y **−0.60** (p0.65) → 5y +0.36 (p0.77) — flat/negative,
  never an edge; slow-cross samples go thin (n 15–27) and are flagged.
- **Above-SMA50 state:** null in every window and market (pooled 5y +0.03, p0.92).
- **SMA/EMA 9/21 up:** null in every window (pooled 5y +0.32/+0.46, p≈0.4–0.5).
- **Support at SMA50:** stays null-to-negative in every window (pooled 10y −0.57, 5y −0.25).
- **Takeaway for the article:** the nulls are not a pre-2000 artifact — the last five and ten
  years say the same thing. Nothing a moving average does has started working.

## One-line verdict (for the article's voice)

> In my testing, on these four markets at the daily timeframe, every moving-average signal —
> price over the line, the golden and death crosses, the faster EMA crosses, even "the average
> held as support" — comes out even with a coin-flip entry made in the same trend and the same
> volatility. Not one of them beats it, in any market, at any horizon. A moving average is the
> most honest indicator there is: it doesn't pretend to be anything but the trend, and when you
> subtract the trend, there's nothing underneath. No edge over a fair comparison.

## Honesty / limitations

- **Slow crosses are low-n by nature:** the golden/death cross fires ~11–28 times per market
  over decades, so a true small edge could hide in that noise. Reported with honest effective n;
  the point is that nothing even *trends* toward significance, and the fast crosses (n 270–770)
  — which would reveal a real MA effect if one existed — are equally null.
- **BTC is one regime** (a 12-year secular bull); its long-signal profits are that bull trend,
  not the MA — and unlike RSI, even BTC shows no matched-control edge here.
- Gold = COMEX futures (GC=F) standing in for XAU spot; EUR/USD has one immaterial 18-day Yahoo
  gap in Aug 2008. Same data as the RSI test.
- The "support" test uses one pre-registered touch definition (low within ½·ATR of the MA,
  close back above). A looser or tighter band would change n but the matched-control framing is
  the same; reported as pre-registered, not tuned.
- Everything compared to a **matched** control (same asset, regime, vol), the deliberately
  hardest bar: the edge is the moving average's marginal contribution, not raw performance. The
  circularity between the SMA200 signal and the 200d-regime control is handled explicitly and
  cross-checked with an independent trend reference (`independent_control.py`).
