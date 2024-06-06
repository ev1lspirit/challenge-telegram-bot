import aiogram.types
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

import strings
from callback_data import CreateUserOwnChallengeCB, ChallengeDurationCBData
from fsm_states import ChallengeCreationStates
from keyboard_styles import ChallengeDurationKeyboard
from keyboard_styles.keyboards import ExitBackToMainMenuButton, MainMenuKeyboard
from strings import CreateNewChallengeMessages, ChallengeDurationPhrases

router = Router(name=__name__)




@router.callback_query(
    CreateUserOwnChallengeCB.filter(),
    ChallengeCreationStates.choosing_challenge
)
async def create_own_challenge_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ChallengeCreationStates.choosing_challenge_title)
    markup = ExitBackToMainMenuButton().markup()
    await callback.message.delete_reply_markup()
    await callback.message.answer(text=CreateNewChallengeMessages.enter_title, reply_markup=markup)


@router.message(
    ChallengeCreationStates.choosing_challenge_title,
    F.text.capitalize() != "Назад в главное меню"
)
async def set_challenge_title_handler(message: Message, state: FSMContext):
    if not (6 <= len(message.text) < 70):
        await message.reply(text=CreateNewChallengeMessages.not_sized_title)
        return
    await message.reply(text=CreateNewChallengeMessages.enter_description)
    await state.set_state(ChallengeCreationStates.setting_challenge_description)
    await state.set_data({"title": message.text})


@router.message(
    ChallengeCreationStates.setting_challenge_description,
    F.text.capitalize() != "Назад в главное меню",
)
async def set_challenge_description(message: Message, state: FSMContext):
    if not (6 <= len(message.text) < 170):
        await message.reply(text=CreateNewChallengeMessages.not_sized_description)
        return
    markup = ChallengeDurationKeyboard().markup(include_back=False)
    await message.reply(text=ChallengeDurationPhrases.question, reply_markup=markup)
    title = (await state.get_data()).pop("title")
    await state.set_state(ChallengeCreationStates.choosing_challenge_length)
    await state.set_data({"title": title, "desc": message.text})


@router.message(
    F.text.capitalize() == "Назад в главное меню",
    StateFilter(
                ChallengeCreationStates.setting_challenge_description,
                ChallengeCreationStates.choosing_challenge_title)
)
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    markup = MainMenuKeyboard().markup()
    markup.resize_keyboard = True
    await message.answer(text="Создание челленджа отменено")
    await message.answer(text=strings.BotMenus.main_menu, reply_markup=markup)