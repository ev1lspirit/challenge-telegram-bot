# This is a sample Python script.
import redis
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# C:\Users\11\Desktop\challenge-bot\UltimateChallengeBot\db\generate.sql

from aiogram import Bot, Dispatcher
import asyncio
from os import getenv
import logging


from routers import (
    start_router,
    user_own_challenge_creation_router,
    join_challenge_router,
    profile_router,
    special_events_router)
from db import DBInteractor


logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=getenv("BOT_TOKEN"))
dp = Dispatcher()
dp.include_router(start_router.router)
dp.include_router(join_challenge_router.router)
dp.include_router(profile_router.router)
dp.include_router(special_events_router.router)
dp.include_router(user_own_challenge_creation_router.router)


async def main():
    interactor = DBInteractor(db_user=getenv("DB_USER"), db_name=getenv("DB_NAME"), db_password=getenv("DB_PASSWORD"))
    await dp.start_polling(bot)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    asyncio.run(main())

