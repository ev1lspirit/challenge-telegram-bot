from aiogram import Router
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.types import ChatMemberUpdated
from filters import PrivateMessageScope

router = Router(name=__name__)
router.my_chat_member.filter(PrivateMessageScope())


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=IS_MEMBER >> IS_NOT_MEMBER)
)
async def user_banned_bot_handler(event: ChatMemberUpdated):
    pass
