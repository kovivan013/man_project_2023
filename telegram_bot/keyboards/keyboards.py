from aiogram.types import (
    KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
)
from typing import Union
from dataclasses import dataclass
import datetime


def default_reply_keyboard(one_time_keyboard: bool = True,
                           resize_keyboard: bool = True,
                           row_width: int = 2):
    return ReplyKeyboardMarkup(
        one_time_keyboard=one_time_keyboard,
        resize_keyboard=resize_keyboard,
        row_width=row_width
    )


def default_inline_keyboard(row_width: int = 2):
    return InlineKeyboardMarkup(
        row_width=row_width
    )


@dataclass(frozen=True)
class YesOrNo:

    yes: str = f"✅ Так"
    no: str = f"❌ Ні"
    cancel: str = f"🛑 Скасувати"
    skip: str = f"▶▶ Пропустити"
    save: str = f"📁 Зберегти"
    next: str = "Далі ↪️"

    yes_callback: str = f"yes_callback"
    no_callback: str = f"no_callback"
    cancel_callback: str = f"cancel_callback"
    skip_callback: str = f"skip_callback"
    save_callback: str = f"save_callback"
    next_callback: str = "next_callback"

    @classmethod
    def keyboard(cls, is_inline_keyboard: bool = False):

        reply_keyboard = default_reply_keyboard()
        inline_keyboard = default_inline_keyboard()

        yes_data: dict = {
            "text": cls.yes,
            "callback_data": cls.yes_callback
        }

        no_data: dict = {
            "text": cls.no,
            "callback_data": cls.no_callback
        }

        if is_inline_keyboard:
            inline_keyboard.add(
                InlineKeyboardButton(**yes_data),
                InlineKeyboardButton(**no_data)
            )

            return inline_keyboard

        reply_keyboard.add(
            KeyboardButton(**yes_data),
            KeyboardButton(**no_data)
        )

        return reply_keyboard

    @classmethod
    def cancel_keyboard(cls, is_inline_keyboard: bool = False):

        reply_keyboard = default_reply_keyboard()
        inline_keyboard = default_inline_keyboard()

        cancel_data: dict = {
            "text": cls.cancel,
            "callback_data": cls.cancel_callback
        }

        if is_inline_keyboard:
            inline_keyboard.add(
                InlineKeyboardButton(**cancel_data)
            )

            return inline_keyboard

        reply_keyboard.add(
            KeyboardButton(**cancel_data)
        )

        return reply_keyboard

    @classmethod
    def skip_keyboard(cls, is_inline_keyboard: bool = False):

        reply_keyboard = default_reply_keyboard()
        inline_keyboard = default_inline_keyboard()

        skip_data: dict = {
            "text": cls.skip,
            "callback_data": cls.skip_callback
        }

        if is_inline_keyboard:
            inline_keyboard.add(
                InlineKeyboardButton(**skip_data)
            )

            return inline_keyboard

        reply_keyboard.add(
            KeyboardButton(**skip_data)
        )

        return reply_keyboard


@dataclass(frozen=True)
class Controls:
    # TODO: Controls Menu Param types: [LIST, DICT, TUPLE]

    forward: str = f"Вперед ▶"
    backward: str = f"◀ Назад"
    close: str = f"Зачинити ✖"

    short_forward: str = f"▶"
    short_backward: str = f"◀"

    forward_callback: str = f"forward_control_callback"
    backward_callback: str = f"backward_control_callback"
    close_callback: str = f"close_control_callback"


