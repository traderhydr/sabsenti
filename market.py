"""Binance USDT-perp universe, klines, EMA/ATR."""
from __future__ import annotations

import httpx

BASE = "https://fapi.binance.com"


async def universe(client: httpx.AsyncClient, top_n: int, min_vol: float) -> dict[str, str]:
    """base asset -> symbol (e.g. SOL -> SOLUSDT), top_n by 24h quote volume."""
    r = await client.get(f"{BASE}/fapi/v1/ticker/24hr", timeout=20)
    r.raise_for_status()
    rows = [t for t in r.json() if t["symbol"].endswith("USDT") and float(t["quoteVolume"]) >= min_vol]
    rows.sort(key=lambda t: float(t["quoteVolume"]), reverse=True)
    return {t["symbol"][:-4]: t["symbol"] for t in rows[:top_n]}


async def klines(client, symbol: str, interval="1h", limit=120):
    r = await client.get(f"{BASE}/fapi/v1/klines",
                         params={"symbol": symbol, "interval": interval, "limit": limit}, timeout=20)
    r.raise_for_status()
    return [{"o": float(k[1]), "h": float(k[2]), "l": float(k[3]), "c": float(k[4]), "v": float(k[5])}
            for k in r.json()]


def ema(values: list[float], n: int) -> float:
    k = 2 / (n + 1)
    e = values[0]
    for v in values[1:]:
        e = v * k + e * (1 - k)
    return e


def atr(bars: list[dict], n: int = 14) -> float:
    trs = [max(b["h"] - b["l"], abs(b["h"] - p["c"]), abs(b["l"] - p["c"]))
           for p, b in zip(bars, bars[1:])]
    return sum(trs[-n:]) / n
