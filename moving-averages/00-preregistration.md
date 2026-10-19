---
type: preregistration
project: graveyard-article-02-MA
dated: 2026-10-19
status: locked-before-results
---

# Pre-registration — Moving averages / golden cross teardown (graveyard article #2)

**Written and locked 2026-10-19, before any forward-return result was computed.**
This is the fresh standalone test specified by the standardized testing harness for
this project (described in the repo README). It is the **identical methodology** used for
the RSI teardown (the `rsi/` folder) — same universe, same matched control, same effective-n
rules, same bootstrap and multiple-testing correction, same output shape — with **moving-average
signals swapped in for RSI signals**. Every number in the final writeup must come from this test.

---

## 1. Universe & data

Same four asset classes as RSI (so "it's a crypto quirk" cannot apply). Daily bars.
Reuses the exact CSVs pulled for the RSI test (Yahoo Finance daily, public chart API, no key);
no re-pull. Spans verified identical to the RSI test.

| asset | class | symbol (source) | span | note |
|---|---|---|---|---|
| BTC | crypto | BTC-USD (Yahoo) | 2014-09-17 → 2026-10-17 | 7-day calendar |
| SPX | equity index | ^GSPC (Yahoo) | 1970-01-02 → 2026-10-16 | trading days only |
| Gold (XAUUSD proxy) | commodity | GC=F (COMEX gold, Yahoo) | 2000-08-30 → 2026-10-16 | stands in for XAU spot |
| EUR/USD | FX | EURUSD=X (Yahoo) | 2003-12-01 → 2026-10-16 | one immaterial 18-day gap Aug-2008 |

**Bar handling:** drop the currently-forming bar. All MAs and ATR are computed only on
completed bars. A signal that "completes" on bar *t* uses only information known at the
close of *t*. No look-ahead.

## 2. MA definitions (textbook / default)

- **SMA(n):** simple moving average of the **close** over n completed bars.
- **EMA(n):** exponential moving average of the close, smoothing **α = 2/(n+1)**, **seeded
  with SMA(n)** at the first valid bar, then `EMA[t] = α·close[t] + (1−α)·EMA[t−1]`. This is
  the standard charting-platform convention (TradingView / StockCharts).
- **ATR(14):** Wilder ATR (reused from the RSI lib, already verified).
- **Verification (hard gate before any signal is computed):**
  - SMA checked against a direct windowed mean.
  - EMA checked against an independent `pandas.ewm(span=n, adjust=False)` implementation
    seeded identically (must agree to < 1e-9), and against a hand-worked 3-step example.
  Not a black-box endpoint.

## 3. Horizons

Forward horizons **5 / 10 / 20 completed daily bars**. **Primary = 10 bars** (same as RSI,
for cross-article comparability). Forward return entered at the **close of the signal bar**:
`fwd_h = close[t+h]/close[t] − 1` for a long; a short's return is `−fwd_h`.

## 4. Signals (locked list)

Direction convention (explicit): a *long* signal is evaluated long (edge = long fwd − control);
a *short* signal is evaluated short (edge = −fwd − control). Each cross pair produces two
directional events in time: the up-cross (fast above slow, or price above MA) = a **long**
event; the down-cross = a **short** event. For the fade-ish short signals I also report the
plain long forward return where it is informative (does "below the MA" actually keep falling).

Each signal tested in TWO layers where meaningful: **(1) naive** (fire everywhere) and
**(2) trend-conditional** (fire only when aligned with the 200-day SMA regime:
`close > SMA200` = uptrend). The support signals are trend-conditional by construction.

### A. Price vs a moving average — STATE (the "I'm long while price is above the MA" filter)
Sampled **throughout the state**, de-clustered every H bars (not onset-only), because
price-above-MA is a persistent majority condition, not a rare event — the right question is
"what does *being* above the MA pay," not just "the instant it crossed." (This is the one
deliberate implementation difference from RSI's bursty oversold/overbought states, and it is
stated here, before results.)
1. **price > SMA50 → long**; **price < SMA50 → short**.
2. **price > SMA200 → long**; **price < SMA200 → short**.  *(⚠ CIRCULARITY — see §5a.)*

