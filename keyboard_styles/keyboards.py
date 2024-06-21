import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder, KeyboardBuilder
from aiogram.types.keyboard_button import KeyboardButton

import strings
from callback_data import *
from strings import ChallengeDurationPhrases
import abc
import typing as tp
from strings import (
    ExistingOrNewChallengeButtonNames as EoNButtonNames,
    MainMenuButtonNames as MMBNames,
    PaginationButtonMessages
)


class BaseKeyboard(abc.ABC):
    keyboard_builder = lambda: None

    def __init__(self, *args):
        self.builder = self.keyboard_builder()

    @abc.abstractmethod
    def markup(self, *args, **kwargs) -> InlineKeyboardMarkup:
        raise NotImplementedError()


class InlineTypeKeyboard(BaseKeyboard):
    keyboard_builder = InlineKeyboardBuilder

    def markup(self, *args) -> InlineKeyboardMarkup:
        return self.builder().as_markup()


class ReplyTypeKeyboard(BaseKeyboard):
    keyboard_builder = ReplyKeyboardBuilder

    def markup(self, *args) -> ReplyKeyboardMarkup:
        return self.builder().as_markup()


class MainMenuKeyboard(ReplyTypeKeyboard):

    def markup(self):
        about_button = KeyboardButton(text=MMBNames.my_profile)
        new_challenge_button = KeyboardButton(text=MMBNames.new_challenge)
        join_challenge_button = KeyboardButton(text=MMBNames.join_current)
        self.builder.row(join_challenge_button, width=1)
        self.builder.row(new_challenge_button, width=1)
        register_button = KeyboardButton(text=MMBNames.my_challenges)
        self.builder.row(register_button, about_button, width=2)
        return self.builder.as_markup()


class ExitBackToMainMenuButton(ReplyTypeKeyboard):

    def markup(self, *args) -> ReplyKeyboardMarkup:
        exit_button = KeyboardButton(text="Назад в главное меню")
        self.builder.row(exit_button, width=1)
        markup = self.builder.as_markup()
        markup.resize_keyboard = True
        markup.is_persistent = True
        return markup


class ExistingOrNewChallengeKeyboard(InlineTypeKeyboard):

    def markup(self, *args) -> InlineKeyboardMarkup:
        default_challenge_button = InlineKeyboardButton(text=EoNButtonNames.default_challenge,
                                                        callback_data=CreateDefaultChallengeCB().pack())
        own_challenge_button = InlineKeyboardButton(text=EoNButtonNames.new_challenge,
                                                    callback_data=CreateUserOwnChallengeCB().pack())
        self.builder.row(own_challenge_button, default_challenge_button, width=2)
        return self.builder.as_markup()


class GetBackKeyboard(BaseKeyboard):

    def markup(self, *args) -> InlineKeyboardMarkup:
        btn = InlineKeyboardButton(text="Вернуться", callback_data=GetBackCB().pack())
        self.builder.add(btn)
        return self.builder.as_markup()


def get_pagination_pattern(*, offset: int, total: int, callback, offset_change=5):
    pages = total // offset_change if total % offset_change == 0 else total // offset_change + 1
    pages_count = InlineKeyboardButton(text=f"Страница {offset // offset_change + 1}/{pages}",
                                       callback_data="some_data")
    if total <= offset_change:
        return pages_count,
    if offset:
        print(total, offset, total // offset)
    next_action_button = None
    back_button = None
    forward_condition = not offset or (total // offset > 1 if total != 2*offset else False)
    backward_condition = offset > 0
    if forward_condition:
        next_action_button = InlineKeyboardButton(text=PaginationButtonMessages.forward,
                                                  callback_data=callback(offset=offset + offset_change,
                                                                                        total=total).pack())
    if backward_condition:
        back_button = InlineKeyboardButton(text=PaginationButtonMessages.back,
                                           callback_data=callback(offset=offset - offset_change,
                                                                                 total=total).pack())

    to_create = list(filter(lambda btn: btn is not None, [back_button, next_action_button]))
    if len(to_create) == 2:
        result = to_create[0], pages_count, to_create[1]
    else:
        result = pages_count, to_create[0]
    return result


class SelectChallengeKeyboard(InlineTypeKeyboard):

    def __init__(self, user_id: int, button_text_list: list[tuple[int, str]], total: int):
        self.total = total
        self.user_id = user_id
        self.button_text_list = button_text_list
        super().__init__()

    @property
    def button_text_list(self):
        return self._button_text_list

    @button_text_list.setter
    def button_text_list(self, value):
        assert isinstance(value, list), "Button names must be stored in a list"
        assert value, "Button list cannot be empty"
        self._button_text_list = value

    def markup(self, offset=0) -> InlineKeyboardMarkup:
        for title in self.button_text_list:
            data = ButtonPressedCBData(button_title=title[0], user_id=self.user_id)
            btn = InlineKeyboardButton(text=title[1], callback_data=data.pack())
            self.builder.row(btn, width=1)
        pattern = get_pagination_pattern(offset=offset, total=self.total, callback=LoadNextChallengePageCB)
        self.builder.row(*pattern, width=len(pattern))
        exit_creation = InlineKeyboardButton(text=strings.back_to_main_menu, callback_data=ExitChallengeSettingCB().pack())
        self.builder.row(exit_creation, width=1)
        return self.builder.as_markup()


class UserChallengesPaginationKeyboard(InlineTypeKeyboard):

    def __init__(self, *, offset: int, total_challenges: int):
        self.total = total_challenges
        self.offset = offset
        super().__init__()

    def markup(self, *args) -> InlineKeyboardMarkup:
        pattern = get_pagination_pattern(offset=self.offset, total=self.total, callback=LoadNextUserChallengePageCB)
        self.builder.row(*pattern, width=len(pattern))
        return self.builder.as_markup()


class ChallengeDurationKeyboard(InlineTypeKeyboard):

    def markup(self, include_back=True) -> InlineKeyboardMarkup:
        one_week = InlineKeyboardButton(text=ChallengeDurationPhrases.one_week,
                                            callback_data=ChallengeDurationCBData(weeks=1).pack())
        one_month = InlineKeyboardButton(text=ChallengeDurationPhrases.one_month,
                                             callback_data=ChallengeDurationCBData(weeks=4).pack())
        two_weeks = InlineKeyboardButton(text=ChallengeDurationPhrases.two_weeks,
                                             callback_data=ChallengeDurationCBData(weeks=2).pack())
        self.builder.add(one_week)
        self.builder.add(one_month)
        self.builder.add(two_weeks)

        if include_back:
            btn = InlineKeyboardButton(text="Вернуться", callback_data=GetBackCB().pack())
            self.builder.row(btn)

        exit_btn = InlineKeyboardButton(text=strings.back_to_main_menu, callback_data=ExitChallengeSettingCB().pack())
        self.builder.row(exit_btn)
        return self.builder.as_markup()


class ChallengeSuccessfullyCreatedKeyboard(BaseKeyboard):

    def markup(self, *args) -> InlineKeyboardMarkup:
        pass


class OneButtonKeyboard(InlineTypeKeyboard):

    def __init__(self, button_text: str):
        self.button_text = button_text
        super().__init__()