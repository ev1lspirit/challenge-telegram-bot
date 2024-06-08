import logging
from configparser import ConfigParser
import re
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
import asyncio
from db import select_query
from validators import is_user_registered
from bot_types import ChatTypes

__all__ = ["SpecialRegisterFilter", "RequireAdmin", "RequireRegistration",
           "PrivateMessagesScope"]


class SpecialRegisterFilter(Filter):
    def __init__(self, command_list: set[int]):
        self.command_list = command_list

    async def __call__(self, message: Message) -> bool:
        msg = re.split(r"[,.!?><&*^$]", message.text)
        return hash("".join(msg)) in self.command_list

class RequireAdmin(Filter):
    __authcfgfile = ConfigParser()

    def __init__(self):
        self.__authcfgfile.read(r"C:\Users\11\Desktop\challenge-bot\UltimateChallengeBot\routers\filters\authcfg.ini")
        self.admin_id = self.__authcfgfile.getint("admin", "id")

    async def __call__(self, message: Message):
        if message.from_user.id == self.admin_id:
            return True
        await message.reply("Недостаточно прав для выполнения команды!")
        return False


class RequireRegistration(Filter):

    async def __call__(self, message: Message):
        loop = asyncio.get_event_loop()
        is_registered = await loop.run_in_executor(None, is_user_registered, message.from_user.id, message.from_user.username)
        if isinstance(message, CallbackQuery):
            message = message.message
        if not is_registered:
            await message.reply("Зарегистрирутесь в боте, чтобы получить доступ к челленджам")
        return is_registered


class PrivateMessagesScope(Filter):

    async def __call__(self, message: Message):
        if isinstance(message, CallbackQuery):
            return message.message.chat.type == ChatTypes.PRIVATE
        return message.chat.type == ChatTypes.PRIVATE


class LessThanTenChallengesFilter(Filter):

    async def __call__(self, message: Message):
        query = '''SELECT COUNT(owner_id) FROM ActiveChallenge;'''
        logging.info("LessThanTenChallengesFilter SELECT: selecting count(owner_id) from ActiveChallenge")
        count = await select_query(query)
        if count:
            logging.info("LessThanTenChallengesFilter SELECT successfull: result %d" % count[0][0])
            return count[0][0] <= 10
        return False

