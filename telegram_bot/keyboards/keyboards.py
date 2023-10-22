from aiogram.types import (
    KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
)
from man_project_2023.telegram_bot.utils.utils import StateUtils
from typing import Union
from dataclasses import dataclass


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


class Utils:



    def get_buttons(self):
        buttons = vars(self)

        buttons_list: list = []
        for i, v in buttons.items():
            if "callback" not in i:
                buttons_list.append([{"text": v, "callback_data": buttons[i + "_callback"]}])

        return buttons_list

    def get_current_menu(self, state: str):
        keyboards = vars(self)

        return {"text": f"✅ {keyboards[state]} ▼", "callback_data": keyboards[state + "_callback"]}




@dataclass(frozen=True)
class YesOrNo:

    yes: str = f"✅ Так"
    no: str = f"❌ Ні"
    cancel: str = f"🛑 Відміна"
    skip: str = f"▶▶ Пропустити"

    yes_callback: str = f"yes_callback"
    no_callback: str = f"no_callback"
    cancel_callback: str = f"cancel_callback"
    skip_callback: str = f"skip_callback"

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
    close: str = f"Закрити ✖"

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

    filters_sign: str = f"Оберіть необхідний фільтр ✅"
    menu_sign: str = f"Оберіть необхідне меню 💻"
    select_sign: str = f"Оберіть потрібні варіанти 🔑"

    callback_data: str = f"none"

    @classmethod
    def placeholder_menu(cls, current_menu_button: dict):
        keyboard = default_inline_keyboard(row_width=1)

        keyboard.add(
            InlineKeyboardButton(**current_menu_button)
        )

        return keyboard

    @classmethod
    def menu_keyboard(cls, state: str, buttons: list) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(row_width=1)

        # keyboard.add(
        #     InlineKeyboardButton(text=cls.menu_sign,
        #                          callback_data=cls.callback_data)
        # )

        for i in buttons:
            for data in i:
                if state in data["callback_data"]:
                    data["text"] = f"✅ {data['text']}"
                keyboard.insert(
                    InlineKeyboardButton(**data)
                )

        return keyboard


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


class MyProfile(Utils):

    def __init__(self):
        self.info_about: str = f"Про себе 🔓"
        self.gigs: str = f"Мої оголошення 📰"

        self.info_about_callback: str = f"info_about_callback"
        self.gigs_callback: str = f"gigs_callback"

    placeholder_callback: str = f"placeholder_callback"

    @classmethod
    def placeholder(cls, text: str, callback_data: str = placeholder_callback) -> dict:
        return {
            "text": f"✅ {text} ▼",
            "callback_data": callback_data
        }

    @classmethod
    def info_about_keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(row_width=1)

        placeholder_data: dict = cls.placeholder(
            cls.info_about
        )

        keyboard.add(
            InlineKeyboardButton(**placeholder_data)
        )

        return keyboard

    @classmethod
    def my_gigs_keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(row_width=1)

        placeholder_data: dict = cls.placeholder(
            cls.gigs
        )

        keyboard.add(
            InlineKeyboardButton(**placeholder_data)
        )

        return keyboard