### B. Price crossing a moving average — EVENT (the breakout-entry trigger)
Onset only. Up-cross: `close[t−1] ≤ MA[t−1]` and `close[t] > MA[t]`. Down-cross symmetric.
3. price crosses **up / down through SMA50** → long / short.
4. price crosses **up / down through SMA200** → long / short.  *(⚠ partial coincidence — §5a.)*

### C. MA–MA crosses — the headline (golden / death cross), both directions, SMA **and** EMA
Up-cross = fast MA crosses above slow MA → long; down-cross = fast below slow → short.
5. **SMA 50/200** — golden (long) / death (short).  *(⚠ the headline; correlated with the
   200d regime — §5a.)*
6. **EMA 50/200** — up (long) / down (short).
7. **SMA 20/50** — up / down.
8. **EMA 20/50** — up / down.
9. **SMA 9/21** — up / down.
10. **EMA 9/21** — up / down.
11. **SMA 12/26** — up / down.
12. **EMA 12/26** — up / down.
Pairs 5–12 give a clean **SMA-vs-EMA** comparison on the same windows (item E).

### D. "MA held as support" — direct test of the most-repeated claim
In an uptrend, price pulls back to the rising MA, the MA "holds," price resumes up.
Pre-registered precise definition of a touch-and-hold:
13. **support at SMA50:** `close[t] > SMA200[t]` (uptrend) **and** `close[t] ≥ SMA50[t]`
    (closed back above/at the MA = held) **and** `low[t] ≤ SMA50[t] + 0.5·ATR[t]` (the bar
    dipped to within half an ATR of the MA) → **long**. De-clustered by H.
14. **support at SMA200:** `close[t] ≥ SMA200[t]` **and** `low[t] ≤ SMA200[t] + 0.5·ATR[t]`
    → **long**. (Rarer; reported with its honest effective n.)
The test asks directly: does a bounce off the MA beat a matched random long in the same
uptrend/vol bucket? If the MA were genuinely "support," it should.

### E. SMA vs EMA
Not a separate run — delivered by pairs 5–12 (50/200, 20/50, 9/21, 12/26 in both SMA and EMA).
The writeup compares the two families head-to-head at the primary horizon.

## 5. The matched control (the whole game)

Identical to RSI. Random entries on the **same symbol**, matched on **trend regime**
(`close` above/below **SMA200**) **and** volatility bucket (ATR(14)/close, **per-asset
terciles** over full usable history), **same horizon**. A signal episode in bucket
*(regime, vol)* is compared to the distribution of directional forward returns of **all days
in that same bucket** for that asset & horizon. **Headline edge = signal mean − matched-control
mean**, shown `signal (control)`. Bootstrap (10,000×) resamples each episode from its own
matched bucket → two-sided p for the observed edge. Control pool sizes reported.

### 5a. Circularity — handled explicitly, not silently (REQUIRED by the harness)

The matched control conditions on the **200d SMA regime**. Several MA signals *are* that
reference or a close proxy, so testing them against a 200d-regime control is partly or wholly
tautological. I handle it **both** ways the harness allows and say which applies to each:

- **(b) Report-and-interpret the near-tautology.** For **price vs SMA200 (state, signal 2)**:
  up-state bars are *by definition* the up-regime, so the matched control pool ≈ the signal
  itself → **edge ≈ 0 by construction**. That is not a bug; it is the thesis stated in its
  purest form — *the MA state literally IS the trend label the control already conditions on.*
  I flag it as a tautology, not a discovered null. For the **golden/death cross (signal 5)**
  and **price-cross-SMA200 (signal 4)**: these are slow proxies of the 200d regime (50-day vs
  200-day; the regime label itself), highly correlated but **not identical**, so the matched
  control is a fair-but-conservative reference and the edge is interpretable.

