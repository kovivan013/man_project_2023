import datetime

from keyboards.keyboards import DropdownMenu, CalendarMenu
from aiogram.types import Message

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
    def get_ending(num: int, list_of_words: list) -> str:
        cases = [2, 0, 1, 1, 1, 2]
        if 4 < num % 100 < 20:
            return list_of_words[2]
        else:
            return list_of_words[cases[min(num % 10, 5)]]
