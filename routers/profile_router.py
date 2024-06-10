import datetime
from dataclasses import dataclass
from pprint import pprint

import aiogram.types
from aiogram.types import Message
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.utils.formatting import Text
from middlewares import RequireRegistrationMiddleware
import queries
from bot_types import UserChallenge
from callback_data import ShowMyChallengesCB, LoadNextUserChallengePageCB, LoadPreviousUserChallengePageCB
from db import select_query
from keyboard_styles import ProfileKeyboard
from filters import RequireRegistration, PrivateMessagesScope
from keyboard_styles.keyboards import UserChallengesPaginationKeyboard
from strings import ShowProfileInfoPhrases, ChallengeListTemplates, DatetimeEndings, MainMenuButtonNames
from utils import get_timedelta


router = Router(name='ProfileRouter')
router.message.middleware(RequireRegistrationMiddleware())


@router.message(
    F.text.capitalize() == MainMenuButtonNames.my_profile,
    PrivateMessagesScope()
)
async def user_profile_handler(message: Message):
  #  keyboard = ProfileKeyboard()
  #  markup = keyboard.markup()
    query_result = await select_query("SELECT * FROM Participant"
                                " WHERE user_id={user_id};".format(user_id=message.from_user.id))
    tg_id, tg_username, join_date, rep_points, *_ = query_result[0]
    await message.reply(
        ShowProfileInfoPhrases.basic_template.format(user_id=tg_id, username=tg_username,
                                rep_points=rep_points, join_date=join_date.strftime("%d/%m/%Y")))


@router.callback_query(
    LoadNextUserChallengePageCB.filter(),
    PrivateMessagesScope()
)
@router.callback_query(
    LoadPreviousUserChallengePageCB.filter(),
    PrivateMessagesScope()
)
async def load_nex_previous_user_active_challenges_pages_handler(callback: aiogram.types.CallbackQuery, callback_data: LoadNextUserChallengePageCB):
    offset, total = callback_data.offset, callback_data.total
    query = queries.select_challenges_query.format(user_id=callback.from_user.id, offset=offset)
    challenges = await select_query(query)
    challenges = list(map(lambda tup: UserChallenge(*tup), challenges))
    templates = []
    for challenge in challenges:
        templates.append(ChallengeListTemplates(
            title=challenge.title,
            description=challenge.description,
            username=str(challenge.owner_id),
            time_delta=get_timedelta(challenge.end_date)
        ).toText())
    markup = UserChallengesPaginationKeyboard(offset=offset, total_challenges=total).markup()
    await callback.message.edit_text(**(Text(*templates).as_kwargs()))
    await callback.message.edit_reply_markup(reply_markup=markup)


@router.message(
    F.text.capitalize() == MainMenuButtonNames.my_challenges,
    PrivateMessagesScope()
)
async def show_list_of_challenges(message: Message):
    query = queries.select_challenges_query.format(user_id=message.from_user.id, offset=0)
    challenges = await select_query(query)
    if not challenges:
        return

    total_user_challenges = queries.total_user_challenges.format(user_id=message.from_user.id)
    total_count = (await select_query(total_user_challenges))[0][0]
    markup = UserChallengesPaginationKeyboard(offset=0, total_challenges=total_count).markup()

    challenges = list(map(lambda tup: UserChallenge(*tup), challenges))
    owner_username = await select_query(queries.select_username_by_id.format(
        user_id=challenges[0].owner_id
    ))
    templates = []
    for challenge in challenges:
        templates.append(ChallengeListTemplates(
            title=challenge.title,
            description=challenge.description,
            username=owner_username[0][0],
            time_delta=get_timedelta(challenge.end_date)
        ).toText())
    await message.answer(**Text(*templates).as_kwargs(), reply_markup=markup)





