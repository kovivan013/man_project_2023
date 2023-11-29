from man_project_2023.telegram_bot.config import bot, Dispatcher
from aiogram.types import Message, ContentTypes
from aiogram.dispatcher.storage import FSMContext

async def debug_handler(message: Message, state: FSMContext) -> None:


    await message.delete()
    # current_state = await state.get_state()
    # if current_state is not None:
    #     await state.finish()
    # await StartMH.cls_menu(message)

def register_debug_handlers(dp: Dispatcher) -> None:

    dp.register_message_handler(
        debug_handler, content_types=ContentTypes.ANY, state=["*"]
    )