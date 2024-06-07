import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder, KeyboardBuilder
from aiogram.types.keyboard_button import KeyboardButton

import strings
from callback_data import *
from commands import StartCallbackQueryCommands as StartCQC
from strings import ChallengeDurationPhrases
import abc
import typing as tp
from strings import (
    ExistingOrNewChallengeButtonNames as EoNButtonNames,
    MainMenuButtonNames as MMBNames
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
        about_button = KeyboardButton(text="Про наш бот", callback_data=StartCQC.HELP.value)
        new_challenge_button = KeyboardButton(text=MMBNames.new_challenge)
        join_challenge_button = KeyboardButton(text=MMBNames.join_current)
        self.builder.row(join_challenge_button, width=1)
        self.builder.row(new_challenge_button, width=1)
        register_button = KeyboardButton(text=MMBNames.help_btn)
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

class StartKeyboard(BaseKeyboard):
    def markup(self) -> InlineKeyboardMarkup:
        about_button = InlineKeyboardButton(text="Про наш бот", callback_data=StartCQC.HELP.value)
        new_challenge_button = InlineKeyboardButton(text="Создать новый челлендж",
                                                         callback_data=CreateUserOwnChallengeCB().pack())
        join_challenge_button = InlineKeyboardButton(text="Присоединиться к существующему челленджу",
            callback_data=JoinExistingChallengeCB().pack())
        self.builder.row(join_challenge_button, width=1)
        self.builder.row(new_challenge_button, width=1)
        register_button = InlineKeyboardButton(text="Помощь", callback_data=HelpButtonCB().pack())
        self.builder.row(register_button, about_button, width=2)
        return self.builder.as_markup()


class ProfileKeyboard(BaseKeyboard):

    def markup(self) -> InlineKeyboardMarkup:
        join_challenge_button = InlineKeyboardButton(text="Присоединиться к челленджу",
                                                     callback_data=StartCQC.NEW.value)
        rating_table_button = InlineKeyboardButton(text="Мои челленджи", callback_data=ShowMyChallengesCB().pack())
        self.builder.add(join_challenge_button)
        self.builder.add(rating_table_button)
        self.builder.adjust(2, 1)
        return self.builder.as_markup()


class GetBackKeyboard(BaseKeyboard):

    def markup(self, *args) -> InlineKeyboardMarkup:
        btn = InlineKeyboardButton(text="Вернуться", callback_data=GetBackCB().pack())
        self.builder.add(btn)
        return self.builder.as_markup()


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
        pages_count = InlineKeyboardButton(text=f"Страница {offset // 5 + 1}/{self.total // 5 + 1}",
                                           callback_data="some_data")

        next_action_button = None
        back_button = None

        forward_condition = not offset or self.total // offset > 1
        backward_condition = offset > 0
        if forward_condition:
            next_action_button = InlineKeyboardButton(text="Следующая страница",
                                                      callback_data=LoadNextChallengePageCB(offset=offset + 5,
                                                                                            total=self.total).pack())
        if backward_condition:
            back_button = InlineKeyboardButton(text="Назад", callback_data="ff")

        to_create = list(filter(lambda btn: btn is not None, [next_action_button, back_button]))
        print(to_create)
        self.builder.row(pages_count, *to_create, width=1+len(to_create))
        exit_creation = InlineKeyboardButton(text=strings.back_to_main_menu, callback_data=ExitChallengeSettingCB().pack())
        self.builder.row(exit_creation, width=1)
        return self.builder.as_markup()


class ChallengeDurationKeyboard(InlineTypeKeyboard):
    _saved_markup: tp.Optional[InlineKeyboardMarkup] = None

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