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
from dataclasses import dataclass
from typing import Union
from man_project_2023.telegram_bot.states.states import CurrentState
from man_project_2023.telegram_bot.keyboards.keyboards import DropdownMenu
from aiogram.types import Message

class Utils:
    pass


class HandlersUtils:
    # TODO: context manager, etc...

    @classmethod
    async def context_manager(cls, current_state: CurrentState,
                              message: Message, image: str):
        photo = await current_state.state_photo(image=image)
        await message.answer_photo(photo=photo,
                                   reply_markup=DropdownMenu.placeholder_menu(
                                       current_menu=await current_state.get_placeholder()
                                   ))

class KeyboardsUtils:
    pass

class StatesUtils:
    pass


# class StateUtils:
#
#     @classmethod
#     def get_state(cls, state: State):
#         return f"{state._state}"
#
#     @classmethod
#     def get_current_state(cls, current_state: str):
#         return current_state.split(":")[-1]

# class Utils:
#
#     def get_buttons(self):
#         buttons = vars(self)
#
#         buttons_list: list = []
#         for i, v in buttons.items():
#             if "callback" not in i:
#                 buttons_list.append([{"text": v, "callback_data": buttons[i + "_callback"]}])
#
#         return {"inline_keyboard": buttons_list}
#
# class MyProfile(Utils):
#
#     def __init__(self):
#         self.info_about: str = f"Про себе 🔓"
#         self.gigs: str = f"Мої оголошення 📰"
#
#         self.info_about_callback: str = f"info_about_callback"
#         self.gigs_callback: str = f"gigs_callback"
#
#
# print(MyProfile().get_buttons())
