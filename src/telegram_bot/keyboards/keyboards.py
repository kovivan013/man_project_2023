from aiogram.types import (
    KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
)
from schemas.api_schemas import GigsResponse
from typing import Union
from dataclasses import dataclass
import datetime


def default_reply_keyboard(one_time_keyboard: bool = True,
                           resize_keyboard: bool = True,
                           row_width: int = 2):
    return ReplyKeyboardMarkup(
        one_time_keyboard=one_time_keyboard,
        resize_keyboard=resize_keyboard,
        row_width=row_width,
        input_field_placeholder="test"
    )


def default_inline_keyboard(row_width: int = 2):
    return InlineKeyboardMarkup(
        row_width=row_width
    )


class YesOrNo:
    yes: str = f"✅ Так"
    no: str = f"❌ Ні"
    ready: str = f"✅ Готово"
    cancel: str = f"🛑 Скасувати"
    skip: str = f"▶▶ Пропустити"
    save: str = f"📁 Зберегти"
    next: str = "Далі ↪️"

    yes_callback: str = f"yes_callback"
    no_callback: str = f"no_callback"
    ready_callback: str = f"ready_callback"
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


class Controls:
    # TODO: Controls Menu Param types: [LIST, DICT, TUPLE]

    forward: str = f"Вперед ▶"
    backward: str = f"◀ Назад"
    close: str = f"Зачинити ✖"

    plus: str = f"➕"
    minus: str = f"➖"

    short_forward: str = f"▶"
    short_backward: str = f"◀"

    forward_callback: str = f"forward_control_callback"
    backward_callback: str = f"backward_control_callback"
    close_callback: str = f"close_control_callback"
    plus_callback: str = f"plus_callback"
    minus_callback: str = f"minus_callback"

    @classmethod
    def pages_keyboard(cls, page: int, pages: int):
        keyboard: list = []

        if page > 1:
            keyboard.append(
                {
                    "text": cls.short_backward,
                    "callback_data": cls.backward_callback
                }
            )
        if pages > 0:
            keyboard.append(
                {
                    "text": f"{page} із {pages}",
                    "callback_data": "pass"
                }
            )
        if page < pages:
            keyboard.append(
                {
                    "text": cls.short_forward,
                    "callback_data": cls.forward_callback
                }
            )

        return keyboard


class Filters(Controls, YesOrNo):
    placeholder: str = f"🎛️ Фільтри"

    time: str = f"⏰ За часом"
    city: str = f"📍 За місцем"
    tags: str = f"🏷️ За тегами"
    reset_city: str = f"🔄 Скинути фільтр"

    types: dict = {
        "active": lambda c: f"Активні оголошення ({c})",
        "completed": lambda c: f"Завершені оголошення ({c})",
        "pending": lambda c: f"Очікують публікації ({c})",
        "archived": lambda c: f"Видалені оголошення ({c})"
    }

    placeholder_callback: str = f"filters_placeholde_callback"
    time_callback: str = f"time_callback"
    city_callback: str = f"city_callback"
    tags_callback: str = f"tags_callback"
    reset_city_callback: str = f"reset_city_callback"

    @classmethod
    def keyboard(cls, time: str = "latest", city: str = "all",
                 tags: int = 0, finish: bool = False) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(row_width=1)

        _time: dict = {
            "latest": ": Нові",
            "oldest": ": Старі",
        }

        _city: dict = {
            "all": "Усі"
        }

        keyboard.add(
            InlineKeyboardButton(text=f"{cls.time}{_time[time]}",
                                 callback_data=cls.time_callback),
            InlineKeyboardButton(text=f"{cls.city}: {_city.get(city, city)}",
                                 callback_data=cls.city_callback),
            InlineKeyboardButton(text=f"{cls.tags}: {tags}",
                                 callback_data=cls.tags_callback),
        )

        if finish:
            keyboard.add(
                InlineKeyboardButton(text=cls.ready,
                                     callback_data=cls.ready_callback)
            )
        else:
            keyboard.add(
                InlineKeyboardButton(text=cls.backward,
                                     callback_data=cls.backward_callback)
            )

        return keyboard

    @classmethod
    def time_keyboard(cls, time: str):
        keyboard = default_inline_keyboard()

        fields: list[InlineKeyboardButton] = [
            InlineKeyboardButton(
                text=f"▲ Нових",
                callback_data="latest"
            ),
            InlineKeyboardButton(
                text=f"▼ Старих",
                callback_data="oldest"
            )
        ]

        for i in fields:
            if i.callback_data == time:
                i.text = f"{i.text} ✅"

        keyboard.row(*fields)
        keyboard.add(
            InlineKeyboardButton(text=cls.ready,
                                 callback_data=cls.ready_callback)
        )

        return keyboard

    @classmethod
    def location_keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(row_width=1)

        keyboard.add(
            InlineKeyboardButton(text=cls.reset_city,
                                 callback_data=cls.reset_city_callback),
            InlineKeyboardButton(text=cls.ready,
                                 callback_data=cls.ready_callback)
        )

        return keyboard

    @classmethod
    def types_keyboard(cls, current_type: Union[str, int], types_count: dict):
        keyboard = default_inline_keyboard(row_width=1)

        for i, v in cls.types.items():
            keyboard.add(
                InlineKeyboardButton(text=f"{'✅ ' if i == current_type else ''}{v(types_count[i])}",
                                     callback_data=f"{i}_type_callback")
            )

        return keyboard


