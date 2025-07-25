import asyncio
from os import getenv

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from app.phrasal_verbs_handlers import router

from utils.database import initialize_database
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from utils.constant_strings import *
from utils.logger import Logger


load_dotenv()

log = Logger(__name__).get_logger()

TOKEN = getenv("TELEGRAM_BOT_TOKEN")

if TOKEN is None:
    log.critical("TOKEN is not set")
    raise ValueError("TELEGRAM_BOT_TOKEN is not set")

dp = Dispatcher()
bot = Bot(token=TOKEN)


async def main() -> None:


    log.info("Initializing database")
    await initialize_database()
    log.info("Database initialized")
    dp.include_router(router)
    log.info("Application started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info('Application stopped')


