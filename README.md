# A Trader's Workbench — test code & results

The reproducible tests behind the "graveyard" series at
[A Trader's Workbench](https://tobiasowen.substack.com) — where I test the indicators
traders swear by and show what the numbers actually say.

Each folder is one indicator's teardown: the pre-registration (the design and my
predictions, written **before** any results were computed), the data, the analysis code,
and the full results. Nothing here is cherry-picked — every signal I tested is reported,
including the ones that did nothing.

## What's here

- **`moving-averages/`** — the golden/death cross, price-vs-MA, the faster EMA crosses, and
  "the MA held as support." (Teardown #1)
- **`rsi/`** — overbought/oversold, level crossings (30/50/70), and RSI vs its own signal line. (Teardown #2)

Inside each folder:

| file | what it is |
|---|---|
| `00-preregistration.md` | the design and predictions, locked before looking at results |
| `fetch.py`, `*_lib.py`, `analyze.py` | pull the data, compute the indicator (verified against hand-calcs), run the test |
| `results.md` | the full tables — every signal × market × horizon |
| `summary.md` | the plain-language writeup the article is built from |
| `data/` | the daily OHLC used (public Yahoo Finance data) |

## The method, in one paragraph

Every signal is compared not to zero but to a **matched random entry on the same market** —
same trend regime (above or below the 200-day average) and same volatility bucket, same
holding period. The "edge" is only what survives subtracting a coin-flip entry made in the
same conditions. Four markets (Bitcoin, the S&P 500, gold, EUR/USD), daily bars, as much
history as the data allows. Repeated signals are de-clustered into distinct episodes so the
counts aren't inflated, the p-values are bootstrapped, and the headline results are corrected
for multiple testing. The full method is in each folder's `00-preregistration.md`.

## Reproduce it

```
cd rsi            # or: cd moving-averages
python -I fetch.py    # rsi only — moving-averages reuses the same data, already in its data/ folder
python -I analyze.py
```

(Python 3 with pandas/numpy.)

---

*Not financial advice. No entries, no targets, no position sizes — this is testing, not a
signal service.*
