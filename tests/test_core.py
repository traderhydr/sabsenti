import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import sentiment, signals
from sentiment import Buzz


def test_score_and_negation():
    assert sentiment.score_text("SOL breakout, very bullish") > 0
    assert sentiment.score_text("ETH crash and dump") < 0
    assert sentiment.score_text("not bullish") < 0


def test_extract_symbols():
    assert sentiment.extract_symbols("Buying $sol and BTC today", {"SOL", "BTC", "ETH"}) == {"SOL", "BTC"}


def _bars(start, step, n=100):
    out, p = [], start
    for _ in range(n):
        p += step
        out.append({"o": p, "h": p + 1, "l": p - 1, "c": p, "v": 1})
    return out


def test_long_signal_on_uptrend():
    s = signals.build_signal("SOL", Buzz(5, 3.0, {"x", "news"}), _bars(100, 1))
    assert s and s.side == "LONG" and s.sl < s.entry < s.tps[0] < s.tps[-1]


def test_skip_when_trend_disagrees():
    assert signals.build_signal("SOL", Buzz(5, 3.0, {"x"}), _bars(200, -1)) is None


def test_skip_weak_buzz():
    assert signals.build_signal("SOL", Buzz(1, 1.0, {"x"}), _bars(100, 1)) is None


def test_short_signal_levels():
    s = signals.build_signal("SOL", Buzz(5, -3.0, {"x"}), _bars(300, -1))
    assert s and s.side == "SHORT" and s.tps[-1] < s.tps[0] < s.entry < s.sl


def test_funding_veto_and_display():
    from sources import cryptopanic
    assert signals.build_signal("SOL", Buzz(5, 3.0, {"x"}), _bars(100, 1), deriv={"funding_pct": 0.2}) is None
    s = signals.build_signal("SOL", Buzz(5, 3.0, {"x"}), _bars(100, 1), deriv={"funding_pct": 0.01, "oi_change_pct": 4.2})
    assert s and "Funding +0.010%" in signals.format_signal(s) and "OI 6h +4.2%" in signals.format_signal(s)
    items = cryptopanic.to_items([{"title": "ETF approval", "currencies": [{"code": "SOL"}], "votes": {"positive": 5, "negative": 1}}])
    assert items == [("cryptopanic", "$SOL ETF approval bullish")]
