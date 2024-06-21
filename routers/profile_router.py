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
from db import select_query, ChallengeDB
from filters import RequireRegistration, PrivateMessagesScope
from keyboard_styles.keyboards import UserChallengesPaginationKeyboard
from strings import ShowProfileInfoPhrases, ChallengeListTemplates, DatetimeEndings, MainMenuButtonNames
from utils import get_timedelta


router = Router(name='ProfileRouter')
router.message.middleware(RequireRegistrationMiddleware())
router.callback_query.filter(PrivateMessagesScope())


@router.message(
    F.text.capitalize() == MainMenuButtonNames.my_profile,
)
@router.message(
    Command("profile")
)
async def user_profile_handler(message: Message):
    query_result = await select_query("SELECT * FROM Participant"
                                " WHERE user_id={user_id};".format(user_id=message.from_user.id))
    tg_id, tg_username, join_date, rep_points, *_ = query_result[0]
    await message.reply(
        ShowProfileInfoPhrases.basic_template.format(user_id=tg_id, username=tg_username,
                                rep_points=rep_points, join_date=join_date.strftime("%d/%m/%Y")))


@router.callback_query(
    LoadNextUserChallengePageCB.filter(),
)
@router.callback_query(
    LoadPreviousUserChallengePageCB.filter()
)
async def load_nex_previous_user_active_challenges_pages_handler(callback: aiogram.types.CallbackQuery, callback_data: LoadNextUserChallengePageCB):
    offset, total = callback_data.offset, callback_data.total
    query = queries.select_challenges_query.format(user_id=callback.from_user.id, offset=offset)
    with ChallengeDB() as conn:
        challenges = await conn.select(query)
        challenges = list(map(lambda tup: UserChallenge(*tup), challenges))
        challenge_owner_ids = map(lambda challenge: str(challenge.owner_id), challenges)
        owner_usernames: dict[int, str] = dict(await conn.select(queries.select_username_by_id.format(
        id_list=",".join(dict.fromkeys(challenge_owner_ids))
        )))

    templates = []
    for challenge in challenges:
        username = owner_usernames.get(challenge.owner_id)
        templates.append(ChallengeListTemplates(
            title=challenge.title,
            description=challenge.description,
            username=challenge.owner_id if username is None else f"@{username}",
            time_delta=get_timedelta(challenge.end_date)
        ).toText())
    markup = UserChallengesPaginationKeyboard(offset=offset, total_challenges=total).markup()
    await callback.message.edit_text(**(Text(*templates).as_kwargs()), reply_markup=markup)

@router.message(
    F.text.capitalize() == MainMenuButtonNames.my_challenges,
    PrivateMessagesScope()
)
async def show_list_of_challenges(message: Message):
    query = queries.select_challenges_query.format(user_id=message.from_user.id, offset=0)

    with ChallengeDB() as conn:
        challenges = await conn.select(query)
        if not challenges:
            await message.answer("Челленджей не найдено :(")
            return
        total_user_challenges = queries.total_user_challenges.format(user_id=message.from_user.id)
        total_count = (await conn.select(total_user_challenges))[0][0]
        markup = UserChallengesPaginationKeyboard(offset=0, total_challenges=total_count).markup()

        challenges = list(map(lambda tup: UserChallenge(*tup), challenges))
        challenge_owner_ids = map(lambda challenge: str(challenge.owner_id), challenges)
        owner_usernames = dict(await conn.select(queries.select_username_by_id.format(
            id_list=",".join(dict.fromkeys(challenge_owner_ids))
        )))

    templates = []
    for challenge, owner_username in zip(challenges, map(lambda challenge: challenge.username, challenges)):
        username = owner_usernames.get(challenge.owner_id)
        templates.append(ChallengeListTemplates(
            title=challenge.title,
            description=challenge.description,
            username=challenge.owner_id if username is None else f"@{username}",
            time_delta=get_timedelta(challenge.end_date)
        ).toText())
    await message.answer(**Text(*templates).as_kwargs(), reply_markup=markup)





