from dataclasses import dataclass

from aiogram.utils.formatting import as_list, as_key_value, as_marked_section, Text, Bold

from emoji import emojize


bot_typedefs = ("Ботослон", "Ботяра", "Слонобот")
choose_action = "Выберите действие"
challenge_creation_menu = f'{emojize(":desktop_computer:")} Меню создания челленджа'
back_to_main_menu = emojize(':cross_mark:')


@dataclass
class PaginationButtonMessages:
    back = f"{emojize(':backhand_index_pointing_left:')} Назад"
    forward = f"Вперед {emojize(':backhand_index_pointing_right:')} "


@dataclass
class InterruptionMessages:
    challenge_interrupt_string = f"{emojize(':warning:')} Чтобы выйти из меню создания челленджа, нажмите \"Выйти в главное меню\" на клавиатуре"
    user_already_in_challenge = f"{emojize(':red_exclamation_mark:')} Вы уже состоите в данном челлендже. Пожалуйста, выберите другой"


@dataclass
class CreateNewChallengeMessages:
    enter_title = f"{emojize(':pencil:')} Введите название челленджа: "
    not_sized_title = f"{emojize(':warning:')} Длина названия должна быть в диапазоне от 6 от 70 символов."
    enter_description = f"{emojize(':pencil:')} Введите описание челленджа: "
    not_sized_description = f"{emojize(':warning:')} Длина описания должна быть в диапазоне от 6 от 170 символов."

@dataclass
class BotMenus:
    challenge_creation_menu = f'{emojize(":desktop_computer:")} Меню создания челленджа'
    main_menu = f'{emojize(":pushpin:")} Главное меню'


@dataclass
class MainMenuButtonNames:
    new_challenge = "Создать новый челлендж"
    join_current = "Присоединиться к существующему челленджу"
    help_btn = "Помощь"
    my_challenges = "Мои челленджи"
    my_profile = "Мой профиль"


@dataclass
class ExistingOrNewChallengeButtonNames:
    new_challenge = "Создать свой челлендж"
    default_challenge = "Выбрать челлендж из числа установленных"


@dataclass
class InterruptChallengeCreationStrings:
    back_to_menu = "Назад в главное меню"



@dataclass
class StartPhrases:
    basic_template: str = ("{username}, привет, слоняра! Я Челлендж-бот и я готов помочь тебе стать чуточку лучше и продуктивнее. "
                           )

@dataclass
class SupergroupStartPhrases:
    basic_template: str = """Привет, слоняры! Я Челлендж-бот и я готов помочь вам стать чуточку лучше и продуктивнее. Для того, чтобы участвовать, отправьте боту команду /register или нажмите на кнопку \"Учаcтвовать\""""


@dataclass
class ShowProfileInfoPhrases:
    basic_template: str = (emojize(":pushpin:") + " ID пользователя: {user_id}\n"
                      f'{emojize(":woman_frowning:")} ' + "Юзернейм: {username}\n"
                      f'{emojize(":calendar:")} ' + "Присоединился: {join_date}\n"
                      f'{emojize(":sports_medal:")} ' + "Репутация: {rep_points}")


class ChallengeListTemplates:
    __slots__ = "title", "description", "username", "timedelta"

    def __init__(self, title: str, description: str, username: str, time_delta: str):
        self.title = title
        self.description = description
        self.username = username
        self.timedelta = time_delta

    def toText(self):
        return as_list(
                Bold(f"{emojize(':pushpin:')} {self.title}"),
                f"{self.description}",
                as_key_value(f"   {emojize(':writing_hand:')} Автор", f"@{self.username}"),
                as_key_value(f"   {emojize(':calendar:')} Челлендж закончится через", f"{self.timedelta}"),
                "\n"
        )


@dataclass
class DatetimeEndings:
    template1 = "{weeks} {w_ending}, {days} {d_ending}, {hours} {h_ending}"
    template2 = "{days} {d_ending} и {hours} {h_ending}"
    template3 = "{hours} {h_ending}"
    week = ("Неделю", "Недели", "Недель")
    days = ("День", "Дня", "Дней")
    hours = ("Час", "Часа", "Часов")


@dataclass
class JoinChallengePhrases:
    just_joined: str = emojize(":red_heart:") + f"""Отлично! Ниже приведены челленджи, в которых ты можешь поучаствовать.
{emojize(":warning:")} Добавление своих собственных испытаний возможно только в личных сообщениях бота. Добавленные испытания видны только вам."""
    available_challenges: str = emojize(":pushpin:") + "Доступные испытания: "


@dataclass
class ChallengeDurationPhrases:
    question: str = "Как долго будет длиться челлендж?"
    one_week: str = "Одна неделя"
    two_weeks: str = "Две недели"
    one_month: str = "Один месяц"




