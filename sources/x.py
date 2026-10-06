"""X (Twitter) API v2 recent search. Needs a bearer token; returns [] without one."""
import logging
import httpx

log = logging.getLogger("sabsenti.x")
URL = "https://api.twitter.com/2/tweets/search/recent"


async def fetch(client: httpx.AsyncClient, token: str, accounts: list[str]) -> list[tuple[str, str]]:
    if not token:
        return []
    queries = ["(crypto OR bitcoin OR altcoin) (long OR short OR breakout) lang:en -is:retweet"]
    if accounts:
        queries.append("(" + " OR ".join(f"from:{a}" for a in accounts) + ") -is:retweet")
    out = []
    for q in queries:
        try:
            r = await client.get(URL, params={"query": q, "max_results": 100},
                                 headers={"Authorization": f"Bearer {token}"}, timeout=20)
            r.raise_for_status()
            out += [("x", t["text"]) for t in r.json().get("data", [])]
        except Exception as e:
            log.warning("X fetch failed: %s", e)
    return out
