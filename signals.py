"""Turn social sentiment + price confirmation into a trade signal."""
from __future__ import annotations

from dataclasses import dataclass

import logging

import config
from market import atr, ema


@dataclass
class Signal:
    symbol: str
    side: str
    leverage: int
    entry: float
    sl: float
    tps: list[float]
    sentiment: float
    mentions: int
    sources: list[str]
    funding_pct: float | None = None
    oi_change_pct: float | None = None


log = logging.getLogger("sabsenti.signals")


def _round(x: float) -> float:
    return float(f"{x:.6g}")


def build_signal(symbol: str, buzz, bars: list[dict], fng: int | None = None,
                 deriv: dict | None = None) -> Signal | None:
    """Sentiment picks direction; price trend must agree (EMA20 vs EMA50) or we skip."""
    if buzz.mentions < config.MIN_MENTIONS or abs(buzz.sentiment) < config.MIN_SENTIMENT:
        log.info("skip %s: weak buzz (%d mentions, sentiment %+.2f)", symbol, buzz.mentions, buzz.sentiment)
        return None
    if len(bars) < 60:
        return None
    side = "LONG" if buzz.sentiment > 0 else "SHORT"
    closes = [b["c"] for b in bars]
    price = closes[-1]
    e20, e50 = ema(closes, 20), ema(closes, 50)
    if (side == "LONG" and not (price > e20 > e50)) or (side == "SHORT" and not (price < e20 < e50)):
        log.info("skip %s: %s sentiment %+.2f but trend disagrees", symbol, side, buzz.sentiment)
        return None
    # Extreme market-wide greed/fear: don't chase the crowd.
    if fng is not None and ((side == "LONG" and fng >= 85) or (side == "SHORT" and fng <= 15)):
        return None
    deriv = deriv or {}
    fund = deriv.get("funding_pct")
    # Crowded positioning: very high funding means longs are paying a lot (and vice versa).
    if fund is not None and ((side == "LONG" and fund > config.FUNDING_MAX_PCT)
                             or (side == "SHORT" and fund < -config.FUNDING_MAX_PCT)):
        log.info("skip %s: %s but funding %+.3f%% shows crowded positioning", symbol, side, fund)
        return None
    risk = atr(bars) * config.ATR_SL_MULT
    if risk <= 0:
        return None
    sgn = 1 if side == "LONG" else -1
    return Signal(
        symbol=symbol, side=side, leverage=config.LEVERAGE, entry=_round(price),
        sl=_round(price - sgn * risk),
        tps=[_round(price + sgn * risk * m) for m in config.TP_MULTIPLES],
        sentiment=round(buzz.sentiment, 2), mentions=buzz.mentions, sources=sorted(buzz.sources),
        funding_pct=fund, oi_change_pct=deriv.get("oi_change_pct"),
    )


def format_signal(s: Signal) -> str:
    arrow = "🟢" if s.side == "LONG" else "🔴"
    lines = [f"{arrow} SIGNAL: #{s.symbol}USDT", "",
             f"Direction: {s.side}", f"Leverage: {s.leverage}X", "",
             f"🎯 Entry: {s.entry}", "💰 Take-Profit:"]
    lines += [f"TP {i}: {tp}" for i, tp in enumerate(s.tps, 1)]
    lines += [f"🛑 Stop Loss: {s.sl}", ""]
    extra = []
    if s.funding_pct is not None:
        extra.append(f"Funding {s.funding_pct:+.3f}%")
    if s.oi_change_pct is not None:
        extra.append(f"OI 6h {s.oi_change_pct:+.1f}%")
    if extra:
        lines.append("📈 " + " · ".join(extra))
    lines += [
              f"📊 Sentiment {s.sentiment:+.2f} · {s.mentions} mentions ({', '.join(s.sources)})",
              "⚠️ Not financial advice. Use your own risk management."]
    return "\n".join(lines)
