import logging

from aiogram import F, Router
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, IS_NOT_MEMBER, MEMBER
from aiogram.types import ChatMemberUpdated
from bot_types import ChatTypes
from strings import SupergroupStartPhrases
from keyboard_styles import MainMenuKeyboard

router = Router(name=__name__)
router.my_chat_member.filter(F.chat.type.in_({ChatTypes.GROUP, ChatTypes.SUPERGROUP}))


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=
                            IS_NOT_MEMBER >> MEMBER)
)
async def handle_adding_bot_to_group(event: ChatMemberUpdated):
    logging.info(event.old_chat_member.status)
    reply_phrase = SupergroupStartPhrases.basic_template
    await event.answer(
        text=reply_phrase
    )

