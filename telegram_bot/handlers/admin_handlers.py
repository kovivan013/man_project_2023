from config import Dispatcher, bot, settings
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.storage import FSMContext
from keyboards.keyboards import AdminMenu
from decorators.decorators import check_super_admin
from classes.api_requests import AdminAPI


@check_super_admin
async def admin_menu(message: Message, state: FSMContext) -> None:
    await message.answer(
        text=f"*Адмін-панель перед Вами:*",
        parse_mode="Markdown"
    )

@check_super_admin
async def accept_request(callback: CallbackQuery, state: FSMContext) -> None:
    telegram_id, gig_id = tuple(callback.data.split("_")[:2])
    await callback.message.edit_reply_markup()
    response = await AdminAPI.accept_create(telegram_id=telegram_id,
                                            gig_id=gig_id)
    await callback.answer(text=response.message,
                          show_alert=True)

@check_super_admin
async def decline_request(callback: CallbackQuery, state: FSMContext) -> None:
    telegram_id, gig_id = tuple(callback.data.split("_")[:2])
    await callback.message.edit_reply_markup()
    response = await AdminAPI.decline_create(telegram_id=telegram_id,
                                             gig_id=gig_id)
    await callback.answer(text=response.message,
                          show_alert=True)


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(
        admin_menu, commands=["admin"], state=["*"]
    )
    dp.register_callback_query_handler(
        accept_request, Text(endswith="_accept")
    )
    dp.register_callback_query_handler(
        accept_request, Text(endswith="_decline")
    )
