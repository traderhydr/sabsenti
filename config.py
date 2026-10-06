import os
from dotenv import load_dotenv

load_dotenv()


def _f(name, default):
    return float(os.getenv(name, default))


def _list(name, default=""):
    return [x.strip() for x in os.getenv(name, default).split(",") if x.strip()]


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")
X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN", "")
X_ACCOUNTS = _list("X_ACCOUNTS")
SCAN_SECONDS = int(_f("SCAN_SECONDS", 300))
TOP_N = int(_f("TOP_N", 40))
MIN_QUOTE_VOLUME_USD = _f("MIN_QUOTE_VOLUME_USD", 50_000_000)
MIN_SENTIMENT = _f("MIN_SENTIMENT", 0.25)
MIN_MENTIONS = int(_f("MIN_MENTIONS", 3))
LEVERAGE = int(_f("LEVERAGE", 5))
ATR_SL_MULT = _f("ATR_SL_MULT", 1.5)
TP_MULTIPLES = [float(x) for x in _list("TP_MULTIPLES", "1.0,1.8,2.6")]
COOLDOWN_HOURS = _f("COOLDOWN_HOURS", 12)
MAX_SIGNALS_PER_SCAN = int(_f("MAX_SIGNALS_PER_SCAN", 2))
