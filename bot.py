"""sabsenti: scan X + web sentiment, confirm with price, post signals to Telegram."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from pathlib import Path

import httpx

import config
import market
import sentiment
import signals
import telegram
from sources import cryptopanic, web, x

log = logging.getLogger("sabsenti")
STATE = Path(__file__).with_name("state.json")


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text())
    except Exception:
        return {}


def save_state(st: dict) -> None:
    STATE.write_text(json.dumps(st))


async def scan_once(client, state: dict) -> int:
    uni = await market.universe(client, config.TOP_N, config.MIN_QUOTE_VOLUME_USD)
    items, fng = [], None
    results = await asyncio.gather(
        x.fetch(client, config.X_BEARER_TOKEN, config.X_ACCOUNTS),
        web.trending(client), web.news(client), web.fear_greed(client),
        cryptopanic.fetch(client, config.CRYPTOPANIC_TOKEN, config.CRYPTOPANIC_URL))
    for r in (results[0], results[1], results[2], results[4]):
        items += r
    fng = results[3]
    buzz = sentiment.aggregate(items, set(uni))
    log.info("%d items, %d symbols with buzz, fear&greed=%s", len(items), len(buzz), fng)

    ranked = sorted(buzz.items(), key=lambda kv: kv[1].mentions * abs(kv[1].sentiment), reverse=True)
    sent = 0
    for base, b in ranked:
        if sent >= config.MAX_SIGNALS_PER_SCAN:
            break
        if time.time() - state.get(base, 0) < config.COOLDOWN_HOURS * 3600:
            continue
        sig = signals.build_signal(base, b, await market.klines(client, uni[base]), fng,
                                   await market.derivatives(client, uni[base]))
        if sig and await telegram.send(client, config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHANNEL_ID,
                                       signals.format_signal(sig)):
            state[base] = time.time()
            sent += 1
    save_state(state)
    return sent


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    if not config.TELEGRAM_BOT_TOKEN:
        log.warning("No TELEGRAM_BOT_TOKEN: dry-run mode (signals print to console)")
    state = load_state()
    async with httpx.AsyncClient(follow_redirects=True) as client:
        while True:
            try:
                await scan_once(client, state)
            except Exception:
                log.exception("scan failed")
            await asyncio.sleep(config.SCAN_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
