import datetime

from keyboards.keyboards import DropdownMenu, CalendarMenu
from aiogram.types import Message

#TODO: super Calendar cls
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