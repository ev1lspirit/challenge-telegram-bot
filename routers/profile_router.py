import datetime
from dataclasses import dataclass
from pprint import pprint

import aiogram.types
from aiogram.types import Message
from aiogram import Router
from aiogram.filters import Command, StateFilter

import queries
from callback_data import ShowMyChallengesCB
from db import select_query
from keyboard_styles import ProfileKeyboard
from filters import RequireRegistration, PrivateMessagesScope
from strings import ShowProfileInfoPhrases, ChallengeListTemplates, DatetimeEndings
from utils import get_timedelta

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


@dataclass
class UserChallenge:
    title: str
    description: str
    owner_id: int
    end_date: datetime.datetime


@router.message(
    Command('challenge')
)
async def show_list_of_challenges(message: aiogram.types.CallbackQuery):
    query = queries.select_challenges_query.format(user_id=message.from_user.id)
    challenges = await select_query(query)
    if not challenges:
        return
    challenges = list(map(lambda tup: UserChallenge(*tup), challenges))
    owner_username = await select_query(queries.select_username_by_id.format(user_id=challenges[0].owner_id))

    templates = []
    for challenge in challenges:
        templates.append(ChallengeListTemplates.template.format(
            username=owner_username[0][0],
            description=challenge.description,
            challenge_title=challenge.title,
            time_delta=get_timedelta(challenge.end_date)
        ))

    await message.answer(text="\n".join(templates))





