from aiogram.dispatcher.middlewares.base import BaseMiddleware
import typing as tp
import queries
from aiogram.types import TelegramObject, CallbackQuery, Message
from db import select_query, add_user_to_bot


class RequireRegistrationMiddleware(BaseMiddleware):

    @staticmethod
    async def check_if_registered(user_id: int) -> bool:
        query = queries.check_if_registered_query.format(user_id=user_id)
        return True if await select_query(query) else False

    async def  __call__(self, handler: tp.Callable[
        [TelegramObject, tp.Dict[str, tp.Any]], tp.Awaitable[tp.Any]], event: Message,
                        data: tp.Dict[str, tp.Any]) -> tp.Any:
        if not await self.check_if_registered(event.from_user.id):
            await add_user_to_bot(user_id=event.from_user.id, username=event.from_user.username)
        return await handler(event, data)