@dataclass(frozen=True)
class Filters:

    dashboard_callback: str = f"dashboard_filter_callback"

    @classmethod
    def dashboard_filter(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(row_width=1)

        by_active: str = "Активні оголошення (0) ▼"

        keyboard.add(
            InlineKeyboardButton(text=by_active,
                                 callback_data=cls.dashboard_callback)
        )

        return keyboard


@dataclass(frozen=True)
class DropdownMenu:
    # будет 3 вида вида выпадающих меню для фильтров (active option с галочкой)
    #
    # такого же типа с галочкой, но для меню без показа количества найденных вариантов по фильтру
    #
    # режим select (можно выбрать несколько вариантов чего-то например для удаления)

    # TODO: Возможно уберу, поскольку это в тексте сообщения + На пк - лучше как сейчас, на телефона и так и так

    filters_sign: str = f"Оберіть необхідний фільтр ✅"
    menu_sign: str = f"Оберіть необхідне меню 💻"
    select_sign: str = f"Оберіть потрібні варіанти 🔑"

    callback_data: str = f"none"

    @classmethod
    def placeholder_menu(cls, current_menu: dict):
        keyboard = default_inline_keyboard(row_width=2)

        keyboard.add(
            InlineKeyboardButton(text=f"↩ На головну",
                                 callback_data="change_mode"),
            InlineKeyboardButton(text=f"Режим 🔦",
                                 callback_data="change_mode"),
            InlineKeyboardButton(**current_menu)
        )

        return keyboard

    @classmethod
    def menu_keyboard(cls, buttons: list) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(row_width=2)

        # keyboard.add(
        #     InlineKeyboardButton(text=cls.menu_sign,
        #                          callback_data=cls.callback_data)
        # )

        for i in buttons:
            for data in i:
                keyboard.insert(
                    InlineKeyboardButton(**data)
                )

        return {"inline_keyboard": buttons}

# TODO: Нужно разделить на 2 класса потерявшего и нашедшего, буду смотреть по ситуации
@dataclass(frozen=True)
class Navigation:

    # general buttons
    settings: str = f"Налаштування ⚙️"
    profile: str = f"Мій Профіль 👤"
    gigs: str = f"Оголошення 🗞️"

    #finder buttons
    dashboard: str = f"Панель Детектива 🔦"

    # seeker buttons
    marketplace: str = f"Маркетплейс 🔎"

    @classmethod
    def finder_keyboard(cls) -> Union[ReplyKeyboardMarkup]:
        reply_keyboard = default_reply_keyboard(row_width=2, one_time_keyboard=False)

        reply_keyboard.add(
            KeyboardButton(text=cls.dashboard),
            KeyboardButton(text=cls.profile),
            KeyboardButton(text=cls.gigs),
            KeyboardButton(text=cls.settings)
        )

        return reply_keyboard

    @classmethod
    def seeker_keyboard(cls) -> Union[ReplyKeyboardMarkup]:
        pass


class MyProfile:

    def __init__(self):
        self.info_about: str = f"Про себе 🔓"
        self.gigs: str = f"Мої оголошення 📰"

        self.info_about_callback: str = f"info_about_callback"
        self.gigs_callback: str = f"gigs_callback"


    update: str = f"🖊 Змінити"
    share: str = f"🔗 Поділитися"

    update_callback: str = f"🖊 Змінити"
    share_callback: str = f"🔗 Поділитися"

    @classmethod
    def info_about_keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(row_width=1)

        keyboard.add(
            InlineKeyboardButton(text=cls.update,
                                 callback_data=cls.update_callback),
            InlineKeyboardButton(text=cls.share,
                                 callback_data=cls.share_callback)
        )

        return keyboard


class UpdateProfile(Controls, YesOrNo):

    def __init__(self):
        self.username: str = f"✏️ Нікнейм"
        self.description: str = f"📝 Опис"

        self.username_callback: str = f"username_callback"
        self.description_callback: str = f"description_callback"

    @classmethod
    def keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(row_width=1)

        keyboard.add(
            InlineKeyboardButton(text=cls.backward,
                                 callback_data=cls.backward_callback)
        )

        return keyboard

    @classmethod
    def base_keyboard(cls, with_save: bool = True) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(text=cls.backward,
                                 callback_data=cls.backward_callback)
        )
        if with_save:
            keyboard.insert(
                InlineKeyboardButton(text=cls.save,
                                     callback_data=cls.save_callback)
            )

        return keyboard

