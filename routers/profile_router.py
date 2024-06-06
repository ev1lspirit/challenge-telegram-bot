import datetime

import aiogram.types
from aiogram.types import Message
from aiogram import F, Router
from aiogram.filters import Command, StateFilter

from callback_data import ShowMyChallengesCB
from db import select_query
from keyboard_styles import ProfileKeyboard
from .filters import RequireRegistration, PrivateMessagesScope
from strings import ShowProfileInfoPhrases


router = Router(name='ProfileRouter')


@router.message(Command("profile"),
                RequireRegistration()
)
async def user_profile_handler(message: Message):
    keyboard = ProfileKeyboard()
    markup = keyboard.markup()
    query_result = await select_query("SELECT * FROM Participant"
                                " WHERE user_id={user_id};".format(user_id=message.from_user.id))
    tg_id, tg_username, join_date, rep_points, *_ = query_result[0]
    await message.reply(
        ShowProfileInfoPhrases.basic_template.format(user_id=tg_id, username=tg_username,
                                rep_points=rep_points, join_date=join_date.strftime("%d/%m/%Y")),
                        reply_markup=markup)


@router.callback_query(
    StateFilter(None),
    ShowMyChallengesCB.filter(),
    RequireRegistration(),
    PrivateMessagesScope()
)
async def show_list_of_challenges(callback: aiogram.types.CallbackQuery):
    pass

