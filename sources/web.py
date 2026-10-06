"""Free sources: CoinGecko trending, Fear & Greed, news RSS."""
from __future__ import annotations

import logging
import feedparser
import httpx

log = logging.getLogger("sabsenti.web")
UA = {"User-Agent": "sabsenti-bot/1.0"}
RSS = [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://decrypt.co/feed",
]


async def trending(client) -> list[tuple[str, str]]:
    """Trending coins are treated as mild bullish attention."""
    try:
        r = await client.get("https://api.coingecko.com/api/v3/search/trending", headers=UA, timeout=20)
        r.raise_for_status()
        return [("coingecko", f"${c['item']['symbol']} trending bullish")
                for c in r.json().get("coins", [])]
    except Exception as e:
        log.warning("coingecko failed: %s", e)
        return []


async def fear_greed(client) -> int | None:
    try:
        r = await client.get("https://api.alternative.me/fng/", headers=UA, timeout=20)
        return int(r.json()["data"][0]["value"])
    except Exception as e:
        log.warning("fear&greed failed: %s", e)
        return None


async def news(client) -> list[tuple[str, str]]:
    out = []
    for url in RSS:
        try:
            r = await client.get(url, headers=UA, timeout=20)
            for e in feedparser.parse(r.text).entries[:30]:
                out.append(("news", f"{e.get('title', '')}. {e.get('summary', '')}"))
        except Exception as e:
            log.warning("rss %s failed: %s", url, e)
    return out

