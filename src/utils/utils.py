import datetime
import uuid

from telegram_bot.keyboards.keyboards import DropdownMenu, CalendarMenu
from aiogram.types import Message, InputMediaPhoto, CallbackQuery


class Utils(CalendarMenu):

    def file_id(self, message: Message) -> str:
        return message.photo[-1].file_id

    def location(self, message: Message) -> dict:
        data: dict = {
            "latitude": message.location.latitude,
            "longitude": message.location.longitude
        }
        return data

    def date(self, timestamp: int):
        date = datetime.datetime.fromtimestamp(timestamp)
        return f"{date.day} {self.months[date.month]['case']}, {date.year} року"

    def now(self, timestamp: bool = True):
        now = datetime.datetime.now()
        if timestamp:
            return now.timestamp().__int__()
        return now

    @staticmethod
    def get_uuid():
        return str(uuid.uuid4())

    @classmethod
    def sort_by(cls, obj: dict, path: list,
                reverse: bool = True):
        sorted_obj = dict(sorted(
            obj.items(),
            key=lambda x: cls.get_value(x[1], path=path),
            reverse=reverse
        ))

        return sorted_obj

    @classmethod
    def get_value(cls, obj: dict, path: list):
        for i in path:
            obj = obj.setdefault(i)
        return obj
