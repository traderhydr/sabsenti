"""Tiny lexicon sentiment + ticker extraction (no ML deps)."""
import re
from dataclasses import dataclass, field

BULL = {"bullish", "long", "breakout", "pump", "moon", "rally", "surge", "buy",
        "accumulate", "support", "uptrend", "ath", "soar", "adoption", "approval",
        "partnership", "upgrade", "listing", "higher", "reversal"}
BEAR = {"bearish", "short", "dump", "crash", "sell", "rug", "hack", "exploit",
        "downtrend", "breakdown", "resistance", "lawsuit", "ban", "delist",
        "liquidation", "plunge", "lower", "scam", "fud", "rejected"}
NEGATORS = {"not", "no", "never", "isn't", "wont", "won't"}

CASHTAG = re.compile(r"\$([A-Za-z]{2,10})\b")
WORD = re.compile(r"[a-z']+")


def score_text(text: str) -> float:
    """-1..1 polarity of one text."""
    words = WORD.findall(text.lower())
    s = 0
    for i, w in enumerate(words):
        v = 1 if w in BULL else -1 if w in BEAR else 0
        if v and i and words[i - 1] in NEGATORS:
            v = -v
        s += v
    return max(-1.0, min(1.0, s / 3)) if s else 0.0


def extract_symbols(text: str, known: set[str]) -> set[str]:
    """Cashtags ($SOL) plus bare uppercase tickers that exist in `known`."""
    out = {m.upper() for m in CASHTAG.findall(text)}
    out |= {w for w in re.findall(r"\b[A-Z]{2,10}\b", text) if w in known}
    return out & known


@dataclass
class Buzz:
    mentions: int = 0
    total: float = 0.0
    sources: set = field(default_factory=set)

    @property
    def sentiment(self) -> float:
        return self.total / self.mentions if self.mentions else 0.0


def aggregate(items: list[tuple[str, str]], known: set[str]) -> dict[str, Buzz]:
    """items = [(source, text)] -> per-symbol Buzz."""
    out: dict[str, Buzz] = {}
    for src, text in items:
        s = score_text(text)
        for sym in extract_symbols(text, known):
            b = out.setdefault(sym, Buzz())
            b.mentions += 1
            b.total += s
            b.sources.add(src)
    return out