- **(a) Independent-reference robustness.** For the three regime-coincident signals
  (price>SMA200 state, golden/death cross, price-cross-SMA200) I ALSO re-run the matched
  control with a **trend reference independent of every tested MA**: regime = sign of the
  **120-day price change** (`close[t]/close[t−120] − 1`), vol tercile unchanged. 120d momentum
  is distinct from SMA50/SMA200/EMA windows, so if the edge is still ≈ 0 under this independent
  reference, the null is **real**, not manufactured by the control absorbing the signal (and
  conversely a genuine edge would survive). Reported alongside the primary control.

## 6. Effective n — distinct episodes

Raw signal-bar counts overstate n (price sits above a MA for long runs; forward windows
overlap).
- **States (A):** sampled through the state but **de-clustered to ≥ H bars apart** so forward
  windows never overlap; report raw in-state bar count and effective (de-clustered) n.
- **Crosses & price-crosses (B, C) and support (D):** each event is one onset; de-clustered to
  ≥ H bars apart. Report raw count and effective n.
- Effective n is the denominator for every statistic.

## 7. Metrics (compute all; report a curated slice; every number as `signal (control)`)

Identical to RSI:
- **Headline:** edge vs matched control, primary horizon 10 (also 5 & 20).
- **Win rate + avg win vs avg loss.**
- **Run-to-target, vol-normalized:** MFE / MAE in ATR (R) units; fraction reaching +1R before
  −1R (first touch). Never raw %.
- **Per-trade Sharpe vs control.**
- **Per-asset AND pooled.** An edge in one market and not others is itself a finding.
- **Multiple testing:** Benjamini–Hochberg (q=0.10) and Bonferroni (0.05/m) over the
  deduplicated pooled primary-horizon family.
- **Secondary:** absolute P&L vs buy-&-hold (`absolute.py`), recency 10y/5y (`recency.py`) —
  same as RSI.

## 8. What I expect (prior, pre-registered)

Series thesis: an indicator is a transformation of the price you already have, so a moving
average can only restate "price has been trending." A moving average is the **most literal**
possible trend-restatement, so I expect the null to be the *cleanest* of any indicator so far.

1. **Price vs SMA200 (state):** edge ≈ **0 by construction** (tautology, §5a). States the thesis.
2. **Price vs SMA50 (state):** positive raw long return inherited from the trend; edge vs
   matched control ≈ **0** (SMA50-above is just a slightly-faster trend label).
3. **Golden cross (SMA 50/200 long):** positive raw return (it fires in uptrends), but edge vs
   matched control ≈ **0** — the golden cross is a lagging restatement of the 200d regime the
   control already conditions on. Death cross (short): ≈ 0 or slightly negative (shorting a
   market whose base drift is up). I expect the famous golden cross to be the headline null.
4. **Faster crosses (20/50, 9/21, 12/26; SMA & EMA):** null vs matched control across assets;
   more whipsaw, same ≈ 0 edge.
5. **SMA vs EMA:** no meaningful difference — EMA is a faster SMA, not new information.
6. **MA-as-support (bounce off SMA50/200 in an uptrend):** the loudest claim; I expect it to
   be a matched-control null — a pullback-to-the-MA long ≈ a random long in the same uptrend.
7. **BTC caveat:** as with RSI, BTC's secular bull may make long MA signals look strong in BTC
   alone; that is the BTC trend, not the MA. Flag per-asset.

**Adversarial commitment:** report what the data says even if a real, consistent, multi-asset
edge appears and contradicts the thesis. A real edge found is more valuable than a forced null.
Effective n reported honestly even when it kills a result's power. No rounding to flatter a story.

## 9. Deliverables

- `00-preregistration.md` (this file).
- `data/*.csv` raw OHLC per asset (reused from RSI); `results.json` / `results.csv` raw stats.
- `results.md` full table (every signal × asset × horizon, `signal (control)`, n) incl. the
  independent-reference robustness panel and multiple-testing section.
- `summary.md` plain-language, article-ready: every signal, `signal (control)` at primary
  horizon, per-asset + pooled, effective n, one-line takeaway each, SMA-vs-EMA comparison, the
  absolute-P&L and recency sections, and an honesty/limitations section.
