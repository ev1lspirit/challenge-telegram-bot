from aiogram import Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message

from db import add_user_to_bot
from keyboard_styles.keyboards import MainMenuKeyboard
from strings import StartPhrases
from validators import is_user_registered

__all__ = "router"

router = Router(name="StartRouter")


@router.message(
    StateFilter(None),
    CommandStart()
)
async def start_message_handler(message: Message):
    if not is_user_registered(message.from_user.id, message.from_user.username):
        await add_user_to_bot(user_id=message.from_user.id, username=message.from_user.username)
    keyboard = MainMenuKeyboard()
    markup = keyboard.markup()
    markup.resize_keyboard = True
    answer_phrase = StartPhrases.basic_template.format(username=message.from_user.username)
    await message.answer(answer_phrase,
                         reply_markup=markup, message=message)


@router.message(
    StateFilter(None),
    Command("help")
)
async def help_message_handler(message: Message):
    await message.answer("Хы")



