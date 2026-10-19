# Did the signal pick the WHEN? — results

Answers the reader's second objection: *"the signal told me WHEN to buy; a random buy or
buy-and-hold could have been earlier or later and returned something different."* Correct — so
the signal's entry timing is judged against the **distribution** of alternative timings, holding
the **same duration** (the actual golden→death / RSI>50 segment length) each time. Produced by
`timing_test.py`. Close-to-close, no look-ahead, no costs.

## Did entering ON the signal beat a same-duration entry elsewhere?

For each real long segment (length L), signal return vs buying and holding L bars starting at a
random day — **(A)** anywhere in history, and **(B)** restricted to the same 200d-regime and
volatility tercile ("same kind of market"). Shown signal (control), edge, p.

### Golden / death cross
| asset | vs ANY-day random | vs SAME regime+vol random | n segments |
|---|---|---|---|
| BTC | +254.8% (+112.7%) +142.1 p0.08 | +254.8% (+153.8%) +101.0 **p0.21** | 10 |
| SPX | +17.7% (+14.3%) +3.4 p0.40 | +17.7% (+13.9%) +3.8 **p0.32** | 27 |
| Gold | +17.3% (+15.6%) +1.7 p0.77 | +17.3% (+17.2%) +0.1 **p0.99** | 16 |
| EUR/USD | +0.5% (−0.1%) +0.6 p0.73 | +0.5% (−1.6%) +2.1 **p0.15** | 16 |

### RSI-50 regime
| asset | vs ANY-day random | vs SAME regime+vol random | n segments |
|---|---|---|---|
| BTC | +5.2% (+2.8%) +2.4 p0.04 | +5.2% (+3.0%) +2.1 **p0.07** | 190 |
| SPX | +0.4% (+0.4%) +0.0 p1.00 | +0.4% (+0.5%) −0.0 **p0.91** | 762 |
| Gold | +0.4% (+0.5%) −0.1 p0.47 | +0.4% (+0.5%) −0.1 **p0.43** | 356 |
| EUR/USD | −0.1% (+0.0%) −0.1 p0.22 | −0.1% (+0.0%) −0.1 **p0.17** | 339 |

**Reading.** Holding for the signal's own duration, entering *on* the signal did **not**
significantly beat entering at a random comparable time, in any market — every "same regime+vol"
p is ≥ 0.07. The golden cross's biggest-looking number (BTC +101 edge) sits at p0.21 on ten
segments: noise. The only sub-0.05 reading anywhere is RSI-50 in BTC *versus an any-day entry*
(p0.04) — and even that fades to p0.07 once you compare against entries in the same regime, and
it is one asset. The precise "when" carried no reliable information.

Note the two columns: **(A) any-day** is where the signal can look good just by being long in
uptrends (it beats a random entry that might land in a bear market) — but that is regime
selection, i.e. being in the trend, not timing skill. **(B) same regime+vol** removes that, and
the edge collapses. "It told me when" is really "it kept me in the uptrend," which the naked
trend already does.

## Placebo: shift every entry/exit by k bars (whole-system compounded return)

| | k=−20 | k=−10 | k=−5 | **k=0** | k=+5 | k=+10 | k=+20 |
|---|---|---|---|---|---|---|---|
| Golden/death BTC | 137,137% | 30,284% | 22,085% | **14,449%** | 14,495% | 9,862% | 7,266% |
| Golden/death SPX | 36,685% | 11,379% | 7,269% | **6,060%** | 5,323% | 5,351% | 5,037% |
| Golden/death Gold | 2,014% | 1,546% | 1,106% | **695%** | 632% | 860% | 946% |
| Golden/death EUR/USD | 104% | 46% | 26% | **6%** | 1% | −3% | −10% |

**Reading (with one caveat).** Entering a week *later* than the cross (k=+5) gives essentially
the same result as entering on it (BTC 14,495% vs 14,449%; SPX, Gold within noise) — the exact
cross day is **not a special peak**. ⚠ The *negative*-k (earlier) columns are **not** clean
evidence: shifting exposure earlier bleeds look-ahead (you're long before the signal exists), so
the big earlier-entry numbers are partly an artifact and are **not** used to claim "earlier is
better." The clean takeaway is only that k=0 is unremarkable versus its later neighbours. For the
high-turnover **RSI-50** system the shift produces degenerate look-ahead blow-ups (billions of %
at k=−5) and is **uninterpretable** — the same-duration entry test above is the right tool there,
and it says null.

## Verdict

"The signal told me WHEN" decomposes into two claims:
- **"It kept me long in the right regime."** True — but that is trend-following; the naked
  200-day trend does the same, and the series already credits trend persistence as the one edge.
- **"It nailed the precise entry."** False. Holding the same duration, entering on the signal did
  not beat entering at a random same-regime time, and entering a week later barely changed the
  result. The cross is a lagging confirmation, not a timing edge.

And on buy-and-hold: the reader is right that a single B&H number is start-date-dependent — which
is exactly why the fair benchmark is the *distribution* of alternative entry timings, not one run.
Against that distribution the signal's timing is not special.
