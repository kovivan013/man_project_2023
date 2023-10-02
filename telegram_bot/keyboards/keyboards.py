from aiogram.types import (
    KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
)
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
class MainMenu:
    pass



@dataclass(frozen=True)
class Navigation:

    dashboard: str = f"Панель Детектива 🔦"
    profile: str = f"Мій Профіль 👤"
    gigs: str = f"Оголошення 🗞️"
    settings: str = f"Налаштування ⚙️"
    marketplace: str = f"Маркетплейс 🔎"

    @classmethod
    def finder_keyboard(cls) -> Union[ReplyKeyboardMarkup]:
        reply_keyboard = default_reply_keyboard(row_width=1, one_time_keyboard=False)

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



@dataclass(frozen=True)
class FinderMenu:

    @classmethod
    def keyboard(cls) -> Union[ReplyKeyboardMarkup]:

        inline_keyboard = default_inline_keyboard()



        return reply_keyboard


@dataclass(frozen=True)
class SeekerMenu:

    find: str = f"🔎 Я загубив річ..."
    my_profile: str = "👤 Мій профіль"
    info_about: str = "ℹ Про проект"

    @classmethod
    def keyboard(cls) -> Union[ReplyKeyboardMarkup]:
        reply_keyboard = default_reply_keyboard(row_width=2)

        reply_keyboard.add(
            KeyboardButton(text=cls.find)
        )
        reply_keyboard.add(
            KeyboardButton(cls.my_profile),
            KeyboardButton(cls.info_about)
        )

        return reply_keyboard

@dataclass(frozen=True)
class MyProfile:

    switch_mode: str = f"Сменить режим"
    info_about: str = f"Про меня"
    gigs: str = f"Мои объявления"

    switch_mode_callback: str = f"switch_mode_callback"
    info_about_callback: str = f"info_about_callback"
    gigs_callback: str = f"gigs_callback"

    @classmethod
    def keyboard(cls) -> Union[ReplyKeyboardMarkup]:
        inline_keyboard = default_inline_keyboard(row_width=1)

        switch_mode_data: dict = {
           "text": cls.switch_mode,
            "callback_data": cls.switch_mode_callback
        }
        info_about_data: dict = {
            "text": cls.info_about,
            "callback_data": cls.info_about_callback
        }
        gigs_data: dict = {
            "text": cls.gigs,
            "callback_data": cls.gigs_callback
        }


        inline_keyboard.add(
            InlineKeyboardButton(**switch_mode_data),
            InlineKeyboardButton(**info_about_data),
            InlineKeyboardButton(**gigs_data)
        )

        return inline_keyboard