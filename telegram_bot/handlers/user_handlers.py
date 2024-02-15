import asyncio
import datetime
from pydantic import BaseModel

from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.message import ContentTypes
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InputMediaPhoto, InputFile

from telegram_bot.config import bot, Dispatcher, dp
from telegram_bot.utils.utils import Utils
from telegram_bot.classes.api_requests import UserAPI, LocationStructure, LocationAPI
from telegram_bot.states.states import (
    ProfileStates, UpdateDescriptionStates, UpdateUsernameStates,
    CreateGigStates, MainMenuStates, MarketplaceStates, FiltersStates,
    GigPreviewStates, State
)
from telegram_bot.classes.utils_classes import (
    calendar_menu, current_state, context_manager, list_manager,
    filters_manager, marketplace, Marketplace, Storage
)
from telegram_bot.keyboards.keyboards import (
    YesOrNo, Controls, MyProfile, Filters, DropdownMenu, UpdateProfile,
    CreateGigMenu, CalendarMenu, ListMenu, MainMenu, GigContextMenu, MarketplaceMenu
)
from telegram_bot.decorators.decorators import (
    catch_error, history_manager
)
from photos_database.handlers import PhotosDB
from utils.schemas.api_schemas import (
    GigCreate, UserCreate, UpdateDescription, BaseGig, BaseUser, Mode
)

utils = Utils()


class RegisterMH:
    pass


