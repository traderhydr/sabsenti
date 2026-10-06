import logging
import httpx

log = logging.getLogger("sabsenti.tg")


async def send(client: httpx.AsyncClient, token: str, chat_id: str, text: str) -> bool:
    if not token or not chat_id:
        print("[dry-run]\n" + text + "\n")
        return True
    try:
        r = await client.post(f"https://api.telegram.org/bot{token}/sendMessage",
                              json={"chat_id": chat_id, "text": text}, timeout=20)
        r.raise_for_status()
        return True
    except Exception as e:
        log.error("telegram send failed: %s", e)
        return False
