import datetime
from middlewares import RequireRegistrationMiddleware
import aiogram.types
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
import queries
import strings
from callback_data import *
from keyboard_styles.keyboards import (ExistingOrNewChallengeKeyboard,
                                       MainMenuKeyboard)
from filters import PrivateMessagesScope
from db import select_query, insert
from strings import (
    JoinChallengePhrases,
    ChallengeDurationPhrases,
    MainMenuButtonNames as MMBNames,
    InterruptionMessages
)
from keyboard_styles import ChallengeDurationKeyboard, SelectChallengeKeyboard
from aiogram.fsm.context import FSMContext
from fsm_states import ChallengeCreationStates

router = Router(name='JoinChallengeRouter')
router.message.middleware(RequireRegistrationMiddleware())


async def get_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    markup = MainMenuKeyboard().markup()
    markup.resize_keyboard = True
    await message.answer(text=strings.BotMenus.main_menu, reply_markup=markup)


@router.message(
    F.text.capitalize() == MMBNames.new_challenge,
    StateFilter(None),
    PrivateMessagesScope()
)
async def create_new_challenge_handler(message: Message, state: FSMContext):
    await message.reply(text=strings.challenge_creation_menu, reply_markup=aiogram.types.ReplyKeyboardRemove())
    markup = ExistingOrNewChallengeKeyboard().markup()
    await message.answer(text=strings.choose_action, reply_markup=markup, protect_content=True)
    await state.set_state(ChallengeCreationStates.choosing_challenge)


@router.callback_query(
    CreateDefaultChallengeCB.filter(),
    ChallengeCreationStates.choosing_challenge,
    PrivateMessagesScope()
)
async def create_default_challenge_handler(callback: aiogram.types.CallbackQuery):
    total_challenges = await select_query(queries.select_total_challenges.format(owner_id=callback.from_user.id))
    challenge_list = await select_query(queries.select_challenges.format(user_id=callback.from_user.id, offset=0))

    markup = SelectChallengeKeyboard(callback.from_user.id, challenge_list, total_challenges[0][0]).markup()
    await callback.message.edit_text(text=f'{JoinChallengePhrases.just_joined}\n{JoinChallengePhrases.available_challenges}')
    await callback.message.edit_reply_markup(reply_markup=markup)


@router.callback_query(
    LoadNextChallengePageCB.filter(),
    ChallengeCreationStates.choosing_challenge,
    PrivateMessagesScope()
)
@router.callback_query(
    LoadPreviousChallengePageCB.filter(),
    ChallengeCreationStates.choosing_challenge,
    PrivateMessagesScope()
)
async def load_next_page_handler(callback: aiogram.types.CallbackQuery, callback_data: LoadNextChallengePageCB):
    offset = callback_data.offset
    total = callback_data.total
    button_list = await select_query(queries.select_challenges.format(user_id=callback.from_user.id,
                                                                      offset=offset))
    markup = SelectChallengeKeyboard(callback.from_user.id, button_list, total).markup(offset=offset)
    await callback.message.edit_reply_markup(reply_markup=markup)


@router.callback_query(
    ButtonPressedCBData.filter(),
    ChallengeCreationStates.choosing_challenge
)
async def challenge_chosen_handler(callback: CallbackQuery, callback_data: ButtonPressedCBData, state: FSMContext):
    challenge_id, user_id = callback_data.button_title, callback_data.user_id
    query = queries.check_if_challenge_taken.format(user_id=callback_data.user_id,
                                                    challenge_id=callback_data.button_title)
    if await select_query(query):
        await callback.message.answer(text=InterruptionMessages.user_already_in_challenge)
        return
    markup = ChallengeDurationKeyboard().markup()
    await callback.message.edit_text(text=ChallengeDurationPhrases.question)
    await callback.message.edit_reply_markup(reply_markup=markup)
    await state.set_state(ChallengeCreationStates.choosing_challenge_length)
    await state.set_data({"challenge_id": challenge_id, "user_id": user_id})


@router.callback_query(
    ChallengeDurationCBData.filter(),
    ChallengeCreationStates.choosing_challenge_length,
    PrivateMessagesScope()
)
async def add_challenge_to_the_database(callback: CallbackQuery, callback_data: ChallengeDurationCBData, state: FSMContext):
    state_data = await state.get_data()
    challenge_id, user_id = state_data.get("challenge_id"), state_data.get("user_id")

    if challenge_id is None or user_id is None:
        title, desc = state_data.pop("title"), state_data.pop("desc")
        user_id = callback.from_user.id
        query = queries.insert_new_user_challenge.format(
            owner_id=user_id,
            title=title,
            description=desc,
            creation_date=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        )
        challenge_id = await insert(query, return_last=True)

    weeks = callback_data.weeks
    current_time = datetime.datetime.now()
    challenge_end_time = current_time + datetime.timedelta(weeks=weeks)
    creation_time = current_time.strftime("%d/%m/%Y %H:%M:%S")
    end_time = challenge_end_time.strftime("%d/%m/%Y %H:%M:%S")
    print(challenge_id)
    query = queries.insert_active_transaction.format(user_id=user_id,
                                                   challenge_id=challenge_id,
                                                   creation_date=creation_time,
                                                   end_date=end_time)
    result = await insert(query)
    if result is not None:
        await callback.message.edit_text(text="Челлендж успешно создан!")
    else:
        await callback.message.edit_text(text="Что-то пошло не так")
    await get_to_main_menu(callback.message, state)


@router.callback_query(
    GetBackCB.filter(),
    ChallengeCreationStates.choosing_challenge_length
)
async def get_back_to_challenge_choice_menu_handler(callback: aiogram.types.CallbackQuery, state: FSMContext):
    await state.set_state(ChallengeCreationStates.choosing_challenge)
    await create_default_challenge_handler(callback)


@router.callback_query(
    ExitChallengeSettingCB.filter(),
    ~StateFilter(None)
)
async def exit_challenge_creation_handler(callback: aiogram.types.CallbackQuery, state: FSMContext):
    await state.clear()
    markup = MainMenuKeyboard().markup()
    markup.resize_keyboard = True
    await callback.message.answer(text=strings.BotMenus.main_menu, reply_markup=markup)
    await callback.message.edit_text(text="Создание челленджа отменено")


@router.message(
    ~StateFilter(None, ChallengeCreationStates.choosing_challenge_title,
                 ChallengeCreationStates.setting_challenge_description),
)
async def action_during_choosing_challenge_process_handler(message: Message, state: FSMContext):
    await message.reply(text=InterruptionMessages.challenge_interrupt_string)



