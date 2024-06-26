# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# C:\Users\11\Desktop\challenge-bot\UltimateChallengeBot\db\generate.sql

from aiogram import Bot, Dispatcher
from pytz import utc
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from functools import partial
import asyncio
from middlewares import RequireRegistrationMiddleware
from os import getenv
import logging

from middlewares.authmiddleware import CatchAiogramErrorMiddleware
from routers import (
    start_router,
    user_own_challenge_creation_router,
    new_challenge_router,
    profile_router,
    special_events_router,
    join_challenge_router
)
from scheduled_jobs import check_for_expired_challenges

logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=getenv("BOT_TOKEN"))
dp = Dispatcher()
dp.include_router(start_router.router)
dp.include_router(new_challenge_router.router)
dp.include_router(profile_router.router)
dp.include_router(special_events_router.router)
dp.include_router(user_own_challenge_creation_router.router)
dp.include_router(join_challenge_router.private_join_router)
dp.message.middleware(RequireRegistrationMiddleware())


aioscheduler = AsyncIOScheduler(timezone=utc)


async def main():
    expired_checker_job = partial(check_for_expired_challenges, bot=bot)
    aioscheduler.add_job(expired_checker_job, 'interval', seconds=30)
    aioscheduler.start()
    await dp.start_polling(bot)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    asyncio.run(main())


