import asyncio
import aiohttp
import logging
import json

from aiogram import Bot, Dispatcher, executor, types, md
from aiogram.utils.executor import start_webhook

from collector import Collector

with open("./secrets.json") as f:
    secrets = json.load(f)
    

BOT_TOKEN = secrets['bot']['token']

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# webhook settings
WEBHOOK_HOST = 'https://your.domain'
WEBHOOK_PATH = '/path/to/api'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = 'localhost'  # or ip
WEBAPP_PORT = 5000


collector = Collector()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    logger.info(message)
    await message.reply("Hi")

@dp.message_handler(commands=['stats'])
async def start(message: types.Message):
    logger.info(message)
    await bot.send_message(message.chat.id, "Collecting stats for Ampleforth...")
    await types.ChatActions.typing()

    telegram_members = await collector.get_telegram_members()
    subreddit_subscribers = await collector.get_subreddit_subscribers()

    await bot.send_message(
        message.chat.id,
        md.text(
            md.bold("Stats for Ampleforth:\n"),
            md.code(f"Telegram members: {telegram_members}"),
            md.code(f"Subreddit subscribers: {subreddit_subscribers}"),
        ),
        parse_mode='MARKDOWN'
    )


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dispatcher):
    logger.info("Shutting down...")
    await bot.delete_webhook()
    logger.info("Shutdown successful")


if __name__ == "__main__":
    # executor.start_polling(dp, on_shutdown=on_shutdown)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        # on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
