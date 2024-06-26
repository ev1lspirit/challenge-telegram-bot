import logging

from aiogram import Router
from aiogram.filters import CommandStart, Command, StateFilter, ChatMemberUpdatedFilter, MEMBER, KICKED, IS_NOT_MEMBER, \
    IS_MEMBER
from aiogram.types import Message
from filters import PrivateMessageScope
from keyboard_styles.keyboards import MainMenuKeyboard
from strings import StartPhrases

__all__ = "router"

router = Router(name="StartRouter")
router.message.filter(PrivateMessageScope())
router.my_chat_member.filter(PrivateMessageScope())
logger = logging.getLogger(__name__)


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



