import asyncio
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

from utils.logger import Logger

from utils.constant_strings import *
from utils.database import get_random_phrasal_verb


load_dotenv()

log = Logger(__name__).get_logger()

TOKEN = getenv("TELEGRAM_BOT_TOKEN")

if TOKEN is None:
    log.critical("TOKEN is not set")
    raise ValueError("TELEGRAM_BOT_TOKEN is not set")

dp = Dispatcher()


@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer(START_GREETING)


@dp.message(Command("get_phrasal_verb"))
async def command_start_handler(message: Message) -> None:

    phrasal_verb = get_random_phrasal_verb()

    output = PHRASAL_VERB1.format(
        phrasal_verb=phrasal_verb.phrasal_verb,
        translate=phrasal_verb.translate,
        example=phrasal_verb.example
    )

    await message.answer(output, parse_mode="HTML")



async def main() -> None:
    bot = Bot(token=TOKEN)
    log.info("Application started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

