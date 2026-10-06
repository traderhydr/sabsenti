# sabsenti

Telegram trade-signal bot. It scans **X (Twitter)**, crypto news RSS and CoinGecko trending for coins people are talking about, scores the sentiment, and only posts a signal when **price action agrees** (EMA20/50 trend on Binance futures 1h candles). Stops and targets are ATR-based.

Pipeline: sources → `sentiment.py` (cashtags + lexicon score) → `signals.py` (direction from sentiment, confirmed by trend, vetoed at extreme Fear & Greed) → `telegram.py`.

## Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add TELEGRAM_BOT_TOKEN / TELEGRAM_CHANNEL_ID (optional X_BEARER_TOKEN)
python bot.py          # dry-run (prints signals) until Telegram vars are set
pytest
```
Add the bot as an admin of your channel; `TELEGRAM_CHANNEL_ID` is `@channelname` or the numeric id.

## Notes
- X search needs a paid X API tier; without a token the other sources still work.
- Heuristic sentiment is crude. Backtest/paper-trade before trusting it, and treat output as ideas, not advice.
- Per-symbol cooldown and per-scan cap limit spam (`state.json`).
