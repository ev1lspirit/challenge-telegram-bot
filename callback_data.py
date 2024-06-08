from aiogram.filters.callback_data import CallbackData


class CreateNewChallengeCB(CallbackData, prefix="n-chal"):
    pass


class CreateUserOwnChallengeCB(CallbackData, prefix="o-chal"):
    pass


class LoadNextChallengePageCB(CallbackData, prefix="ld-n"):
    offset: int
    total: int


class LoadPreviousChallengePageCB(CallbackData, prefix="ld-p"):
    offset: int
    total: int


class CreateDefaultChallengeCB(CallbackData, prefix="d-chal"):
    pass


class ButtonPressedCBData(CallbackData, prefix="bdata"):
    button_title: int
    user_id: int


class ChallengeDurationCBData(CallbackData, prefix="cb-dur"):
    weeks: int


class GetBackCB(CallbackData, prefix="back-cb"):
    pass


class ExitChallengeSettingCB(CallbackData, prefix="exit-cb"):
    pass


class HelpButtonCB(CallbackData, prefix="help-b"):
    pass


class ShowMyChallengesCB(CallbackData, prefix="show-ch"):
    pass


class JoinExistingChallengeCB(CallbackData, prefix="join-c"):
    pass

