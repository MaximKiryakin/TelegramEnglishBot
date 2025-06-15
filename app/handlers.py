from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from utils.constant_strings import *
from aiogram.types import CallbackQuery
from utils.database import get_random_phrasal_verb, add_favorite_word


from utils.logger import Logger
log = Logger(__name__).get_logger()

router = Router()


def get_phrasal_verb_kb(word_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Добавить в избранное',
                callback_data=f'favorite_{word_id}'
            )],
            [InlineKeyboardButton(text='Назад', callback_data='back'),
             InlineKeyboardButton(text='Далее', callback_data='forward')]
        ]
    )


@router.callback_query(F.data.startswith('favorite_'))  # Ловим все favorite_{word_id}
async def add_to_favorites(callback: CallbackQuery):
    # Извлекаем word_id из callback_data
    word_id = callback.data.split('_')[1]
    user_id = callback.from_user.id

    # Добавляем в избранное
    try:
        add_favorite_word(user_id, word_id)  # Ваша функция для работы с БД
        await callback.answer('Добавлено в избранное!', show_alert=False)
    except Exception as e:
        await callback.answer('Ошибка при добавлении', show_alert=True)
        log.error(f"Error adding favorite: {e}")

    # Обязательно закрываем callback
    await callback.answer()


@router.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer(START_GREETING)


@router.message(Command("get_phrasal_verb"))
async def command_start_handler(message: Message) -> None:

    phrasal_verb = get_random_phrasal_verb()

    output = PHRASAL_VERB1.format(
        phrasal_verb=phrasal_verb.phrasal_verb,
        translate=phrasal_verb.translate,
        example=phrasal_verb.example
    )

    await message.reply(
        output,
        parse_mode="HTML",
        reply_markup=get_phrasal_verb_kb(phrasal_verb.word_id)
    )