class ListMenu(YesOrNo, Controls):
    """
    Вызывать если нужно ввести список элементов, например список тегов
    """

    @classmethod
    def keyboard(cls, elements_list: list = [], callback: str = "",
                 with_cancel: bool = True, with_skip: bool = False,
                 with_next: bool = False, with_ready: bool = False) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(row_width=4)

        if elements_list:
            for i, v in enumerate(elements_list, start=0):
                if not i % 3:
                    keyboard.add(
                        InlineKeyboardButton(text=v,
                                             callback_data=f"{v}_list_menu")
                    )
                else:
                    keyboard.insert(
                        InlineKeyboardButton(text=v,
                                             callback_data=f"{v}_list_menu")
                    )
                if callback and callback[:callback.rindex("_list_menu")] == v:
                    keyboard.insert(
                        InlineKeyboardButton(text=cls.minus,
                                             callback_data=f"{v}_remove_list_menu")
                    )

        if with_ready:
            keyboard.add(
                InlineKeyboardButton(text=cls.ready,
                                     callback_data=cls.ready_callback)
            )
            return keyboard

        if with_cancel:
            keyboard.add(
                InlineKeyboardButton(text=cls.cancel,
                                     callback_data=cls.cancel_callback)
            )
            if with_skip:
                keyboard.insert(
                    InlineKeyboardButton(text=cls.skip,
                                         callback_data=cls.skip_callback)
                )

            if with_next:
                keyboard.insert(
                    InlineKeyboardButton(text=cls.next,
                                         callback_data=cls.next_callback)
                )

        return keyboard


class MainMenu:
    add_gig: str = f"➕ Додати оголошення"
    dashboard: str = f"📃 Дошка оголошень"
    search: str = f"🔍 Знайти річ"

    change_mode: str = "Режим"
    profile: str = f"👤 Профіль"
    settings: str = f"⚙️ Налаштування"
    support: str = f"🆘 Підтримка"
    info_about: str = f"ℹ Про проект"

    add_gig_callback: str = f"add_gig_callback"
    dashboard_callback: str = f"dashboard_callback"
    search_callback: str = f"search_callback"

    change_mode_callback: str = f"change_mode_callback"
    profile_callback: str = f"profile_callback"
    settings_callback: str = f"settings_callback"
    support_callback: str = f"support_callback"
    info_about_callback: str = f"info_about_callback"

    modes: dict = {
        0: "Шукача 🔦",
        1: "Детектива 🔍"
    }

    @classmethod
    def keyboard(cls, mode: int = 0) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(text=f"{cls.change_mode} {cls.modes[mode]}",
                                 callback_data=cls.change_mode_callback)
        )

        if mode:
            keyboard.add(
                InlineKeyboardButton(text=cls.dashboard,
                                     callback_data=cls.dashboard_callback)
            )
            keyboard.add(
                InlineKeyboardButton(text=cls.add_gig,
                                     callback_data=cls.add_gig_callback)
            )
        else:
            keyboard.add(
                InlineKeyboardButton(text=cls.search,
                                     callback_data=cls.search_callback)
            )

        keyboard.add(
            InlineKeyboardButton(text=cls.profile,
                                 callback_data=cls.profile_callback),
            InlineKeyboardButton(text=cls.settings,
                                 callback_data=cls.settings_callback),
            InlineKeyboardButton(text=cls.support,
                                 callback_data=cls.support_callback),
            InlineKeyboardButton(text=cls.info_about,
                                 callback_data=cls.info_about_callback)
        )

        return keyboard

    @classmethod
    def add_gig_keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(text=cls.add_gig,
                                 callback_data=cls.add_gig_callback)
        )

        return keyboard


