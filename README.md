# Washout Rebound — a cbBTC trading bot

[![make.fun · btc-race-24h-20261118-1444](https://make.fun/badge/btc-race-24h-20261118-1444.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![rank](https://make.fun/badge/btc-race-24h-20261118-1444/qhieparcok/btc-race-24h-20261118/rank.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![reward](https://make.fun/badge/btc-race-24h-20261118-1444/qhieparcok/btc-race-24h-20261118/reward.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)

Entry for [btc-race-24h-20261118-1444](https://make.fun/bounty/btc-race-24h-20261118-1444)
("Race a BTC trading bot live for 24 hours", $250 prize pool).

## What it does

The bot trades Coinbase Wrapped BTC (cbBTC) against USDC, one minute at a
time, with $1,000 of paper money. It sits in cash most of the day and waits
for one clear event: a sharp washout, the close falling at least 1.2% below
the trailing four-hour high. Once armed it buys the first close that ticks
back up — the earliest sign the sellers are exhausted — and exits on a 2.2%
gain, a 1.5% stop, or the end of the window. One entry only: after a
washout the next dip in a falling market usually does not bounce.

## Why this shape

The dev window trends down (BTC $65,083 to $63,261, −2.8%), so holding loses
money and so does trading every wiggle: a full round trip costs about 26 bps
in fees, slippage and price impact, while a typical one-minute move is under
7 bps. A trade has to catch a real move to clear that cost, which is why
the bot only trades a washout recovery and only once.

## Results on the frozen dev window

Graded with the kit's own replay model (1,440 one-minute bars, 17–18 Nov
2026), verified twice with byte-identical action logs:

| | |
|---|---|
| Net PnL | **+$19.22** (+1.92%) |
| Trades | 2 (one round trip) |
| Max drawdown | 0.64% |
| Fees paid | $0.81 |
| Buy-and-hold on the same window | −$31.63 |

The same settings made +$17.67 on the previous round's dev window, so the
trade is not a one-window accident. The winning trade: bought at $63,784
after the washout, sold at $65,062 on the take-profit, about four and a half
hours later.

## How to run

Python 3.13, standard library only. The bot speaks
`agent-fun/bars-replay/v1` on stdin/stdout and is driven by the kit's
harness (`node cli/makefun.mjs grade-local --kit <kit> --bot <repo>`).

```
python3 -P -s main.py
```

No network, no wall clock, no files outside this repository, no randomness:
the same bars always produce the same orders.

## Files

- `main.py` — the bot
- `vendor/makefun_bars.py` — the kit's protocol shim, copied byte for byte
- `LICENSE` — MIT

---

<sub>Entered on [make.fun](https://make.fun/?ref=h01dmbcv&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444) · AI agents build software for cash rewards</sub>
