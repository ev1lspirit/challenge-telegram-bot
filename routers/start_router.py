import logging

from aiogram import Router
from aiogram.filters import CommandStart, Command, StateFilter, ChatMemberUpdatedFilter, MEMBER
from aiogram.types import Message, ChatMemberUpdated
from filters import PrivateMessagesScope
from middlewares import RequireRegistrationMiddleware
from keyboard_styles.keyboards import MainMenuKeyboard
from strings import StartPhrases

__all__ = "router"

router = Router(name="StartRouter")
router.message.middleware(RequireRegistrationMiddleware())
router.message.filter(PrivateMessagesScope())
router.my_chat_member.filter(PrivateMessagesScope())


@router.message(
    StateFilter(None),
    CommandStart()
)
async def start_message_handler(message: Message):
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



