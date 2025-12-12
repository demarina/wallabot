from __future__ import annotations

import asyncio
import logging
from typing import Dict, List

from telegram import Bot

logger = logging.getLogger(__name__)

TOKEN = "8503794608:AAFOtwDIw6sf3K8H1jH4CN8t7YzFmC6uNMA"
CHAT_ID = "1547463803"


async def main(text: str):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text)


def send_telegram_messages(results: List[Dict]) -> int:
    count = 0
    for r in results:
        if not r["is_underpriced"]:
            continue
        print("Sending telegram message")
        text = (
            f"🚲 Oferta potencial!\n"\
            f"{r["texto"]}\n"\
            f"Precio: {r["precio"]}]\n"\
            f"Precio referencia: {500}\n"\
            f"Descuento: {r["descuento"]}%\n"\
            f"Link: {r["link"]}"
        )
        asyncio.run(main(text))
    return count


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    r = [{"texto": "Bicicleta de montaña", "precio": 300, "descuento": 40, "link": "http://example.com", "is_underpriced": True},
         {"texto": "Bicicleta de carretera", "precio": 800, "descuento": 10, "link": "http://example.com", "is_underpriced": False},
         {"texto": "Bicicleta híbrida", "precio": 450, "descuento": 25, "link": "http://example.com", "is_underpriced": True}]
    send_telegram_messages(r)
