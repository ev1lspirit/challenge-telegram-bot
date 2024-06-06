from aiogram.fsm.state import StatesGroup, State


class ChallengeCreationStates(StatesGroup):
    choosing_challenge = State()
    choosing_challenge_title = State()
    setting_challenge_description = State()
    choosing_challenge_length = State()
