"""Core indicators for the MA teardown, computed from scratch (no black-box endpoint).
- sma(x, n): NaN-safe simple moving average (window with any NaN -> NaN).
- ema(close, n): textbook EMA, alpha = 2/(n+1), SEEDED with SMA(n) at the first valid
  bar, then EMA[t] = alpha*close[t] + (1-alpha)*EMA[t-1]. Standard charting convention.
- atr_wilder: Wilder ATR from true range (same as the verified RSI lib).

Running this file directly runs the verification gate:
  - SMA vs a direct windowed mean,
  - EMA vs an independent pandas ewm(span=n, adjust=False) implementation seeded identically,
  - EMA vs a hand-worked 3-step example.
"""
import numpy as np
import pandas as pd


def sma(x, length):
    """NaN-safe simple moving average: a window with any NaN yields NaN."""
    return pd.Series(np.asarray(x, float)).rolling(length, min_periods=length).mean().to_numpy()


def ema(close, length):
    """Textbook EMA. alpha = 2/(length+1), seeded with SMA(length) at index length-1,
    then recursive. Leading (length-1) values are NaN."""
    close = np.asarray(close, dtype=float)
    n = len(close)
    out = np.full(n, np.nan)
    if n < length:
        return out
    alpha = 2.0 / (length + 1.0)
    out[length - 1] = close[:length].mean()  # SMA seed
    for i in range(length, n):
        out[i] = alpha * close[i] + (1.0 - alpha) * out[i - 1]
    return out


def _ema_pandas(close, length):
    """Independent EMA implementation for cross-check: seed the SMA at index length-1,
    then pandas ewm(adjust=False) on the tail. Must match ema() to < 1e-9."""
    close = np.asarray(close, dtype=float)
    n = len(close)
    out = np.full(n, np.nan)
    if n < length:
        return out
    seed = close[:length].mean()
    tail = np.concatenate([[seed], close[length:]])
    e = pd.Series(tail).ewm(span=length, adjust=False).mean().to_numpy()
    out[length - 1:] = e
    return out


def atr_wilder(high, low, close, length=14):
    high = np.asarray(high, float); low = np.asarray(low, float); close = np.asarray(close, float)
    n = len(close)
    tr = np.full(n, np.nan)
    tr[0] = high[0] - low[0]
    for i in range(1, n):
        tr[i] = max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1]))
    atr = np.full(n, np.nan)
    if n < length:
        return atr
    atr[length-1] = tr[:length].mean()
    for i in range(length, n):
        atr[i] = (atr[i-1] * (length - 1) + tr[i]) / length
    return atr


if __name__ == "__main__":
    rng = np.random.default_rng(1)
    x = np.cumsum(rng.normal(0, 1, 500)) + 100.0

    # GATE 1: SMA vs direct windowed mean.
    s = sma(x, 50)
    for i in (49, 100, 250, 499):
        assert abs(s[i] - x[i-49:i+1].mean()) < 1e-10, "SMA mismatch"
    print("SMA verified vs direct windowed mean.")

    # GATE 2: EMA vs independent pandas implementation (seeded identically).
    for L in (9, 12, 21, 26, 50, 200):
        a = ema(x, L); b = _ema_pandas(x, L)
        md = np.nanmax(np.abs(a[~np.isnan(a)] - b[~np.isnan(b)]))
        assert md < 1e-9, f"EMA impls disagree at L={L}: {md:.2e}"
    print("EMA verified vs independent ewm(adjust=False) impl (agree < 1e-9) for L in {9,12,21,26,50,200}.")

    # GATE 3: hand-worked EMA, length 3 (alpha = 0.5). closes = [1,2,3,4,5].
    #   seed EMA[2] = mean(1,2,3) = 2.0
    #   EMA[3] = 0.5*4 + 0.5*2.0 = 3.0
    #   EMA[4] = 0.5*5 + 0.5*3.0 = 4.0
    e3 = ema([1, 2, 3, 4, 5], 3)
    assert abs(e3[2] - 2.0) < 1e-12 and abs(e3[3] - 3.0) < 1e-12 and abs(e3[4] - 4.0) < 1e-12, "EMA hand example failed"
    print(f"EMA hand example (len3, alpha0.5): {e3[2]}, {e3[3]}, {e3[4]} == 2.0, 3.0, 4.0")
    print("MA VERIFICATION PASSED")
