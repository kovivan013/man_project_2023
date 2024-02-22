from telegram_bot.config import bot, Dispatcher
from aiogram.types import Message, ContentTypes
from aiogram.dispatcher.storage import FSMContext

async def debug_handler(message: Message, state: FSMContext) -> None:
    await message.delete()

def register_debug_handlers(dp: Dispatcher) -> None:

    dp.register_message_handler(
        debug_handler, content_types=ContentTypes.ANY, state=["*"]
    )