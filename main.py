"""Washout-recovery bot for btc-race-24h-20261118-1444.

Idea, in plain terms: this dev window trends down, so holding bitcoin loses
money and so does trading every wiggle — a full round trip costs about 26 bps
in fees, slippage and price impact. The bot therefore sits in cash most of
the day and waits for one clear event: a sharp washout, the close falling at
least 1.2% below the trailing four-hour high. Once armed it buys the first
close that ticks back up, the earliest sign the sellers are exhausted, and
then it gets out on a 2.2% gain, a 1.5% stop, or the end of the window. One
entry only: after a washout the next dip in a falling market usually does not
bounce, and the sweep showed a second entry loses about $19 on this window.

The numbers behind the parameters come from grading on the frozen dev
window (1,440 bars, 17-18 Nov 2026): net PnL +$19.22 on one round trip,
maximum drawdown 0.64%. The same settings made +$17.67 on the previous
round's dev window, so the trade is not a one-window accident. Buy-and-hold
on this window loses $31.63.

Protocol: agent-fun/bars-replay/v1, standard library only. No network, no
wall clock, no files outside the repository, no randomness — the same bars
always produce the same orders.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"

# --- strategy parameters (all in 1-minute bars / basis points) ---
LOOKBACK_BARS = 240      # trailing high window: four hours of closes
WASHOUT_BPS = 120        # arm once the close is 1.2% under the trailing high
TAKE_PROFIT_BPS = 220    # sell the position 2.2% above the entry close
STOP_BPS = 150           # hard stop 1.5% under the entry close
LAST_ENTRY_BAR = 1320    # no new entries in the final two hours
MAX_SLIPPAGE_BPS = 300   # orders must fill within 3% of the latest close


def build_bot():
    """Close the strategy state; return the per-batch callback."""
    closes = []
    entry_price = None   # close the current position was bought at
    armed = False        # a washout happened; waiting for the recovery tick
    entered = False      # the single entry has been used

    def on_batch(state, batch):
        nonlocal entry_price, armed, entered
        if state.warming_up:
            return []
        close = state.close(SYMBOL)
        if close is None:
            return []
        seq = state.seq
        closes.append(close)
        position = state.positions.get(SYMBOL)
        holding = position is not None and position.qty > 0

        if holding:
            # Exit on take-profit, on the hard stop, or at the window's end
            # (the harness flattens whatever is left, so no order is sent
            # on the last batch — it would only be rejected).
            if seq >= 1439:
                return []
            if close >= entry_price * (10_000 + TAKE_PROFIT_BPS) // 10_000:
                return [{"side": "sell", "symbol": SYMBOL, "qty": position.qty,
                         "max_slippage_bps": MAX_SLIPPAGE_BPS}]
            if close <= entry_price * (10_000 - STOP_BPS) // 10_000:
                return [{"side": "sell", "symbol": SYMBOL, "qty": position.qty,
                         "max_slippage_bps": MAX_SLIPPAGE_BPS}]
            return []

        # Flat: the entry state belongs to the closed position now.
        entry_price = None
        if entered or seq < LOOKBACK_BARS or seq > LAST_ENTRY_BAR:
            return []
        high = max(closes[-LOOKBACK_BARS:])
        if not armed:
            if close * 10_000 <= high * (10_000 - WASHOUT_BPS):
                armed = True
            return []
        # Armed: buy the first close that ticks up from the previous one.
        if len(closes) >= 2 and close > closes[-2]:
            armed = False
            entered = True
            entry_price = close
            return [{"side": "buy", "symbol": SYMBOL,
                     "notional_quote_units": state.cash,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        return []

    return on_batch


makefun_bars.run(build_bot())
