
import asyncio
import schedule
import time
import logging
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
from report import build_full_report
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, REPORT_TIME

logging.basicConfig(
format=”%(asctime)s [%(levelname)s] %(message)s”,
level=logging.INFO,
handlers=[
logging.FileHandler(“bot.log”),
logging.StreamHandler()
]
)
log = logging.getLogger(**name**)

async def send_report():
“”“Fetch latest data, build report, send to Telegram.”””
log.info(“Building daily investment report…”)
bot = Bot(token=TELEGRAM_BOT_TOKEN)

```
try:
    sections = build_full_report()
    for i, section in enumerate(sections):
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=section,
            parse_mode=ParseMode.HTML,
        )
        if i < len(sections) - 1:
            await asyncio.sleep(1)  # small delay between messages
    log.info(f"Report sent successfully — {len(sections)} messages")
except Exception as e:
    log.error(f"Failed to send report: {e}")
    # Send error notification
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=f"⚠️ <b>Report Error</b>\n<code>{str(e)}</code>",
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        pass
```

def run_async(coro):
asyncio.run(coro)

def job():
run_async(send_report())

def main():
log.info(f”Bot started. Daily report scheduled at {REPORT_TIME} UTC.”)
log.info(f”Chat ID: {TELEGRAM_CHAT_ID}”)

```
# Send one immediately on startup
log.info("Sending startup report...")
job()

# Schedule daily
schedule.every().day.at(REPORT_TIME).do(job)

while True:
    schedule.run_pending()
    time.sleep(30)
```

if **name** == “**main**”:
main()