class StartMH:

    @classmethod
    @history_manager(group=["add_gig", "change_mode"], onetime=True)
    async def context_manager(cls, message: Message, state: FSMContext) -> None:
        await context_manager.delete(state)
        await current_state.set_state(state)
        await current_state.update_classes(state=state,
                                           keyboard_class=MainMenu,
                                           state_class=MainMenuStates)
        await MainMenuStates.start_menu.set()
        response = await UserAPI.get_user(telegram_id=state.user)
        user = BaseUser().model_validate(response.data)
        await context_manager.send_default(state=state,
                                           current_state=current_state,
                                           text=f"👋 Вітаємо, *{user.username}*!",
                                           reply_markup=MainMenu.keyboard(mode=user.mode),
                                           image="logo")

    @classmethod
    async def start_menu(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await context_manager.delete(state)
        await current_state.update_classes(state=state,
                                           keyboard_class=MainMenu,
                                           state_class=MainMenuStates)
        await cls.context_manager(message=callback.message,
                                  state=state)

    @classmethod
    async def change_mode(cls, callback: CallbackQuery, state: FSMContext) -> None:
        mode = await UserAPI.get_mode(telegram_id=state.user)
        data: dict = {
            "mode": {0: 1, 1: 0}[mode]
        }
        await UserAPI.update_mode(telegram_id=state.user,
                                  data=data)
        await callback.answer(text=f"Тепер Ви у режимі {MainMenu.modes[data['mode']]}")
        await history_manager.back(state=state,
                                   group="change_mode")


class MarketplaceMH:

    @classmethod
    async def search(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await current_state.set_state(state)
        await MarketplaceStates.search_input.set()
        await filters_manager.reset_filters(state)
        await context_manager.edit(state=state,
                                   current_state=current_state,
                                   text="🔍 *Уведіть пошуковий запит:*",
                                   image="gigs_list",
                                   reply_markup=MarketplaceMenu.search_keyboard(),
                                   with_placeholder=False)

    @classmethod
    async def check_request(cls, message: Message, state: FSMContext) -> None:
        if len(request_key := message.text) <= 100:
            await message.delete()
            await marketplace.set_request(state=state,
                                          key=request_key)
            await context_manager.edit(state=state,
                                       text=f"🔍 Ваш пошуковий запит: *{request_key}*",
                                       image="gigs_list",
                                       reply_markup=MarketplaceMenu.search_keyboard(with_search=True),
                                       with_placeholder=False)

    @classmethod
    @history_manager(group=["add_gig", "gig_preview"], onetime=True)
    async def request(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await MarketplaceStates.gigs_list.set()
        request = await marketplace._document(state)
        await marketplace.get_gigs(state=state,
                                   request=request.key)
        document = await marketplace._document(state)
        await context_manager.edit(state=state,
                                   text=f"🗒️ За Вашим пошуковим запитом було знайдено *{document.gigs}* оголошень!",
                                   image="gigs_list",
                                   reply_markup=MarketplaceMenu.keyboard(page=document.page,
                                                                         pages=document.pages),
                                   with_placeholder=False)
        await marketplace.send_gigs(state=state,
                                    reply_markup=GigContextMenu.marketplace_keyboard)

    @classmethod
    @history_manager(group="gig_preview", onetime=True)
    async def update_page(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await context_manager.delete_context_messages(state)
        document = await marketplace._document(state)
        if callback.data == Controls.forward_callback:
            document = await marketplace.next_page(state)
        elif callback.data == Controls.backward_callback:
            document = await marketplace.previous_page(state)
        await context_manager.edit(state=state,
                                   text=f"🗒️ За Вашим пошуковим запитом було знайдено *{document.gigs}* оголошень!",
                                   image="gigs_list",
                                   reply_markup=MarketplaceMenu.keyboard(page=document.page,
                                                                         pages=document.pages),
                                   with_placeholder=False)
        await marketplace.get_gigs(state=state,
                                   request=document.key,
                                   page=document.page)
        await marketplace.send_gigs(state=state,
                                    reply_markup=GigContextMenu.marketplace_keyboard)


class MyProfileMH:

    # @classmethod
    # async def select_menu(cls, callback: CallbackQuery, state: FSMContext) -> None:
    #     await context_manager.select(state)
    #     await ProfileStates.select_menu.set()

    @classmethod
    @catch_error
    @history_manager(group=["add_gig", "change_mode"], onetime=True)
    async def info_about(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await current_state.set_state(state)
        await current_state.update_classes(state=state,
                                           keyboard_class=MyProfile,
                                           state_class=MyProfile)
        await ProfileStates.info_about.set()
        response = await UserAPI.get_user(telegram_id=state.user)
        user: BaseUser = BaseUser().model_validate(response.data)

        await context_manager.edit(state=state,
                                   current_state=current_state,
                                   reply_markup=MyProfile.info_about_placeholder(),
                                   image="dashboard_profile")
        image = open('img/reg_data_board.png', 'rb')
        if not await context_manager.states_equals(state):
            await context_manager.appent_delete_list(
                state=state,
                message=await bot.send_photo(chat_id=state.chat,
                                             caption="📃 *Опис*"
                                                     "\n\n"
                                                     f"{user.user_data.description}"
                                                     "\n\n"
                                                     "⭐ *Досягнення*"
                                                     "\n\n"
                                                     "Недоступно",
                                             photo=image,
                                             parse_mode="Markdown",
                                             reply_markup=MyProfile.info_about_keyboard())
            )

    @classmethod
    @history_manager(group=["change_mode", "select_type", "gig_preview"], onetime=True)
    async def my_gigs(cls, message: Message, state: FSMContext) -> None:
        await current_state.update_classes(state=state,
                                           keyboard_class=MyProfile,
                                           state_class=MyProfile)
        await ProfileStates.gigs.set()
        if not await context_manager.states_equals(state):
            await marketplace.get_user_gigs(state=state,
                                            telegram_id=state.user,
                                            mode=await UserAPI.get_mode(telegram_id=state.user),
                                            type=(await filters_manager._storage(state)).gigs_type,
                                            limit=2)
        document = await marketplace._document(state)
        await context_manager.edit(state=state,
                                   current_state=current_state,
                                   image="your_gigs",
                                   reply_markup=MyProfile.gigs_placeholder(
                                       document=document
                                   ))
        if not await context_manager.states_equals(state):
            await marketplace.send_gigs(state=state,
                                        reply_markup=GigContextMenu.keyboard)

    @classmethod
    @history_manager(group="gig_preview", onetime=True)
    async def update_page(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await context_manager.delete_context_messages(state)
        document = await marketplace._document(state)
        if callback.data == Controls.forward_callback:
            document = await marketplace.next_page(state)
        elif callback.data == Controls.backward_callback:
            document = await marketplace.previous_page(state)
        await context_manager.edit(state=state,
                                   current_state=current_state,
                                   image="your_gigs",
                                   reply_markup=MyProfile.gigs_placeholder(
                                       document=document
                                   ))
        await marketplace.get_user_gigs(state=state,
                                        telegram_id=state.user,
                                        mode=await UserAPI.get_mode(telegram_id=state.user),
                                        type=document.status,
                                        page=document.page,
                                        limit=2)
        await marketplace.send_gigs(state=state,
                                    reply_markup=GigContextMenu.keyboard)

    @classmethod
    @history_manager(group="edit_description", onetime=True)
    async def edit_menu(cls, callback: CallbackQuery, state: FSMContext) -> None:

        await current_state.update_classes(state=state,
                                           keyboard_class=UpdateProfile,
                                           state_class=ProfileStates)
        await ProfileStates.edit_menu.set()
        await context_manager.select(state=state,
                                     current_state=current_state,
                                     delete_messages=True,
                                     reply_markup=UpdateProfile.keyboard())


class UpdateDescriptionMH:

    @classmethod
    @history_manager(group="proceed_description", onetime=True)
    async def modify_description(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await current_state.set_state(state)
        await UpdateDescriptionStates.description.set()
        await state.update_data({"_payload": UpdateDescription()})
        await context_manager.edit(state=state,
                                   text="⌨️ *Уведіть новий опис Вашого профіля:*",
                                   image="dashboard_profile",
                                   reply_markup=UpdateProfile.base_keyboard(with_save=False),
                                   with_placeholder=False)

    @classmethod
    @history_manager(group="proceed_description", onetime=True)
    async def check_description(cls, message: Message, state: FSMContext) -> None:
        # TODO: description validation
        async with state.proxy() as data:
            data["_payload"].user_data.description = message.text
        try: await message.delete()
        except: pass
        await UpdateDescriptionStates.input_description.set()
        await context_manager.edit(state=state,
                                   text="👆 Натисніть *\"Зберегти\"* або уведіть *новий опис*:",
                                   image="dashboard_profile",
                                   reply_markup=UpdateProfile.base_keyboard(),
                                   with_placeholder=False)

    @classmethod
    async def back_to_edit(cls, callback: FSMContext, state: FSMContext) -> None:
        await history_manager.back(state=state,
                                   group="proceed_description")

    @classmethod
    async def back_to_menu(cls, callback: FSMContext, state: FSMContext) -> None:
        await history_manager.back(state=state,
                                   group="edit_description")

    @classmethod
    async def confirm_backward(cls, callback: CallbackQuery, state: FSMContext) -> None:
        data = await Storage._payload(state)
        if not data.model_dump(exclude_defaults=True):
            await history_manager.back(state=state,
                                       group="edit_description")
            return
        await UpdateDescriptionStates.backward_description.set()
        photo = await current_state.state_photo(image="finish")
        await callback.message.edit_media(media=InputMediaPhoto(
            media=photo,
            caption="❌ *Ви точно хочете закінчити редагування?*",
            parse_mode="Markdown"
        ),
        reply_markup=YesOrNo.keyboard(is_inline_keyboard=True))

    @classmethod
    async def save_data(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await UpdateDescriptionStates.confirm_description.set()
        async with state.proxy() as data:
            data["_payload"].telegram_id = state.user
        await UserAPI.update_description(data=await Storage._payload(state, dump=True))
        await MyProfileMH.edit_menu(callback=callback,
                                    state=state)


class UpdateUsernameMH:

    @classmethod
    async def modify_username(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await callback.answer(text="Недоступно",
                              show_alert=True)


class CreateGig:

    @classmethod
    @history_manager(group="proceed_gig", onetime=True)
    async def enter_name(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await current_state.set_state(state)
        await current_state.update_classes(state=state,
                                           keyboard_class=UpdateProfile,
                                           state_class=CreateGigStates)
        await CreateGigStates.name.set()
        await state.update_data({"_payload": GigCreate()})
        await list_manager.reset(state)

        # TODO: Mode 0 - ви шукаєте.... Mode 1 - ви знайшли....
        await context_manager.edit(state=state,
                                   current_state=current_state,
                                   text=f"⌨️ *Уведіть назву оголошення:*",
                                   image="name",
                                   reply_markup=CreateGigMenu.keyboard(),
                                   with_placeholder=False)

    @classmethod
    @history_manager(group="proceed_gig", onetime=True)
    async def check_name(cls, message: Message, state: FSMContext) -> None:
        # TODO: text validation
        async with state.proxy() as data:
            data["_payload"].data.name = message.text
        await message.delete()
        await context_manager.edit(state=state,
                                   text=f"Ви увели: *{message.text}*\n\n"
                                        f""
                                        f"👆 Натисніть *\"Далі\"* або уведіть *іншу назву*:",
                                   image="name",
                                   reply_markup=CreateGigMenu.keyboard(with_next=True),
                                   with_placeholder=False)

    @classmethod
    @history_manager(group="proceed_gig", onetime=True)
    async def enter_description(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await CreateGigStates.description.set()
        await context_manager.edit(state=state,
                                   text=f"⌨️ *Уведіть опис оголошення:*",
                                   image="description",
                                   reply_markup=CreateGigMenu.keyboard(),
                                   with_placeholder=False)

    @classmethod
    @history_manager(group="proceed_gig", onetime=True)
    async def check_description(cls, message: Message, state: FSMContext) -> None:
        async with state.proxy() as data:
            data["_payload"].data.description = message.text
        await message.delete()
        await context_manager.edit(state=state,
                                   text=f"Ви увели: *{message.text}*\n\n"
                                        f""
                                        f"👆 Натисніть *\"Далі\"* або уведіть *інший опис*:",
                                   image="description",
                                   reply_markup=CreateGigMenu.keyboard(with_next=True),
                                   with_placeholder=False)

    @classmethod
    @history_manager(group="proceed_gig", onetime=True)
    async def load_image(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await CreateGigStates.photo.set()
        await context_manager.edit(state=state,
                                   text=f"⌨️ *Відправте фотографію предмета, який знайшли:*",
                                   image="photo",
                                   reply_markup=CreateGigMenu.keyboard(with_faq=True),
                                   with_placeholder=False)

    @classmethod
    @history_manager(group="proceed_gig", onetime=True)
    async def check_image(cls, message: Message, state: FSMContext) -> None:
        file_id = utils.file_id(message=message)
        async with state.proxy() as data:
            data.update({
                "file_id": file_id
            })

        await message.delete()
        await context_manager.edit(state=state,
                                   text=f"▲ Ви відправили фотографію\n\n"
                                        f""
                                        f"👆 Натисніть *\"Далі\"* або відправте *іншу фотографію*:",
                                   file_id=file_id,
                                   reply_markup=CreateGigMenu.keyboard(with_next=True),
                                   with_placeholder=False)

    @classmethod
    @history_manager(group="proceed_gig", onetime=True)
    async def enter_location(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await CreateGigStates.location.set()
        await context_manager.edit(state=state,
                                   text=f"⌨️ *Відправте локацію місця, де ви знайшли річ:*",
                                   image="location",
                                   reply_markup=CreateGigMenu.keyboard(with_faq=True),
                                   with_placeholder=False)

    @classmethod
    @history_manager(group="proceed_gig", onetime=True)
    async def check_location(cls, message: Message, state: FSMContext) -> None:
        location = utils.location(message=message)
        address = await LocationAPI.get_address(**location)
        city = await LocationStructure(location=address.data).get_city(with_type=True)

        location.update(data=city)

        async with state.proxy() as data:
            data["_payload"].data.location = data["_payload"].data.location.model_copy().model_validate(location)
            data["_payload"].data.address = address.data

        await message.delete()
        await context_manager.edit(state=state,
                                   text=f"Ви обрали *{' '.join(city.values())}*\n\n"
                                        f""
                                        f"👆 Натисніть *\"Далі\"* або відправте локацію *іншого місця*:",
                                   image="location",
                                   reply_markup=CreateGigMenu.keyboard(with_next=True),
                                   with_placeholder=False)

    @classmethod
    @history_manager(group="proceed_gig", onetime=True)
    async def enter_date(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await CreateGigStates.date.set()
        await calendar_menu.update_dates(state)
        await context_manager.edit(state=state,
                                   text=f"⌨️ *Оберіть дату, коли була знайдена річ:*",
                                   image="date",
                                   reply_markup=await calendar_menu.reply_markup(state),
                                   with_placeholder=False)

    @classmethod
    @history_manager(group="proceed_gig", onetime=True)
    async def set_date(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await callback.answer()
        if callback.data.startswith("now"):
            timestamp = utils.now()
        else:
            timestamp = int(callback.data.split("_")[0])
        date = utils.date(timestamp=timestamp)
        await context_manager.edit(state=state,
                                   text=f"Ви обрали *{date}*\n\n"
                                        f""
                                        f"👆 Натисніть *\"Далі\"* або оберіть *іншу дату*:",
                                   reply_markup=await calendar_menu.reply_markup(state,
                                                                                 with_next=True),
                                   with_placeholder=False)
        async with state.proxy() as data:
            data["_payload"].data.date = timestamp

    @classmethod
    @history_manager(group="proceed_gig", onetime=True)
    async def enter_tags(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await CreateGigStates.tags.set()
        await context_manager.edit(state=state,
                                   text=f"⌨️ *Уведіть до 5 тегів для Вашого оголошення:*",
                                   image="tags",
                                   reply_markup=ListMenu.keyboard(with_skip=True),
                                   with_placeholder=False)

    @classmethod
    @history_manager(group="proceed_gig", onetime=True)
    async def add_tag(cls, message: Message, state: FSMContext) -> None:
        reply_markup = await list_manager.add(state=state,
                                              message=message)
        await context_manager.edit(state=state,
                                   text=f"❌ *Натисніть на тег, щоб видалити його.*\n\n"
                                        f""
                                        f"👆 Натисніть *\"Далі\"* або *додайте більше тегів*:",
                                   reply_markup=reply_markup,
                                   with_placeholder=False)

    @classmethod
    @catch_error
    @history_manager(group="proceed_gig", onetime=True)
    async def confirm_create(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await CreateGigStates.check_data.set()
        async with state.proxy() as data:
            data["_payload"].data.tags = await list_manager._elements_list(state, clear=True)
            file_id = data["file_id"]

        _payload: GigCreate = await Storage._payload(state)

        address = _payload.data.location.data
        date = utils.date(timestamp=_payload.data.date)

        n = "\n"
        text = f"🔍 *Перевірте інформацію:*\n\n" \
               f"" \
               f"Назва: *{_payload.data.name}*\n" \
               f"Опис: *{_payload.data.description}*\n" \
               f"Дата: *{date}*\n" \
               f"Місце: *{address.type} {address.name}*\n" \
               f"{'Теги: *#*' + ' *#*'.join(_payload.data.tags) + f'{n}{n}' if _payload.data.tags else n}" \
               f"" \
               f"*Публікуємо оголошення?*"

        await context_manager.edit(state=state,
                                   text=text,
                                   file_id=file_id,
                                   reply_markup=YesOrNo.keyboard(is_inline_keyboard=True),
                                   with_placeholder=False)

    @classmethod
    @catch_error
    async def create(cls, callback: CallbackQuery, state: FSMContext) -> None:
        async with state.proxy() as data:
            data["_payload"].telegram_id = state.user
            data["_payload"].mode = await UserAPI.get_mode(telegram_id=state.user)
        data = await Storage._payload(state, dump=True)
        response = await UserAPI.create_gig(data=data)
        await Storage._clear_payload(state)
        response_data = BaseGig().model_validate(response.data)

        async with state.proxy() as data:
            file_id = data["file_id"]
        await PhotosDB.save(telegram_id=state.user,
                            file_id=file_id,
                            gig_id=response_data.id)

        if response._success:
            await callback.answer(text=f"✅ Успішно!",
                                  show_alert=True)
        else:
            await callback.answer(text=f"❌ Помилка!\n"
                                       f"Будь ласка, повторіть спробу.",
                                  show_alert=True)

        await MyProfileMH.my_gigs(message=callback.message,
                                  state=state)

    @classmethod
    async def back_to_create(cls, callback: FSMContext, state: FSMContext) -> None:
        await history_manager.back(state=state,
                                   group="proceed_gig")

    @classmethod
    async def back_to_menu(cls, callback: FSMContext, state: FSMContext) -> None:
        await history_manager.back(state=state,
                                   group="add_gig")

    @classmethod
    async def confirm_backward(cls, callback: CallbackQuery, state: FSMContext) -> None:
        data = await Storage._payload(state)
        if not data.model_dump(exclude_defaults=True):
            await history_manager.back(state=state,
                                       group="add_gig")
            return
        await CreateGigStates.backward.set()
        photo = await current_state.state_photo(image="finish")
        await callback.message.edit_media(media=InputMediaPhoto(
            media=photo,
            caption="❌ *Ви точно хочете закінчити редагування?*",
            parse_mode="Markdown"
        ),
        reply_markup=YesOrNo.keyboard(is_inline_keyboard=True))


class GigPreviewMH:
    pass


def register_user_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(
        StartMH.context_manager, commands=["start"], state=None
    )
    dp.register_callback_query_handler(
        StartMH.start_menu, Text(equals="back_to_main"), state=["*"]
    )
    dp.register_callback_query_handler(
        StartMH.change_mode, Text(equals=MainMenu.change_mode_callback), state=["*"]
    )

    dp.register_callback_query_handler(
        MarketplaceMH.search, Text(equals=MainMenu.search_callback), state=MainMenuStates.start_menu
    )
    dp.register_message_handler(
        MarketplaceMH.check_request, state=MarketplaceStates.search_input
    )
    dp.register_callback_query_handler(
        MarketplaceMH.request, Text(equals=MarketplaceMenu.search_callback), state=MarketplaceStates.search_input
    )
    dp.register_callback_query_handler(
        MarketplaceMH.update_page, Text(equals=Controls.forward_callback), state=MarketplaceStates.gigs_list
    )
    dp.register_callback_query_handler(
        MarketplaceMH.update_page, Text(equals=Controls.backward_callback), state=MarketplaceStates.gigs_list
    )

    dp.register_callback_query_handler(
        MyProfileMH.my_gigs, Text(equals=MyProfile.gigs_callback), state=ProfileStates.info_about
    )
    dp.register_callback_query_handler(
        MyProfileMH.info_about, Text(equals=MyProfile.info_about_callback), state=ProfileStates.gigs
    )
    dp.register_callback_query_handler(
        MyProfileMH.info_about, Text(equals=MainMenu.profile_callback), state=MainMenuStates.start_menu
    )
    dp.register_callback_query_handler(
        MyProfileMH.info_about, Text(equals=MyProfile().info_about_callback), state=ProfileStates.select_menu
    )
    dp.register_callback_query_handler(
        MyProfileMH.info_about, Text(equals=UpdateProfile.backward_callback), state=ProfileStates.edit_menu
    )
    dp.register_callback_query_handler(
        MyProfileMH.my_gigs, Text(equals=MyProfile().gigs_callback), state=ProfileStates.select_menu
    )
    dp.register_callback_query_handler(
        MyProfileMH.edit_menu, Text(equals=MyProfile.update_callback), state=ProfileStates.info_about
    )
    dp.register_callback_query_handler(
        MyProfileMH.edit_menu, Text(equals=UpdateProfile.backward_callback), state=UpdateUsernameStates.username
    )
    dp.register_callback_query_handler(
        MyProfileMH.edit_menu, Text(equals=UpdateProfile.backward_callback), state=UpdateDescriptionStates.description
    )
    dp.register_callback_query_handler(
        UpdateUsernameMH.modify_username, Text(equals=UpdateProfile().username_callback), state=ProfileStates.edit_menu
    )

    dp.register_callback_query_handler(
        UpdateDescriptionMH.modify_description, Text(equals=UpdateProfile().description_callback), state=ProfileStates.edit_menu
    )
    dp.register_callback_query_handler(
        UpdateDescriptionMH.confirm_backward, Text(equals=Controls.backward_callback), state=UpdateDescriptionStates.input_description
    )
    dp.register_message_handler(
        UpdateDescriptionMH.check_description, state=UpdateDescriptionStates.description
    )
    dp.register_callback_query_handler(
        UpdateDescriptionMH.save_data, Text(equals=UpdateProfile.save_callback), state=UpdateDescriptionStates.input_description
    )
    dp.register_callback_query_handler(
        UpdateDescriptionMH.back_to_edit, Text(equals=YesOrNo.no_callback), state=UpdateDescriptionStates.backward_description
    )
    dp.register_callback_query_handler(
        UpdateDescriptionMH.back_to_menu, Text(equals=UpdateProfile.yes_callback), state=UpdateDescriptionStates.backward_description
    )

    dp.register_callback_query_handler(
        filters_manager.filters_menu, Text(equals=Filters.placeholder_callback), state=MarketplaceStates.gigs_list
    )
    dp.register_callback_query_handler(
        filters_manager.time_filter, Text(equals=Filters.time_callback), state=FiltersStates.filters
    )
    dp.register_callback_query_handler(
        filters_manager.set_time, Text(startswith=["latest", "oldest"]), state=FiltersStates.time_filter
    )
    dp.register_callback_query_handler(
        filters_manager.location_filter, Text(equals=Filters.city_callback), state=FiltersStates.filters
    )
    dp.register_message_handler(
        filters_manager.set_location, state=FiltersStates.location_filter
    )
    dp.register_callback_query_handler(
        filters_manager.reset_location, Text(equals=Filters.reset_city_callback), state=FiltersStates.location_filter
    )
    dp.register_callback_query_handler(
        filters_manager.tags_filter, Text(equals=Filters.tags_callback), state=FiltersStates.filters
    )
    dp.register_callback_query_handler(
        filters_manager.remove_tag, Text(endswith="_list_menu"), state=FiltersStates.tags_filter
    )
    dp.register_message_handler(
        filters_manager.add_tag, state=FiltersStates.tags_filter
    )
    dp.register_callback_query_handler(
        filters_manager.filters_menu, Text(equals=Filters.ready_callback), state=FiltersStates.time_filter
    )
    dp.register_callback_query_handler(
        filters_manager.filters_menu, Text(equals=Filters.ready_callback), state=FiltersStates.location_filter
    )
    dp.register_callback_query_handler(
        filters_manager.filters_menu, Text(equals=Filters.ready_callback), state=FiltersStates.tags_filter
    )
    dp.register_callback_query_handler(
        filters_manager.type_filter, Text(equals=MyProfile.change_type_callback), state=ProfileStates.gigs
    )
    dp.register_callback_query_handler(
        filters_manager.set_type, Text(endswith="_type_callback"), state=ProfileStates.gigs
    )

    dp.register_callback_query_handler(
        MarketplaceMH.request, Text(equals=Filters.backward_callback), state=FiltersStates.filters
    )
    # dp.register_callback_query_handler(
    #     MyProfileMH.my_gigs, Text(equals=Filters.backward_callback), state=ProfileStates.gigs
    # )

    dp.register_callback_query_handler(
        MyProfileMH.update_page, Text(equals=Filters.forward_callback), state=ProfileStates.gigs
    )
    dp.register_callback_query_handler(
        MyProfileMH.update_page, Text(equals=Filters.backward_callback), state=ProfileStates.gigs
    )

    dp.register_callback_query_handler(
        CreateGig.enter_name, Text(equals=MyProfile.add_gig_callback), state=[MainMenuStates.start_menu,
                                                                              ProfileStates.info_about,
                                                                              MarketplaceStates.gigs_list]
    )
    dp.register_message_handler(
        CreateGig.check_name, state=CreateGigStates.name
    )
    dp.register_callback_query_handler(
        CreateGig.enter_description, Text(equals=CreateGigMenu.next_callback), state=CreateGigStates.name
    )
    dp.register_message_handler(
        CreateGig.check_description, state=CreateGigStates.description
    )
    dp.register_callback_query_handler(
        CreateGig.load_image, Text(equals=CreateGigMenu.next_callback), state=CreateGigStates.description
    )
    dp.register_message_handler(
        CreateGig.check_image, content_types=ContentTypes.PHOTO, state=CreateGigStates.photo
    )
    dp.register_callback_query_handler(
        CreateGig.enter_location, Text(equals=CreateGigMenu.next_callback), state=CreateGigStates.photo
    )
    dp.register_message_handler(
        CreateGig.check_location, content_types=ContentTypes.LOCATION, state=CreateGigStates.location
    )
    dp.register_callback_query_handler(
        CreateGig.enter_date, Text(equals=CreateGigMenu.next_callback), state=CreateGigStates.location
    )
    dp.register_callback_query_handler(
        CreateGig.set_date, Text(endswith=CalendarMenu.date_callback), state=CreateGigStates.date
    )
    dp.register_callback_query_handler(
        CreateGig.enter_tags, Text(equals=CreateGigMenu.next_callback), state=CreateGigStates.date
    )
    dp.register_message_handler(
        CreateGig.add_tag, state=CreateGigStates.tags
    )
    dp.register_callback_query_handler(
        list_manager.remove, Text(endswith="_list_menu"), state=CreateGigStates.tags
    )
    dp.register_callback_query_handler(
        CreateGig.confirm_create, Text(equals=[CreateGigMenu.skip_callback, CreateGigMenu.next_callback]), state=CreateGigStates.tags
    )
    dp.register_callback_query_handler(
        CreateGig.create, Text(equals=YesOrNo.yes_callback), state=CreateGigStates.check_data
    )
    dp.register_callback_query_handler(
        CreateGig.confirm_backward, Text(equals=YesOrNo.cancel_callback), state=[CreateGigStates.name,
                                                                                 CreateGigStates.description,
                                                                                 CreateGigStates.photo,
                                                                                 CreateGigStates.location,
                                                                                 CreateGigStates.date,
                                                                                 CreateGigStates.tags,
                                                                                 CreateGigStates.check_data]
    )
    dp.register_callback_query_handler(
        CreateGig.back_to_menu, Text(equals=YesOrNo.yes_callback), state=CreateGigStates.backward
    )
    dp.register_callback_query_handler(
        CreateGig.back_to_create, Text(equals=YesOrNo.no_callback), state=CreateGigStates.backward
    )

    dp.register_callback_query_handler(
        calendar_menu.move_forward, Text(equals=Controls.forward_callback), state=CreateGigStates.date
    )
    dp.register_callback_query_handler(
        calendar_menu.move_bacward, Text(equals=Controls.backward_callback), state=CreateGigStates.date
    )
    dp.register_callback_query_handler(
        marketplace.confirm_delete, Text(endswith=[GigContextMenu.stop_callback, YesOrNo.no_callback]), state=ProfileStates.gigs
    )
    dp.register_callback_query_handler(
        marketplace.delete_gig, Text(endswith=GigContextMenu.confirm_delete_callback), state=ProfileStates.gigs
    )
    dp.register_callback_query_handler(
        marketplace.gig_preview, Text(endswith=[GigContextMenu.preview_callback, GigContextMenu.detail_callback]), state=[ProfileStates.gigs,
                                                                                                                          MarketplaceStates.gigs_list]
    )
    dp.register_callback_query_handler(
        marketplace.back_to_menu, Text(equals=Controls.backward_callback), state=GigPreviewStates.preview
    )