class RegisterMenu(MainMenu, YesOrNo):
    start: str = f"🌟 Почати!"
    start_register: str = f"🌟 Почати реєстрацію!"
    from_profile: str = f"👤 Взяти з Telegram"
    send_number: str = f"📞 Відправити номер телефону"
    dont_share: str = f"❌ Не хочу ділитися!"

    start_callback: str = f"start_callback"
    from_profile_callback: str = f"from_profile_callback"

    @classmethod
    def keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(text=cls.info_about,
                                 callback_data=cls.info_about_callback),
            InlineKeyboardButton(text=cls.start,
                                 callback_data=cls.start_callback)
        )

        return keyboard

    @classmethod
    def start_keyboard(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(text=cls.start_register,
                                 callback_data=cls.start_callback)
        )

        return keyboard

    @classmethod
    def username_keyboard(cls, with_next: bool = False) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        if with_next:
            keyboard.add(
                InlineKeyboardButton(text=cls.next,
                                     callback_data=cls.next_callback)
            )
            return keyboard

        keyboard.add(
            InlineKeyboardButton(text=cls.from_profile,
                                 callback_data=cls.from_profile_callback)
        )

        return keyboard

    @classmethod
    def description_keyboard(cls, with_next: bool = False) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        if with_next:
            keyboard.add(
                InlineKeyboardButton(text=cls.next,
                                     callback_data=cls.next_callback)
            )
            return keyboard

        keyboard.add(
            InlineKeyboardButton(text=cls.skip,
                                 callback_data=cls.skip_callback)
        )

        return keyboard

    @classmethod
    def photo_keyboard(cls, with_next: bool = False) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        if with_next:
            keyboard.add(
                InlineKeyboardButton(text=cls.next,
                                     callback_data=cls.next_callback)
            )
            return keyboard

        keyboard.add(
            InlineKeyboardButton(text=cls.from_profile,
                                 callback_data=cls.from_profile_callback)
        )

        return keyboard

    @classmethod
    def phone_keyboard(cls) -> Union[ReplyKeyboardMarkup]:
        keyboard = default_reply_keyboard()

        keyboard.add(
            KeyboardButton(text=cls.dont_share),
            KeyboardButton(text=cls.send_number,
                           request_contact=True)
        )

        return keyboard


class DropdownMenu(MainMenu):
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
    def placeholder_menu(cls, reply_markup: InlineKeyboardMarkup, mode: int = 0):
        keyboard = default_inline_keyboard()
        modes: dict = {
            0: "🔦",
            1: "🔍"
        }

        keyboard.add(
            InlineKeyboardButton(text=f"↩ На головну",
                                 callback_data="back_to_main"),
            InlineKeyboardButton(text=f"Режим {modes[mode]}",
                                 callback_data=cls.change_mode_callback),
        )

        for i in reply_markup.inline_keyboard:
            keyboard.inline_keyboard.append(i)

        return keyboard

    @classmethod
    def menu_keyboard(cls, buttons: list) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        for i in buttons:
            for data in i:
                keyboard.insert(
                    InlineKeyboardButton(**data)
                )

        return {"inline_keyboard": buttons}


