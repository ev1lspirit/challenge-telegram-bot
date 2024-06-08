import logging

from aiogram import F, Router
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, IS_NOT_MEMBER, MEMBER
from aiogram.types import ChatMemberUpdated
from bot_types import ChatTypes
from keyboard_styles import StartKeyboard
from strings import SupergroupStartPhrases

router = Router(name=__name__)
router.my_chat_member.filter(F.chat.type.in_({ChatTypes.GROUP, ChatTypes.SUPERGROUP}))


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=
                            IS_NOT_MEMBER >> MEMBER)
)
async def handle_adding_bot_to_group(event: ChatMemberUpdated):
    keyboard = StartKeyboard()
    logging.info(event.old_chat_member.status)
    markup = keyboard.markup()
    reply_phrase = SupergroupStartPhrases.basic_template
    await event.answer(
        text=reply_phrase
    )

