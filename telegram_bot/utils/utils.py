# class Animal:
#     def __init__(self, type: int, age: int, satiety: int = 10):
#         types: dict = {0: "Собака", 1: "Кіт"}
#         self.type = types[type]
#         self.age = age
#         self.satiety = satiety
#
#     def check_satiety(self):
#         return "Голодний" if self.satiety < 10 else "Ситий"
#
#     def sleep(self):
#         if self.satiety >= 4:
#             self.satiety -= self.satiety/2
#         else:
#             self.satiety -= 1
#         return f"{self.type} поспав і зголоднів на {int(self.satiety/2) if self.satiety >=4 else 1}"
#
# class Dog(Animal):
#     def __init__(self, type: int):
#         super().__init__(self.satiety, self.age)
#         self.type = type
#
#
# class Cat(Animal):
#     pass
#
# dog = Dog(ag)
import datetime

from dataclasses import dataclass
from typing import Union
from man_project_2023.telegram_bot.states.states import CurrentState, ProfileStates
from man_project_2023.telegram_bot.keyboards.keyboards import DropdownMenu, CalendarMenu
from aiogram.types import Message, InputMediaPhoto, CallbackQuery
from aiogram.dispatcher.storage import FSMContext


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