class MyProfile(MainMenu, Controls):
    info_about: str = f"🔓 Про себе ▶"
    gigs: str = f"📰 Мої оголошення ▶"

    info_about_callback: str = f"info_about_callback"
    gigs_callback: str = f"gigs_callback"

    update: str = f"🖊 Змінити"
    share: str = f"🔗 Поділитися"

    update_callback: str = f"update_callback"
    share_callback: str = f"share_callback"
    change_type_callback = "change_type_callback"

    @classmethod
    def info_about_placeholder(cls) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(row_width=1)

        keyboard.add(
            InlineKeyboardButton(text=cls.gigs,
                                 callback_data=cls.gigs_callback),
            InlineKeyboardButton(text=cls.add_gig,
                                 callback_data=cls.add_gig_callback)
        )

        return keyboard

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

    # @classmethod
    # def gigs_keyboard(cls, gigs_type: Union[str, int], type_count: int, page: int, pages: int) -> Union[
    #     InlineKeyboardMarkup]:
    #     keyboard = default_inline_keyboard(row_width=1)
    #
    #     keyboard.add(
    #         InlineKeyboardButton(text=f"{Filters.types[gigs_type](type_count)} ▼",
    #                              callback_data=cls.change_type_callback)
    #     )
    #     keyboard.row(*cls.pages_keyboard(page=page,
    #                                      pages=pages))
    #
    #     return keyboard
    @classmethod
    def gigs_placeholder(cls, document: GigsResponse) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(row_width=1)

        keyboard.add(
            InlineKeyboardButton(text=cls.info_about,
                                 callback_data=cls.info_about_callback),
            InlineKeyboardButton(text=f"{Filters.types[document.status](document.gigs)} ▼",
                                 callback_data=cls.change_type_callback)
        )
        keyboard.row(*cls.pages_keyboard(page=document.page,
                                         pages=document.pages))

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
    faq: str = f"❓ Як?"

    faq_callback: str = f"❓ Як?"

    @classmethod
    def keyboard(cls, with_next: bool = False, with_faq: bool = False,
                 with_skip: bool = False, with_ready: bool = False):
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
        if with_faq:
            keyboard.insert(
                InlineKeyboardButton(text=cls.faq,
                                     callback_data=cls.faq_callback)
            )
        if with_skip:
            keyboard.insert(
                InlineKeyboardButton(text=cls.skip,
                                     callback_data=cls.skip_callback)
            )
        if with_ready:
            keyboard.insert(
                InlineKeyboardButton(text=cls.ready,
                                     callback_data=cls.ready_callback)
            )

        return keyboard


