import asyncio
import datetime

from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.message import ContentTypes
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InputMediaPhoto, InputFile

from config import bot, Dispatcher, dp
from utils.utils import utils
from classes.api_requests import UserAPI, LocationAPI
from states.states import (
    ProfileStates, UpdateDescriptionStates, UpdateUsernameStates,
    CreateGigStates, MainMenuStates, MarketplaceStates, FiltersStates,
    GigPreviewStates, RegisterStates, MessagesStates, State
)
from classes.utils_classes import (
    calendar_menu, current_state, context_manager, list_manager,
    filters_manager, marketplace, Marketplace, Storage
)
from keyboards.keyboards import (
    YesOrNo, Controls, MyProfile, Filters, DropdownMenu, UpdateProfile,
    CreateGigMenu, CalendarMenu, ListMenu, MainMenu, GigContextMenu, MarketplaceMenu, RegisterMenu,
    DashboardMenu, MessagesButtons
)
from decorators.decorators import (
    catch_error, history_manager, check_registered, reset_filters, private_message
)
from schemas.api_schemas import (
    GigCreate, UserCreate, UpdateDescription, BaseGig, BaseUser, Mode, SendMessage
)
from api.utils_schemas import LocationStructure
from photos_database.handlers import S3DB


class RegisterMH:
    #TODO: сделать рег в PhotosDB и позже перенести на S3
    @classmethod
    @private_message
    async def start_register(cls, message: Message, state: FSMContext) -> None:
        await RegisterStates.start_register.set()
        await context_manager.send_default(state=state,
                                           text=f"👆 *Хочеш стати частиною нас?*\n\n"
                                                f"Вітаємо, *{message.from_user.username}*! Для користування сервісом необхідно зареєструватись.\n\n"
                                                f"Гарантуємо, що процес займе не більше *декількох хвилин* :)",
                                           reply_markup=RegisterMenu.keyboard(),
                                           image="count_logo")

    @classmethod
    async def enter_nickname(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await RegisterStates.username.set()
        await state.update_data({"_payload": UserCreate()})
        async with state.proxy() as data:
            data["_payload"].telegram_id = state.user
        await callback.answer(text="Етап 1")
        await callback.message.edit_media(media=InputMediaPhoto(
            media=await current_state.state_photo(image="username"),
            caption=f"👍 Чудово! Для початку уведіть свій нікнейм:\n\n"
                    f"‼ Нікнейм не має містити більше 32 символів.",
            parse_mode="Markdown"
        ),
        reply_markup=RegisterMenu.username_keyboard()
        )

    @classmethod
    async def get_username(cls, callback: CallbackQuery, state: FSMContext) -> None:
        if not (username := callback.from_user.username):
            await callback.answer(text=f"❌ Ви не встановили нікнейм у Вашому Telegram-акаунті!\n"
                                       f"🖊 Ви можете зробити це, або увести власний тут.",
                                  show_alert=True)
        else:
            async with state.proxy() as data:
                data["_payload"].username = username
            await context_manager.edit(state=state,
                                       text=f"Ваш нійнейм: *{username}*\n\n"
                                            f"👆 Натисніть *\"Далі\"* або уведіть *інший нікнейм*:",
                                       reply_markup=RegisterMenu.username_keyboard(with_next=True),
                                       image="username",
                                       with_placeholder=False)

    @classmethod
    async def check_nickname(cls, message: Message, state: FSMContext) -> None:
        async with state.proxy() as data:
            data["_payload"].username = (username := message.text)
        await message.delete()
        await context_manager.edit(state=state,
                                   text=f"Ваш нійнейм: *{username}*\n\n"
                                        f"👆 Натисніть *\"Далі\"* або уведіть *інший нікнейм*:",
                                   reply_markup=RegisterMenu.username_keyboard(with_next=True),
                                   image="username",
                                   with_placeholder=False)

    @classmethod
    async def enter_description(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await RegisterStates.description.set()
        await callback.message.edit_media(media=InputMediaPhoto(
            media=await current_state.state_photo(image="description"),
            caption=f"📃 Уведіть опис Вашого профіля:\n\n"
                    f"‼ Опис не має містити більше 512 символів.",
            parse_mode="Markdown"
        ),
            reply_markup=RegisterMenu.description_keyboard()
        )

    @classmethod
    async def check_description(cls, message: Message, state: FSMContext) -> None:
        if len(description := message.text) > 512:
            await message.delete()
        else:
            await message.delete()
            async with state.proxy() as data:
                data["_payload"].user_data.description = description
            await context_manager.edit(state=state,
                                       text=f"Ваш опис: *{description}*\n\n"
                                            f"👆 Натисніть *\"Далі\"* або уведіть *інший опис*:",
                                       reply_markup=RegisterMenu.username_keyboard(with_next=True),
                                       image="description",
                                       with_placeholder=False)
    # @classmethod
    # async def load_profile_photo(cls, callback: CallbackQuery, state: FSMContext) -> None:
    #     await RegisterStates.photo.set()
    #     await callback.answer(text="Етап 2")
    #     await callback.message.edit_media(media=InputMediaPhoto(
    #         media=await current_state.state_photo(image="avatar"),
    #         caption=f"📸 Відправте фотографію (аватар) для Вашого профіля:",
    #         parse_mode="Markdown"
    #     ),
    #     reply_markup=RegisterMenu.photo_keyboard())
    #
    # @classmethod
    # async def save_profile_photo(cls, message: Message, state: FSMContext) -> None:
    #     pass
    @classmethod
    async def enter_phone_number(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await RegisterStates.phone_number.set()
        await callback.answer(text="Етап 3")
        await context_manager.delete(state)
        await context_manager.send_default(state=state,
                                           text=f"📞 Відправте Ваш номер телефону:\n\n"
                                                f"‼ Номер буде відображений іншому користувачу лише у випадку, "
                                                f"коли буде пройдена наша система аутентифікації \"Secret Word\".",
                                           image="contact",
                                           reply_markup=RegisterMenu.phone_keyboard()
                                           )


    @classmethod
    async def check_phone_number(cls, message: Message, state: FSMContext) -> None:
        await message.delete()
        if message.text != RegisterMenu.dont_share and message.text != None:
            msg = await bot.send_message(chat_id=state.chat,
                                         text=f"❌ *Щоб відправити номер телефону, натисніть кнопку нижче.*",
                                         parse_mode="Markdown")
            await asyncio.sleep(3)
            await msg.delete()
        elif message.text == RegisterMenu.dont_share:
            await context_manager.delete(state)
            await cls.create_account(message,
                                     state=state)
        else:
            await context_manager.delete(state)
            async with state.proxy() as data:
                data["_payload"].phone_number = message.contact.phone_number
            await cls.create_account(message,
                                     state=state)


    @classmethod
    async def create_account(cls, message: Message, state: FSMContext) -> None:
        msg = await bot.send_message(chat_id=state.chat,
                                     text=f"🚴‍♂️ *Реєструємо Вас...*",
                                     parse_mode="Markdown")
        response = await UserAPI.create_user(data=await Storage._payload(
            state=state,
            dump=True
        ))
        if not response._success:
            await msg.edit_text(text=f"⚠ Ой-ой... Виникла несподівана помилка!\n"
                                     f"🤚 Ви автоматично повернетесь на екран реєстрації через декілька секунд.")
            await asyncio.sleep(3)
        await msg.delete()
        await StartMH.context_manager(message,
                                      state=state)


class StartMH:

    @classmethod
    @history_manager(group=["add_gig", "change_mode", "main_menu"], onetime=True)
    @check_registered
    @private_message
    async def context_manager(cls, message: Message, state: FSMContext) -> None:
        await context_manager.delete(state)
        await current_state.update_classes(state=state,
                                           keyboard_class=MainMenu,
                                           state_class=MainMenuStates)
        await MainMenuStates.start_menu.set()
        # await MarketplaceStates.gigs_list.set()
        response = await UserAPI.get_user(telegram_id=state.user)
        user = BaseUser().model_validate(response.data)
        await state.update_data({
            "mode": user.mode
        })
        # keyboard = InlineKeyboardMarkup(row_width=2)
        # keyboard.add(
        #     InlineKeyboardButton(text="◀ Назад",
        #                          callback_data="jhdfg"),
        #     InlineKeyboardButton(text="Чат для зв'язку",
        #                          url="t.me/kovivan013")
        # )
        # await context_manager.send_default(state=state,
        #                                    text=f"✅ Перевірка пройдена успішна\\!\n\n"
        #                                         f"*Номер телефону*: ||\\+380675354501||",
        #                                    reply_markup=keyboard,
        #                                    image="allow_access")
        # keyboard = InlineKeyboardMarkup(row_width=2)
        # keyboard.add(
        #     InlineKeyboardButton(text="🛑 Скасувати",
        #                          callback_data="jhdfg"),
        #     InlineKeyboardButton(text=f"🤷‍♂️ Не знаю",
        #                          callback_data="shjg")
        # )
        # await context_manager.send_default(state=state,
        #                                    text=f"Для отримання контактів власника цього оголошення, необхідно дати відповідть на секретне запитання:\n\n\"*Скільки ключів у зв'язці?*\"",
        #                                    reply_markup=keyboard,
        #                                    image="keys")
        # await message.answer(text=f"e",
        #                      reply_markup=GigContextMenu.marketplace_keyboard(telegram_id=state.user,
        #                                                                       gig_id="add2539d-a3d8-4f89-8c04-d2bf5de60618"))
        await context_manager.send_default(state=state,
                                           text=f"👋 Вітаємо, *{user.username}*!",
                                           reply_markup=MainMenu.keyboard(mode=user.mode),
                                           image="logo")

    @classmethod
    @check_registered
    async def start_menu(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await context_manager.delete(state)
        await current_state.update_classes(state=state,
                                           keyboard_class=MainMenu,
                                           state_class=MainMenuStates)
        print("end start func")
        await cls.context_manager(message=callback.message,
                                  state=state)

    @classmethod
    async def change_mode(cls, callback: CallbackQuery, state: FSMContext) -> None:
        mode = await UserAPI.get_mode(telegram_id=state.user)
        data: dict = {
            "mode": {0: 1, 1: 0}[mode]
        }
        await state.update_data({
            "mode": data["mode"]
        })
        await UserAPI.update_mode(telegram_id=state.user,
                                  data=data)
        await callback.answer(text=f"Тепер Ви у режимі {MainMenu.modes[data['mode']]}")
        await history_manager.back(state=state,
                                   group="change_mode")


class MarketplaceMH:

    @classmethod
    @reset_filters
    async def search(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await MarketplaceStates.search_input.set()
        await context_manager.edit(state=state,
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
    @history_manager(group=["add_gig", "gig_preview", "filters_menu"], onetime=True)
    async def request(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await MarketplaceStates.gigs_list.set()
        request = await marketplace._document(state)
        await marketplace.get_gigs(state=state,
                                   request=request.key)
        document = await marketplace._document(state)
        await context_manager.edit(state=state,
                                   text=f"🗒️ За Вашим пошуковим запитом було знайдено *{(num := document.gigs)}* {utils.get_ending(num, ['оголошення', 'оголошення', 'оголошень'])}!",
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

class LatestDashboardMH:

    @classmethod
    @reset_filters
    @history_manager(group=["add_gig", "gig_preview", "filters_menu"], onetime=True)
    async def latest_dashboard(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await MarketplaceStates.latest_dashboard.set()
        document = await marketplace.get_latest_gigs(state=state)
        await context_manager.edit(state=state,
                                   text=f"🔍 *Тут розміщено останні оголошення про загублені речі.*",
                                   image="gigs_dashboard",
                                   reply_markup=DashboardMenu.gigs_placeholder(document=document),
                                   with_placeholder=False)
        await marketplace.send_gigs(state=state,
                                    reply_markup=GigContextMenu.dashboard_keyboard)

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
        await marketplace.get_latest_gigs(state=state,
                                          page=document.page)
        await marketplace.send_gigs(state=state,
                                    reply_markup=GigContextMenu.marketplace_keyboard)


class MyProfileMH:

    @classmethod
    @catch_error
    @history_manager(group=["add_gig", "change_mode"], onetime=True)
    async def info_about(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await current_state.update_classes(state=state,
                                           keyboard_class=MyProfile,
                                           state_class=MyProfile)
        await ProfileStates.info_about.set()
        response = await UserAPI.get_user(telegram_id=state.user)
        user: BaseUser = BaseUser().model_validate(response.data)

        await context_manager.edit(state=state,
                                   reply_markup=MyProfile.info_about_placeholder(),
                                   image="dashboard_profile")
        image = await current_state.state_photo(image="reg_data_board")
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
    @catch_error
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
        #TODO: заменить картинку
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
    @check_registered
    async def modify_description(cls, callback: CallbackQuery, state: FSMContext) -> None:
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
    #TODO: пофиксить баг с удалением сообщения при возвращения с меню подтверждения отмены создания объявления
    @classmethod
    @history_manager(group="proceed_gig", onetime=True)
    @check_registered
    async def enter_name(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await current_state.update_classes(state=state,
                                           keyboard_class=UpdateProfile,
                                           state_class=CreateGigStates)
        await CreateGigStates.name.set()
        await state.update_data({"_payload": GigCreate()})
        await list_manager.reset(state)
        modes = {
            0: "Що Ви загубили?",
            1: "Що Ви знайшли?"
        }
        await context_manager.edit(state=state,
                                   text=f"⌨️ *{modes[await UserAPI.get_mode(telegram_id=state.user)]}*\n"
                                        f"Уведіть лише назву річі.",
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
    @history_manager(group="proceed_gig", onetime=True)
    async def enter_question(cls, callback: CallbackQuery, state: FSMContext) -> None:
        if not await UserAPI.get_mode(telegram_id=state.user):
            await cls.confirm_create(callback,
                                     state=state)
            return
        await CreateGigStates.question.set()
        await context_manager.edit(state=state,
                                   text=f"⌨️ *Уведіть секретне запитання:*\n\n"
                                        f"Воно буде використане для надання доступу до Ваших контактів авторизованому користувачу.",
                                   image="description",
                                   reply_markup=CreateGigMenu.keyboard(),
                                   with_placeholder=False)

    @classmethod
    @history_manager(group="proceed_gig", onetime=True)
    async def check_question(cls, message: Message, state: FSMContext) -> None:
        if len(message.text) < 128:
            async with state.proxy() as data:
                data["_payload"].data.question = message.text
            await message.delete()
            await context_manager.edit(state=state,
                                       text=f"Ви увели: *{message.text}*\n\n"
                                            f""
                                            f"👆 Натисніть *\"Далі\"* або уведіть *інше секретне запитання*:",
                                       image="description",
                                       reply_markup=CreateGigMenu.keyboard(with_next=True),
                                       with_placeholder=False)

    @classmethod
    @history_manager(group="proceed_gig", onetime=True)
    async def enter_answer(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await CreateGigStates.secret_word.set()
        await context_manager.edit(state=state,
                                   text=f"❔ *Уведіть секретне слово (відповідь на секретне запитання):*\n\n"
                                        f"‼ Відповідь має складатись із одного слова або цифри.",
                                   image="description",
                                   reply_markup=CreateGigMenu.keyboard(),
                                   with_placeholder=False)

    @classmethod
    @history_manager(group="proceed_gig", onetime=True)
    async def check_answer(cls, message: Message, state: FSMContext) -> None:
        if len(text := message.text) < 64 and len(text.split()) == 1:
            async with state.proxy() as data:
                data["_payload"].data.secret_word = message.text
            await message.delete()
            await context_manager.edit(state=state,
                                       text=f"Секретне слово: *{message.text}*\n\n"
                                            f""
                                            f"👆 Натисніть *\"Далі\"* або уведіть *інше секретне слово*:",
                                       image="description",
                                       reply_markup=CreateGigMenu.keyboard(with_next=True),
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
               f"Секретне запитання: *{_payload.data.question}*\n" \
               f"Відповідь: *{_payload.data.secret_word}*\n\n" \
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
        await S3DB.save_preview(telegram_id=state.user,
                                    file_id=file_id,
                                    gig_id=response_data.id)

        if response._success:
            await marketplace.send_check_request(from_id=response_data.telegram_id,
                                                 from_username=callback.from_user.username,
                                                 telegram_id=response_data.telegram_id,
                                                 gig_id=response_data.id)
            await callback.answer(text=f"✅ Запит на створення відправлено!",
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


class MessagesMH:

    @classmethod
    async def messages_menu(cls, callback: CallbackQuery, state: FSMContext) -> None:
        response = await UserAPI.get_messages(telegram_id=state.user)
        if response._success:
            await MessagesStates.messages_menu.set()
            await context_manager.edit(state=state,
                                       text="*Меню повідомлень перед Вами:*" if not response.message else response.message,
                                       reply_markup=MessagesButtons.keyboard(),
                                       image="messages",
                                       with_placeholder=False)
            for v in response.data.values():
                message_data = SendMessage().model_validate(v)
                await context_manager.appent_delete_list(
                    state=state,
                    message=await bot.send_message(chat_id=state.user,
                                                   text=message_data.text,
                                                   reply_markup=message_data.reply_markup,
                                                   parse_mode="Markdown",
                                                   disable_notification=True)
                )
        else:
            await callback.answer(text=f"‼ Упс... Виникла несподівана помилка.",
                                  show_alert=True)



def register_user_handlers(dp: Dispatcher) -> None:

    dp.register_message_handler(
        StartMH.context_manager, commands=["start"], state=None
    )

    dp.register_callback_query_handler(
        RegisterMH.enter_nickname, Text(equals=RegisterMenu.start_callback), state=RegisterStates.start_register
    )
    dp.register_message_handler(
        RegisterMH.check_nickname, state=RegisterStates.username
    )
    dp.register_callback_query_handler(
        RegisterMH.get_username, Text(equals=RegisterMenu.from_profile_callback), state=RegisterStates.username
    )
    dp.register_callback_query_handler(
        RegisterMH.enter_description, Text(equals=RegisterMenu.next_callback), state=RegisterStates.username
    )
    dp.register_message_handler(
        RegisterMH.check_description, state=RegisterStates.description
    )
    dp.register_callback_query_handler(
        RegisterMH.enter_phone_number, Text(equals=[RegisterMenu.next_callback, RegisterMenu.skip_callback]), state=RegisterStates.description
    )
    dp.register_message_handler(
        RegisterMH.check_phone_number, content_types=ContentTypes.CONTACT, state=RegisterStates.phone_number
    )
    dp.register_message_handler(
        RegisterMH.check_phone_number, state=RegisterStates.phone_number
    )

    dp.register_callback_query_handler(
        StartMH.start_menu, Text(equals="back_to_main"), state=["*"]
    )
    dp.register_callback_query_handler(
        StartMH.change_mode, Text(equals=MainMenu.change_mode_callback), state=["*"]
    )

    dp.register_callback_query_handler(
        MessagesMH.messages_menu, Text(equals=MainMenu.messages_callback), state=MainMenuStates.start_menu
    )
    dp.register_callback_query_handler(
        StartMH.start_menu, Text(equals=Controls.backward_callback), state=MessagesStates.messages_menu
    )

    dp.register_callback_query_handler(
        LatestDashboardMH.latest_dashboard, Text(equals=MainMenu.dashboard_callback), state=MainMenuStates.start_menu
    )
    dp.register_callback_query_handler(
        LatestDashboardMH.update_page, Text(equals=Controls.forward_callback), state=MarketplaceStates.latest_dashboard
    )
    dp.register_callback_query_handler(
        LatestDashboardMH.update_page, Text(equals=Controls.backward_callback), state=MarketplaceStates.latest_dashboard
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
        filters_manager.filters_menu, Text(equals=Filters.placeholder_callback), state=[MarketplaceStates.gigs_list,
                                                                                        MarketplaceStates.latest_dashboard]
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
        filters_manager.back_to_menu, Text(equals=Filters.backward_callback), state=FiltersStates.filters
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
                                                                              MarketplaceStates.gigs_list,
                                                                              MarketplaceStates.latest_dashboard]
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
        CreateGig.enter_question, Text(equals=[CreateGigMenu.next_callback, CreateGigMenu.skip_callback]), state=CreateGigStates.tags
    )
    dp.register_message_handler(
        CreateGig.check_question, state=CreateGigStates.question
    )
    dp.register_callback_query_handler(
        CreateGig.enter_answer, Text(equals=CreateGigMenu.next_callback), state=CreateGigStates.question
    )
    dp.register_message_handler(
        CreateGig.check_answer, state=CreateGigStates.secret_word
    )
    dp.register_callback_query_handler(
        list_manager.remove, Text(endswith="_list_menu"), state=CreateGigStates.tags
    )
    dp.register_callback_query_handler(
        CreateGig.confirm_create, Text(equals=CreateGigMenu.next_callback), state=CreateGigStates.secret_word
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
        marketplace.gig_preview,
        Text(endswith=[GigContextMenu.preview_callback,
                       GigContextMenu.detail_callback,
                       GigContextMenu.dashboard_callback]),
        state=[ProfileStates.gigs,
               MarketplaceStates.gigs_list,
               MarketplaceStates.latest_dashboard]
    )
    dp.register_callback_query_handler(
        marketplace.back_to_menu, Text(equals=Controls.backward_callback), state=[GigPreviewStates.preview,
                                                                                  GigPreviewStates.secret_word,
                                                                                  GigPreviewStates.contacts]
    )
    dp.register_callback_query_handler(
        marketplace.contact_with, Text(endswith=GigContextMenu.contact_callback), state=GigPreviewStates.preview
    )
    dp.register_message_handler(
        marketplace.check_access, state=GigPreviewStates.secret_word
    )
