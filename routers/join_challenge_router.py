import logging

import aiogram
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from bot_types import ChatTypes, ActiveChallenge, ActiveChallengeParticipant
from callback_data import AcceptParticipantCB, RejectParticipantCB, BanParticipantFromJoiningCB
from db import ChallengeDB
from filters import PrivateMessageScope
from fsm_states import JoiningChallengeStates
from keyboard_styles.keyboards import GetBackKeyboard, AcceptOrRejectKeyboard
from middlewares.authmiddleware import CatchAiogramErrorMiddleware
from queries import select_challenge_by_code, is_user_joined, prevent_user_from_joining, check_if_user_can_join
from routers.new_challenge_router import get_to_main_menu
from strings import MainMenuButtonNames, JoiningChallengeMessages, accept_message, WaitingForCodeMessage
from utils import check_if_user_reachable

private_join_router = Router(name=f"{__name__}_private")
group_join_router = Router(name=f"{__name__}_public")

logger = logging.getLogger(private_join_router.name)

private_join_router.message.filter(PrivateMessageScope())
private_join_router.callback_query.filter(PrivateMessageScope())
private_join_router.callback_query.middleware(CatchAiogramErrorMiddleware(logger))
private_join_router.message.middleware(CatchAiogramErrorMiddleware(logger))
group_join_router.message.filter(F.chat.type.in_({ChatTypes.GROUP, ChatTypes.SUPERGROUP}))


@private_join_router.message(
    StateFilter(None),
    F.text.capitalize() == MainMenuButtonNames.join_current
)
async def join_existing_challenge_handler(message: Message, state: FSMContext):
    markup = GetBackKeyboard().markup()
    await message.reply(JoiningChallengeMessages.enter_host_id, reply_markup=markup)
    await state.set_state(JoiningChallengeStates.waiting_for_entrance_code)


@private_join_router.callback_query(
    BanParticipantFromJoiningCB.filter()
)
async def prevent_user_from_joining_challenge_handler(
        callback: aiogram.types.CallbackQuery,
        callback_data: BanParticipantFromJoiningCB
):
    with ChallengeDB() as conn:
        await conn.execute(
            prevent_user_from_joining.format(
                initiator_id=callback.from_user.id,
                receiver_id=callback_data.receiver
            ),
            autocommit=True
        )
    await callback.message.edit_text("Пользователь успешно заблокирован!")
    await callback.message.delete_reply_markup()


@private_join_router.callback_query(
    AcceptParticipantCB.filter()
)
async def accept_participant_callback_handler(
        callback: aiogram.types.CallbackQuery, callback_data: AcceptParticipantCB, bot: aiogram.Bot):
    with ChallengeDB() as conn:
        await conn.execute(
            "INSERT INTO ChallengeParticipant (user_id, challenge_id, is_kicked) VALUES "
            "({user_id}, {challenge_id}, 'f');".format(user_id=callback_data.user_id,
                                                       challenge_id=callback_data.active_challenge_id),
            autocommit=True
        )
    if not await check_if_user_reachable(
            bot,
            ActiveChallengeParticipant(user_id=callback_data.user_id,
                                                       challenge_id=callback_data.active_challenge_id)
    ):
        logger.info(f"{callback_data.user_id} is not reachable. Doing nothing..")
        return
    user_credentials = f'@{callback.from_user.username}' if callback.from_user.username else str(callback.from_user.id)
    await bot.send_message(callback_data.user_id,
                           text=f"Заявка на вступление в челлендж одобрена {user_credentials}!")
    await callback.message.edit_text(
        text="Пользователь принят в челлендж!"
    )
    await callback.message.delete_reply_markup()


@private_join_router.callback_query(
    RejectParticipantCB.filter()
)
async def reject_participant_callback_handler(
        callback: aiogram.types.CallbackQuery
):
    await callback.message.edit_text(f"Заявка отклонена")
    await callback.message.delete_reply_markup()


@private_join_router.message(
    JoiningChallengeStates.waiting_for_entrance_code
)
async def receiving_code(message: Message, bot: aiogram.Bot, state: FSMContext):
    with ChallengeDB() as conn:
        active_challenge = await conn.select(
            select_challenge_by_code.format(join_code=message.text)
        )
        if not active_challenge:
            await message.reply(WaitingForCodeMessage.invalid_code)
            return

        challenge = ActiveChallenge(*active_challenge[0])
        if await conn.select(
                check_if_user_can_join.format(
                    initiator_id=challenge.owner_id,
                    receiver_id=message.from_user.id
                )):
            await message.answer(WaitingForCodeMessage.unable_to_join_challenge)
            return

        if await conn.select(is_user_joined.format(
                user_id=message.from_user.id,
                challenge_id=challenge.active_challenge_id
        )):
            await message.reply(WaitingForCodeMessage.already_joined)
            return

        markup = AcceptOrRejectKeyboard(
            message.from_user.id,
            challenge.active_challenge_id
        ).markup()

        if not await check_if_user_reachable(
                bot,
                ActiveChallengeParticipant(user_id=challenge.owner_id, challenge_id=challenge.challenge_id)):
            await message.answer(WaitingForCodeMessage.author_unreachable)
            return
        await bot.send_message(challenge.owner_id,
                               text=accept_message.format(title=challenge.title,
                                                        username=f"@{message.from_user.username}"
                                                    if message.from_user.username else message.from_user.id),
                               reply_markup=markup, parse_mode=ParseMode.HTML)
        await message.answer(WaitingForCodeMessage.request_sent)
        await get_to_main_menu(message, state)


