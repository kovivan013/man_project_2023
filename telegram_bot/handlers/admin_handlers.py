from config import Dispatcher, bot, settings
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from decorators.decorators import check_super_admin

@check_super_admin
async def admin_menu(message: Message, state: FSMContext) -> None:
    await message.answer(
        text=f"*Адмін-панель перед Вами:*",
        parse_mode="Markdown"
    )


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(
        admin_menu, commands=["admin"], state=["*"]
    )