class CalendarMenu(Controls, YesOrNo):
    short_days: list = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "НД"]
    days: list = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
    months = {
        1: {"month": "Січень", "days": 31, "case": "Січня"}, 2: {"month": "Лютий", "days": 28, "case": "Лютого"},
        3: {"month": "Березень", "days": 31, "case": "Березня"}, 4: {"month": "Квітень", "days": 30, "case": "Квітня"},
        5: {"month": "Травень", "days": 31, "case": "Травня"}, 6: {"month": "Червень", "days": 30, "case": "Червня"},
        7: {"month": "Липень", "days": 31, "case": "Липня"}, 8: {"month": "Серпень", "days": 31, "case": "Серпня"},
        9: {"month": "Вересень", "days": 30, "case": "Вересня"}, 10: {"month": "Жовтень", "days": 31, "case": "Жовтня"},
        11: {"month": "Листопад", "days": 30, "case": "Листопада"},
        12: {"month": "Грудень", "days": 31, "case": "Грудня"}
    }

    now: str = f"🗓️ Зараз"

    date_callback: str = f"_date_callback"

    @classmethod
    def keyboard(cls, with_cancel: bool = False, with_save: bool = False, with_forward: bool = True,
                 with_next: bool = False, year: int = None, month: int = None, day: int = None) -> Union[
        InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard(row_width=7)

        args = all([year, month, day])
        now = datetime.datetime.now()

        if args:
            today = datetime.datetime(year, month, day, now.hour, now.minute)
        else:
            today = datetime.datetime.now()

        firts_month_day = datetime.datetime(today.year, today.month, 1)
        weekday = firts_month_day.weekday()
        days_to_end = 7 - weekday
        days_in_month = cls.months[today.month]["days"]

        day = 1

        if today.year % 4 == 0 and today.month == 2:
            days_in_month = 29

        r = 6

        if days_in_month - days_to_end - 28 > 0:
            r += 1

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
                if (day > days_in_month or (i < 2 and j < weekday + 1)) or (
                        day > now.day and today.month == now.month and today.year == now.year):
                    keyboard.insert(
                        InlineKeyboardButton(
                            text=" ",
                            callback_data="None"
                        )
                    )
                    continue
                callback = int(datetime.datetime(today.year,
                                                 today.month,
                                                 day,
                                                 today.hour,
                                                 today.minute).timestamp())
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

        if with_next:
            keyboard.insert(
                InlineKeyboardButton(text=cls.next,
                                     callback_data=cls.next_callback)
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


class GigContextMenu(YesOrNo, Controls):
    # TODO: плейсхолдер как и был налаштування, и в back Налаштування ▼, в маркетплейсе будет просто детальніше
    # Также не забыть добавить обработку на то, твое ли то объявление

    # placeholder: str = "⚙️ Налаштування ▲"

    detail: str = f"👉 Детальніше"
    preview: str = f"🔍 Переглянути"
    stop: str = f"🛑 Зупинити"
    contact: str = f"📞 Це моя річ!"
    # stats: str = f"📊 Статистика"
    # share: str = f"🔗 Поділитися"

    # placeholder_callback: str = f"_placeholder"
    detail_callback: str = f"detail_callback"
    preview_callback: str = f"_preview_callback"
    stop_callback: str = f"_stop_callback"
    contact_callback: str = f"_contact_callback"
    # stats_callback: str = f"_stats_callback"
    # share_callback: str = f"_share_callback"
    confirm_delete_callback: str = f"_confirm_delete"

    @classmethod
    def keyboard(cls, telegram_id: int = 0, gig_id: int = 0) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()
        callback_value: str = f"{telegram_id}_{gig_id}"

        keyboard.add(
            InlineKeyboardButton(text=cls.preview,
                                 callback_data=f"{callback_value}{cls.preview_callback}"),
            InlineKeyboardButton(text=cls.stop,
                                 callback_data=f"{callback_value}{cls.stop_callback}")
        )

        return keyboard

    @classmethod
    def confirm_delete(cls, telegram_id: int = 0, gig_id: int = 0) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()
        callback_value: str = f"{telegram_id}_{gig_id}"

        keyboard.add(
            InlineKeyboardButton(text=cls.yes,
                                 callback_data=f"{callback_value}{cls.confirm_delete_callback}"),
            InlineKeyboardButton(text=cls.no,
                                 callback_data=cls.no_callback)
        )

        return keyboard

    @classmethod
    def marketplace_keyboard(cls, telegram_id: int = 0, gig_id: int = 0) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()
        callback_value: str = f"{telegram_id}_{gig_id}"

        keyboard.add(
            InlineKeyboardButton(text=cls.detail,
                                 callback_data=f"{callback_value}_{cls.detail_callback}")
        )

        return keyboard

    @classmethod
    def contact_keyboard(cls, with_contact: bool = False) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(text=cls.backward,
                                 callback_data=cls.backward_callback)
        )
        if with_contact:
            keyboard.insert(
                InlineKeyboardButton(text=cls.contact,
                                     callback_data=cls.contact_callback)
            )

        return keyboard


class MarketplaceMenu(Filters, MainMenu):
    search: str = f"Пошук 🔦"

    search_callback: str = f"search_callback"

    @classmethod
    def keyboard(cls, page: int, pages: int) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(text="↩ На головну",
                                 callback_data="back_to_main"),
            InlineKeyboardButton(text=cls.placeholder,
                                 callback_data=cls.placeholder_callback),
        )
        keyboard.add(
            InlineKeyboardButton(text=cls.add_gig,
                                 callback_data=cls.add_gig_callback)
        )

        keyboard.row(*cls.pages_keyboard(page=page,
                                         pages=pages))

        return keyboard

    @classmethod
    def search_keyboard(cls, with_search: bool = False) -> Union[InlineKeyboardMarkup]:
        keyboard = default_inline_keyboard()

        keyboard.add(
            InlineKeyboardButton(text=cls.backward,
                                 callback_data="back_to_main")
        )

        if with_search:
            keyboard.insert(
                InlineKeyboardButton(text=cls.search,
                                     callback_data=cls.search_callback)
            )

        return keyboard
