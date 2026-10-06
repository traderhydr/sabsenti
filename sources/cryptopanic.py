"""CryptoPanic news with community votes (free API key). Returns [] without a token."""
from __future__ import annotations

import logging

import httpx

log = logging.getLogger("sabsenti.cryptopanic")


def to_items(results: list[dict]) -> list[tuple[str, str]]:
    """One item per (post, currency); community votes decide the polarity keyword."""
    out = []
    for p in results:
        votes = p.get("votes") or {}
        pos = votes.get("positive", 0) + votes.get("liked", 0)
        neg = votes.get("negative", 0) + votes.get("disliked", 0) + votes.get("toxic", 0)
        tone = " bullish" if pos > neg else " bearish" if neg > pos else ""
        for c in p.get("currencies") or []:
            out.append(("cryptopanic", f"${c['code']} {p.get('title', '')}{tone}"))
    return out


async def fetch(client: httpx.AsyncClient, token: str, url: str) -> list[tuple[str, str]]:
    if not token:
        return []
    try:
        r = await client.get(url, params={"auth_token": token, "public": "true", "kind": "news"}, timeout=20)
        if r.status_code >= 400:
            log.warning("CryptoPanic %s: %s", r.status_code, r.text[:300])
            return []
        return to_items(r.json().get("results", []))
    except Exception as e:
        log.warning("CryptoPanic failed: %s", e)
        return []