class CreateGigMenu(YesOrNo):

    @classmethod
    def keyboard(cls, with_next: bool = False, with_skip: bool = False):
        keyboard = default_inline_keyboard(row_width=3)

        keyboard.add(
            InlineKeyboardButton(text=cls.cancel,
                                 callback_data=cls.cancel_callback)
        )
        if with_next:
            keyboard.insert(
                InlineKeyboardButton(text=cls.next,
                                     callback_data=cls.next_callback)
            )
        if with_skip:
            keyboard.insert(
                InlineKeyboardButton(text=cls.skip,
                                     callback_data=cls.skip_callback)
            )

        return keyboard


class CalendarMenu(Controls, YesOrNo):

    short_days: list = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "НД"]
    days: list = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
    months: dict = {1: {"month": "Січень", "days": 31}, 2: {"month": "Лютий", "days": 28},
                    3: {"month": "Березень", "days": 31}, 4: {"month": "Квітень", "days": 30},
                    5: {"month": "Травень", "days": 31}, 6: {"month": "Червень", "days": 30},
                    7: {"month": "Липень", "days": 31}, 8: {"month": "Серпень", "days": 31},
                    9: {"month": "Вересень", "days": 30}, 10: {"month": "Жовтень", "days": 31},
                    11: {"month": "Листопад", "days": 30}, 12: {"month": "Грудень", "days": 31}
    }

    now: str = f"🗓️ Зараз"

    date_callback: str = f"_date_callback"

    @classmethod
    def keyboard(cls, with_cancel: bool = False, with_save: bool = False, with_forward: bool = True,
                 year: int = None, month: int = None, day: int = None) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(row_width=7)

        args = all([year, month, day])

        if args:
            today = datetime.datetime(year, month, day)
        else:
            today = datetime.datetime.now()

        now = datetime.datetime.now()
        firts_month_day = datetime.datetime(today.year, today.month, 1)
        weekday = firts_month_day.weekday()
        days_to_end = 7 - weekday
        days_in_month = cls.months[today.month]["days"]

        day = 1

        if today.year % 4 == 0 and today.month == 2:
            days_in_month = 29

        r = 6

        if days_in_month - days_to_end - 28 > 0:
            r+=1

        keyboard.add(
            InlineKeyboardButton(text=f"{cls.months[today.month]['month']}, {today.year}",
                                 callback_data="None")
        )

        keyboard.add(
            InlineKeyboardButton(text=cls.short_backward,
                                 callback_data=cls.backward_callback)
        )

        if with_forward:
            keyboard.insert(
                InlineKeyboardButton(text=cls.short_forward,
                                     callback_data=cls.forward_callback)
            )

        days = []
        for short_day in cls.short_days:
            days.append(
                InlineKeyboardButton(
                    text=short_day,
                    callback_data="None"
                )
            )

        keyboard.row(*days)

        for i in range(1, r):
            for j in range(1, 8):
                if day > days_in_month or (i<2 and j < weekday + 1):
                    keyboard.insert(
                        InlineKeyboardButton(
                            text=" ",
                            callback_data="None"
                        )
                    )
                    continue
                callback = int(datetime.datetime(today.year,
                                                 today.month,
                                                 day).timestamp())
                keyboard.insert(
                    InlineKeyboardButton(
                        text=f"{day}",
                        callback_data=f"{callback}{cls.date_callback}"
                    )
                )
                day += 1

        keyboard.add(
            InlineKeyboardButton(text=cls.now,
                                 callback_data=f"now{cls.date_callback}"
            )
        )

        if with_cancel:
            keyboard.add(
                InlineKeyboardButton(text=cls.cancel,
                                     callback_data=cls.cancel_callback)
            )
            if with_save:
                keyboard.insert(
                    InlineKeyboardButton(text=cls.next,
                                         callback_data=cls.next_callback)
                )


        return keyboard

