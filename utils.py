import datetime
import logging
from functools import partial
from uuid import uuid4

import aiogram
from aiogram.exceptions import TelegramForbiddenError

from bot_types import ActiveChallengeParticipant
from strings import DatetimeEndings


def get_ending(time_measure: int, time_measure_key: str):
    endings = {"week": DatetimeEndings.week, "day": DatetimeEndings.days, "hour": DatetimeEndings.hours}
    source = endings.get(time_measure_key)
    if source is None:
        raise TypeError()
    if time_measure % 10 == 1:
        ending = source[0]
    elif 2 <= time_measure % 10 <= 4:
        ending = source[1]
    else:
        ending = source[2]
    return ending


def handle(async_func=None, error=None, *errors):
    if async_func is None:
        return partial(handle, error=error, *errors)
    logger = logging.getLogger(async_func.__name__ if not isinstance(async_func, partial) else async_func.func.__name__)

    async def wrapper(*args, **kwargs):
        try:
            return await async_func(*args, **kwargs)
        except (error, *errors) as exc:
            logger.error(f"{exc.__class__.__name__}: {str(exc)}")
            return None
    return wrapper


@handle(error=TelegramForbiddenError)
async def check_if_user_reachable(bot: aiogram.Bot, user: ActiveChallengeParticipant):
    return await bot.send_chat_action(chat_id=user.user_id, action="typing")


def generate_unique_id():
    return str(uuid4()).replace('-', '')


def get_timedelta(date: datetime.datetime):
    timedelta = date - datetime.datetime.now()
    seconds = timedelta.total_seconds()
    weeks = int(seconds // 604800)
    seconds -= weeks*604800
    days = int(seconds // 86400)
    seconds -= days*86400
    hours = int(seconds // 3600)
    week_ending = get_ending(weeks, "week")
    day_ending = get_ending(days, "day")
    hour_ending = get_ending(hours, "hour")
    template = f"{weeks} {week_ending} {days} {day_ending} и {hours} {hour_ending}"
    if not weeks:
        template = f"{days} {day_ending} и {hours} {hour_ending}"
        if not days:
            template = f"{hours} {hour_ending}"
            if not hours:
                template = f"Менее часа"
    elif not days:
        template = f"{hours} {hour_ending}"
        if not hours :
            template = f"Менее часа"
    return template