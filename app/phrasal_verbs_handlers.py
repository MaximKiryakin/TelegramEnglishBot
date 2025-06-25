from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from utils.constant_strings import *
from aiogram.types import CallbackQuery
from utils.database import *

from typing import Dict, List
from utils.logger import Logger
log = Logger(__name__).get_logger()

router = Router()
user_sessions = {}


async def show_start_menu(respond_method: callable):
    await respond_method(START_GREETING)


@router.callback_query(F.data == 'back_to_start_menu')
async def back_to_start_menu(callback: CallbackQuery):
    await show_start_menu(callback.message.answer)
    await callback.answer()


@router.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await show_start_menu(message.answer)


def pv_hub_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='▶ Начать тренировку', callback_data='next_verb')],
            [
                InlineKeyboardButton(text='↩ Назад', callback_data='back_to_start_menu'),
                InlineKeyboardButton(text='⚙️ Параметры', callback_data='pv_parameters')
            ]
        ]
    )


def get_training_kb(word_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Завершить', callback_data='end_training'),
                InlineKeyboardButton(text='Следующий', callback_data='next_verb')

            ],
            [InlineKeyboardButton(text='Добавить в избранное', callback_data=f'favorite_{word_id}')]
        ]
    )


async def show_phrasal_verbs_menu(respond_method: callable, user_id: int):

    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'count': 0,
            'verbs': [],
            'welcome_message_id': None,
            'favorite_words': await get_favorite_words(user_id),
            'current_training_verbs': []
        }

    sent_message = await respond_method(
        PV_INTRO,
        parse_mode="Markdown",
        reply_markup=pv_hub_kb()
    )

    user_sessions[user_id]["welcome_message_id"] = sent_message.message_id


@router.message(Command("Phrasal_verbs"))
async def start_training_handler(message: Message):
    await show_phrasal_verbs_menu(message.answer, message.from_user.id)


@router.callback_query(F.data == 'back_to_phrasal_verb_menu')
async def back_to_phrasal_verb_menu(callback: CallbackQuery):
    await show_phrasal_verbs_menu(callback.message.answer, callback.message.from_user.id)
    await callback.answer()


@router.callback_query(F.data == 'next_verb')
async def next_verb_handler(callback: CallbackQuery):

    user_id = callback.from_user.id
    user_info = await get_user_info(user_id)
    session = user_sessions[user_id]
    session["count"] += 1

    if session["count"] >= user_info.pv_quiz_words_num:
        learned_verbs = "\n".join(
            f"{verb.phrasal_verb:15} - {verb.translate}"
            for verb in session["verbs"]
        )

        await callback.message.edit_text(
            TRAINING_END.format(learned_verbs),
            parse_mode="Markdown",
            reply_markup=pv_hub_kb()
        )
        user_sessions[user_id]['count'] = 0
        user_sessions[user_id]["verbs"] = []

        await callback.answer()
        return

    if user_info.fv_use_favourite:
        phrasal_verb = session["favorite_words"][session["count"] - 1]
    elif not user_sessions[user_id]['current_training_verbs']:
        user_sessions[user_id]['current_training_verbs'] \
            = await get_random_phrasal_verbs(user_info.pv_quiz_words_num)
        phrasal_verb = session["current_training_verbs"][0]
    else:
        phrasal_verb = session["current_training_verbs"][session["count"] - 1]

    session["verbs"].append(phrasal_verb)

    output = PHRASAL_VERB1.format(
        phrasal_verb=phrasal_verb.phrasal_verb,
        translate=phrasal_verb.translate,
        example=phrasal_verb.example
    )

    await callback.message.edit_text(
        f"Прогресс: {session['count']}/{user_info.pv_quiz_words_num}\n\n" + output,
        parse_mode="HTML",
        reply_markup=get_training_kb(phrasal_verb.word_id)
    )
    await callback.answer()


def pv_parameters_kb(favorite: bool = False) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='☆ Только избранные'
                    if not favorite else '🌿 Все глаголы',
                    callback_data='change2'
                ),
            ],
            [InlineKeyboardButton(text='Объём: 5', callback_data='change1_5')],
            [InlineKeyboardButton(text='Объём: 10', callback_data='change1_10')],
            [InlineKeyboardButton(text='Объём: 15', callback_data='change1_15')],
            [InlineKeyboardButton(text='Объём: 20', callback_data='change1_20')],
            [InlineKeyboardButton(text='↩ Назад', callback_data='back_to_phrasal_verb_menu')],
        ]
    )


