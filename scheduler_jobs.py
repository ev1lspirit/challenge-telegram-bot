import datetime
import logging
from collections import defaultdict
from os import getenv
from pprint import pprint

import aiogram
import typing as tp

from aiogram.enums import ParseMode

import queries
from db import select_query, insert
from bot_types import ActiveChallenge, ActiveChallengeParticipant
from db.dbconnector import BaseConnectionState, ChallengeDB
from strings import ExpiredChallengeMessageTemplate
from aiogram.methods.send_chat_action import SendChatAction


async def check_if_user_reachable(bot: aiogram.Bot, user: ActiveChallengeParticipant):
    try:
        return await bot.send_chat_action(chat_id=user.user_id, action="typing")
    except Exception as exc:
        logging.error(str(exc))
        return False


async def send_notification_expired_challenge_participants(
        bot: aiogram.Bot,
        expired_challenges: tp.Tuple[ActiveChallenge],
        user_list: tp.Tuple[ActiveChallengeParticipant]):
    for user in user_list:
        if not await check_if_user_reachable(bot, user):
            continue
        challenges = filter(lambda challenge: user.challenge_id == challenge.active_challenge_id, expired_challenges)
        for challenge in challenges:
            await bot.send_message(chat_id=user.user_id, text=ExpiredChallengeMessageTemplate(challenge).toText(),
                                   parse_mode=ParseMode.HTML)


async def check_for_expired_challenges(*, bot: aiogram.Bot):
    query = queries.select_expired_challenges.format(
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    with ChallengeDB() as conn:
        expired_challenge_records = await conn.select(query)
        logging.info(expired_challenge_records)
        challenges = tuple(map(lambda record: ActiveChallenge(*record), expired_challenge_records))
        if not challenges:
            return
        expired_participants_query = queries.select_expired_participants.format(
            challenge_list=",".join(str(record.active_challenge_id) for record in challenges)
        )
        expired_challenge_participants= await conn.select(expired_participants_query)
        participants = tuple(map(lambda record: ActiveChallengeParticipant(*record), expired_challenge_participants))
        delete_active_transaction = queries.delete_expired_challenges_transaction.format(
            challenge_id_list=",".join(map(str, (challenge.active_challenge_id for challenge in challenges)))
        )
        res = await conn.execute(delete_active_transaction, autocommit=True)
        logging.info(f"Executed {delete_active_transaction} with result {res}")
    await send_notification_expired_challenge_participants(bot, challenges, participants)





