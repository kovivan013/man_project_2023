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
    reply_keyboard = default_reply_keyboard()
    inline_keyboard = default_inline_keyboard()

    yes: str = f"✅ Так"
    no: str = f"❌ Ні"
    cancel: str = f"🛑 Відміна"
    skip: str = f"▶▶ Пропустити"

    yes_callback: str = f"yes_callback"
    no_callback: str = f"no_callback"
    cancel_callback: str = f"cancel_callback"
    skip_callback: str = f"skip_callback"

    @classmethod
    def keyboard(cls, inline_keyboard: bool = False):

        yes_data: dict = {
            "text": cls.yes,
            "callback_data": cls.yes_callback
        }

        no_data: dict = {
            "text": cls.no,
            "callback_data": cls.no_callback
        }

        if inline_keyboard:
            cls.inline_keyboard.add(
                InlineKeyboardButton(**yes_data),
                InlineKeyboardButton(**no_data)
            )

            return cls.inline_keyboard

        cls.reply_keyboard.add(
            KeyboardButton(**yes_data),
            KeyboardButton(**no_data)
        )

        return cls.reply_keyboard

    @classmethod
    def cancel_keyboard(cls, inline_keyboard: bool = False):

        cancel_data: dict = {
            "text": cls.cancel,
            "callback_data": cls.cancel_callback
        }

        if inline_keyboard:
            cls.inline_keyboard.add(
                InlineKeyboardButton(**cancel_data)
            )

            return cls.inline_keyboard

        cls.reply_keyboard.add(
            KeyboardButton(**cancel_data)
        )

        return cls.reply_keyboard

    @classmethod
    def skip_keyboard(cls, inline_keyboard: bool = False):

        skip_data: dict = {
            "text": cls.skip,
            "callback_data": cls.skip_callback
        }

        if inline_keyboard:
            cls.inline_keyboard.add(
                InlineKeyboardButton(**skip_data)
            )

            return cls.inline_keyboard

        cls.reply_keyboard.add(
            KeyboardButton(**skip_data)
        )

        return cls.reply_keyboard


@dataclass(frozen=True)
class Controls:
    # TODO: Controls Menu Param types: [LIST, DICT, TUPLE]

    forward: str = f"Вперед ▶"
    backward: str = f"◀ Назад"
    close: str = f"Закрити ✖"

    forward_callback: str = f"forward_control_callback"
    backward_callback: str = f"backward_control_callback"
    close_callback: str = f"close_control_callback"