@router.callback_query(F.data == 'pv_parameters')
async def pv_parameters_handler(callback: CallbackQuery):

    user_info = await get_user_info(callback.from_user.id)

    await callback.message.answer(
        PV_ANSWER.format(
            user_info.pv_quiz_words_num,
            'ДА' if user_info.fv_use_favourite else 'НЕТ'
        ),
        reply_markup=pv_parameters_kb(favorite=user_info.fv_use_favourite)
    )
    await callback.answer()


@router.callback_query(F.data == 'change2')
async def change1_handler(callback: CallbackQuery):

    user_info = await get_user_info(callback.from_user.id)

    if not user_info.fv_use_favourite and len(user_sessions[callback.from_user.id]['favorite_words']) < user_info.pv_quiz_words_num:
        ans = (
            PV_RPE_ANSWER.format(
                len(user_sessions[callback.from_user.id]['favorite_words'])
            ) + PV_ANSWER.format(
                user_info.pv_quiz_words_num,
                'ДА' if user_info.fv_use_favourite else 'НЕТ'
            )
        )
    else:
        user_info.fv_use_favourite = not user_info.fv_use_favourite
        await update_user_info(user_info)

        ans = PV_ANSWER.format(
            user_info.pv_quiz_words_num,
            'ДА' if user_info.fv_use_favourite else 'НЕТ'
        )

    if callback.message.text.strip().split(' ') != ans.strip().split(' '):
        await callback.message.edit_text(
            ans,
            reply_markup=pv_parameters_kb(favorite=user_info.fv_use_favourite)
        )

    await callback.answer()


@router.callback_query(F.data.startswith('change1_'))
async def add_to_favorites(callback: CallbackQuery):

    new_quiz_words_num = callback.data.split('_')[1]
    user_info = await get_user_info(callback.from_user.id)

    user_info.pv_quiz_words_num = int(new_quiz_words_num)

    if len(user_sessions[callback.from_user.id]['favorite_words']) < user_info.pv_quiz_words_num and user_info.fv_use_favourite:
        user_info.fv_use_favourite = not user_info.fv_use_favourite

    await update_user_info(user_info)

    await callback.message.edit_text(
        PV_ANSWER.format(user_info.pv_quiz_words_num, 'ДА' if user_info.fv_use_favourite else 'НЕТ'),
        reply_markup=pv_parameters_kb(favorite=user_info.fv_use_favourite)
    )
    await callback.answer()


@router.callback_query(F.data == 'end_training')
async def end_training_handler(callback: CallbackQuery):

    user_id = callback.from_user.id
    session = user_sessions.get(user_id)

    if not session:
        await callback.answer("Тренировка не начата")
        return

    learned_verbs = format_verbs_aligned(session["verbs"])

    await callback.message.answer(
        TRAINING_END.format(learned_verbs),
        reply_markup=pv_hub_kb()
    )
    del user_sessions[user_id]
    await callback.answer()









# @router.message(Command("start_training"))
# async def start_training_handler(message: Message) -> None:
#
#     user_id = message.from_user.id
#     user_sessions[user_id] = {"count": 0, "verbs": []}
#
#     phrasal_verb = get_random_phrasal_verb()
#     user_sessions[user_id]["verbs"].append(phrasal_verb)
#
#     output = PHRASAL_VERB1.format(
#         phrasal_verb=phrasal_verb.phrasal_verb,
#         translate=phrasal_verb.translate,
#         example=phrasal_verb.example
#     )
#
#     await message.answer(
#         "Тренировка началась! Всего будет 10 фразовых глаголов.\n\n" + output,
#         parse_mode="HTML",
#         reply_markup=get_training_kb(phrasal_verb.word_id)
#     )


def format_verbs_aligned(verbs):
    # Находим максимальные длины для каждого столбца
    max_verb_len = max(len(verb.phrasal_verb) for verb in verbs)
    max_translate_len = max(len(verb.translate) for verb in verbs)

    formatted_lines = []
    for verb in verbs:
        # Форматируем строку с выравниванием обоих столбцов
        line = f"{verb.phrasal_verb}" + " "*(max_verb_len - len(verb.phrasal_verb)) + f" -- {verb.translate}"
        print(line)
        formatted_lines.append(line)

    return "\n".join(formatted_lines)







@router.callback_query(F.data.startswith('favorite_'))
async def add_to_favorites(callback: CallbackQuery):

    word_id = callback.data.split('_')[1]
    user_id = callback.from_user.id

    try:
        await add_favorite_word(user_id, word_id)
        await callback.answer('Добавлено в избранное!', show_alert=False)
    except Exception as e:
        await callback.answer('Ошибка при добавлении', show_alert=True)
        log.error(f"Error adding favorite: {e}")

    # Обязательно закрываем callback
    await callback.answer()





