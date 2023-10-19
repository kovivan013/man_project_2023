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
from aiogram.dispatcher.filters.state import State

class StateUtils:

    @classmethod
    def get_state(cls, state: State):
        return f"{state._state}"

    @classmethod
    def get_current_state(cls, current_state: str):
        return current_state.split(":")[-1]




