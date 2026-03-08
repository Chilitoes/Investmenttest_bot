import asyncio
import schedule
import time
import logging
from telegram import Bot
from telegram.constants import ParseMode
from report import build_full_report
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, REPORT_TIME

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(**name**)

async def send_report():
bot = Bot(token=TELEGRAM_BOT_TOKEN)
try:
sections = build_full_report()
for i, section in enumerate(sections):
await bot.send_message(
chat_id=TELEGRAM_CHAT_ID,
text=section,
parse_mode=ParseMode.HTML,
)
if i < len(sections) - 1:
await asyncio.sleep(1)
log.info(“Report sent: “ + str(len(sections)) + “ messages”)
except Exception as e:
log.error(“Failed: “ + str(e))
try:
await bot.send_message(
chat_id=TELEGRAM_CHAT_ID,
text=“Error: “ + str(e),
parse_mode=ParseMode.HTML,
)
except Exception:
pass

def job():
asyncio.run(send_report())

def main():
log.info(“Bot started. Scheduled at “ + REPORT_TIME + “ UTC.”)
log.info(“Sending startup report…”)
job()
schedule.every().day.at(REPORT_TIME).do(job)
while True:
schedule.run_pending()
time.sleep(30)

if **name** == “**main**”:
main()