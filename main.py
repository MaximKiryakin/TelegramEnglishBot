import asyncio
from os import getenv

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from app.handlers import router

from utils.database import initialize_database

from utils.logger import Logger


load_dotenv()

log = Logger(__name__).get_logger()

TOKEN = getenv("TELEGRAM_BOT_TOKEN")

if TOKEN is None:
    log.critical("TOKEN is not set")
    raise ValueError("TELEGRAM_BOT_TOKEN is not set")

dp = Dispatcher()
bot = Bot(token=TOKEN)

log.info("Initializing database")
initialize_database()
log.info("Database initialized")




async def main() -> None:
    dp.include_router(router)
    log.info("Application started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info('Application stopped')

