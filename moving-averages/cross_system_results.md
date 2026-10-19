# Indicator traded as a POSITION SYSTEM (hold between signals) — results

Answers the reader's objection: *"on BTC daily you buy every golden cross and sell at the death
cross and make way more than your 10-day number says."* True — so here is the actual system,
and two fair comparisons. Produced by `cross_system.py`. Close-to-close, entry/exit at the
signal bar's close, **no transaction costs (favours the system)**. Long/flat is the system;
L/S also shown. "beat rand" = percentile of the actual system inside a 5,000-path random-timing
control (same long stretches, same lengths, placed at random — identical time-in-market, only
the timing randomized). ~50% = timing added nothing; >50% = timing beat random placement.

Windows differ slightly between the two systems (the cross needs SMA200 warmup, so it starts
~186 bars later than the RSI-50 system — which is why the buy-&-hold column differs per system).

## Golden / death cross (long while SMA50 > SMA200)

| asset | buy & hold | B&H maxDD | SYSTEM | SYS maxDD | % in mkt | # entries | long/short | random median | beat rand |
|---|---|---|---|---|---|---|---|---|---|
| BTC | +32,014% | −83% | **+14,449%** | −69% | 61% | 11 | +1,481% | +3,494% | 85th |
| SPX | +8,998% | −57% | **+6,060%** | −34% | 73% | 28 | +1,918% | +2,392% | 96th |
| Gold | +1,435% | −44% | **+695%** | −35% | 72% | 15 | +224% | +661% | 56th |
| EUR/USD | −7% | −40% | **+6%** | −23% | 51% | 16 | +1% | −5% | 68th |

## RSI-50 regime (long while RSI(14) > 50)

| asset | buy & hold | B&H maxDD | SYSTEM | SYS maxDD | % in mkt | # entries | long/short | random median | beat rand |
|---|---|---|---|---|---|---|---|---|---|
| BTC | +21,138% | −83% | **+58,564%** | −57% | 56% | 200 | +10,308% | +1,896% | 100th |
| SPX | +8,407% | −57% | **+1,852%** | −45% | 63% | 769 | +58% | +1,616% | 58th |
| Gold | +1,454% | −44% | **+181%** | −32% | 57% | 367 | −65% | +386% | 10th |
| EUR/USD | −9% | −40% | **−41%** | −51% | 50% | 354 | −68% | −5% | 1st |

## How to read this honestly

**1. The reader is right that the system makes far more than the 10-day forward number.** The
golden-cross system made +14,449% on BTC and +6,060% on the S&P — not +3.11%. Conceded.

**2. But in every market that trended, the system made LESS than simply buying and holding.**
BTC 14,449% vs 32,014%; SPX 6,060% vs 8,998%; Gold 695% vs 1,435%. You crossed in and out for
years to *underperform* the asset. The only market where the golden cross beat buy-and-hold is
EUR/USD (+6% vs −7%) — the one with no uptrend, where sitting out the downlegs helped.

**3. The system's one genuine benefit is drawdown, not return.** It was long only 61–73% of the
time, so it sidestepped the worst stretches: BTC max drawdown −69% vs −83%, SPX −34% vs −57%,
EUR/USD −23% vs −40%. That is a real risk-management property of trend-following — but it is not
the indicator predicting anything; it is the indicator keeping you out during clustered downturns.

**4. Where the timing beats random placement, it's trend persistence — the one edge the series
already credits.** The golden cross beats a matched random-timing system at the 56th–96th
percentile (highest on SPX, 96th) because it concentrates its long periods inside the real bull
runs and stays flat through the clustered bear periods. That is exactly "what's been going up
keeps going up," harvested through a lagging filter — not the moving average seeing the future.
It is also inconsistent: the RSI-50 system beat random 100th percentile in BTC but was WORSE than
random in gold (10th) and EUR/USD (1st), where the whipsaw actively hurt.

**5. RSI-50 is a split decision that proves the point.** It beat buy-and-hold only in BTC
(+58,564% vs +21,138%, by dodging the crashes) and underperformed badly everywhere else
(Gold +181% vs +1,454%; EUR/USD −41% vs −9% — it lost more than holding). 200–769 round trips,
before costs; real-world frictions would gut the fast ones.

## Verdict (consistent with the forward-return test)

Two different questions, both answered honestly:
- *Does the signal moment predict the next move better than a coin flip in the same trend and
  volatility?* — **No** (the 10-day forward test, which controls for regime).
- *Does holding the position between signals make money?* — **Yes, by riding and dodging the
  trend** — but it underperforms buy-and-hold wherever the market trended, its only reliable
  benefit is lower drawdown, and any timing advantage over a matched-exposure random system is
  small, inconsistent across markets, and is the trend-persistence effect this series already
  credits. The money is the trend's; the indicator is the vehicle, and a leaky one.
