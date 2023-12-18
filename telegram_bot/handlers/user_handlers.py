import datetime

from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.types.message import ContentTypes
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters import Text

from man_project_2023.telegram_bot.config import bot, Dispatcher
from man_project_2023.telegram_bot.utils.utils import Utils
from man_project_2023.telegram_bot.classes.api_requests import UserAPI, LocationStructure, LocationAPI
from man_project_2023.telegram_bot.states.states import (
    ProfileStates, UpdateDescriptionStates, UpdateUsernameStates,
    CreateGigStates, MainMenuStates, State
)
from man_project_2023.telegram_bot.classes.utils_classes import (
    Calendar, CurrentState, ContextManager, ListMenuManager,
    BranchManager
)
from man_project_2023.telegram_bot.keyboards.keyboards import (
    YesOrNo, Controls, MyProfile, Navigation, Filters, DropdownMenu, UpdateProfile,
    InlineKeyboardMarkup, CreateGigMenu, CalendarMenu, ListMenu, MainMenu
)

from man_project_2023.photos_database.handlers import PhotosDB
from man_project_2023.utils.schemas.api_schemas import (
    GigCreate, UserCreate, UpdateDescription, BaseGig, BaseUser
)

utils = Utils()

class RegisterMH:
    pass

# class FinderMH: # Тот кто ищет (НАШЕЛ)
#
#     @classmethod
#     async def cls_menu(cls, message: Message) -> None:
#         photo = open("img/dtpanel1.png", "rb")
#         await bot.send_photo(chat_id=message.from_user.id,
#                              photo=photo,
#                              caption="Знайдено речей за Вересень: *16*",
#                              parse_mode="Markdown",
#                              reply_markup=Filters.dashboard_filter())
#         await bot.send_message(chat_id=message.from_user.id,
#                                text=f"Немає доступних оголошень",
#                                reply_markup=Navigation.finder_keyboard())
#
# class SeekerMH: # Тот кто ищет (ПОТЕРЯЛ)
#
#     @classmethod
#     async def cls_menu(cls, message: Message) -> None:
#         photo = open("img/marketplace_png.png", "rb")
#         await bot.send_photo(chat_id=message.from_user.id,
#                              caption=f"💡 Що шукаєш сьогодні?",
#                              photo=photo,
#                              reply_markup=MainMenu.seeker_keyboard())

contextManager = ContextManager()
photos_db = PhotosDB(bot=bot)


class StartMH:
    current_state: CurrentState = CurrentState(keyboard_class=MainMenu,
                                               state_class=MainMenuStates)

    @classmethod
    async def context_manager(cls, message: Message, state: FSMContext) -> None:
        await cls.current_state.set_state(state)
        await MainMenuStates.start_menu.set()
        response = await UserAPI.get_user(telegram_id=state.user)
        user = BaseUser().model_validate(response.data)

        await contextManager.send_default(current_state=cls.current_state,
                                          text=f"Вітаємо, *{user.username}*!",
                                          reply_markup=MainMenu.keyboard(),
                                          image="dashboard_profile")


    @classmethod
    async def start_menu(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await contextManager.delete()
        await cls.current_state.update_classes(keyboard_class=MainMenu,
                                               state_class=MainMenuStates)
        await cls.context_manager(message=callback.message,
                                  state=state)
        # await contextManager.edit(current_state=cls.current_state,
        #                           text=)
        # response = await UserAPI.get_user(telegram_id=message.from_user.id)
        # user = BaseUser().model_validate(response.data)
        #
        # await message.answer(text=f"Вітаємо, *{user.username}*!",
        #                      reply_markup=MainMenu.keyboard(),
        #                      parse_mode="Markdown")


class MyProfileMH:

    current_state: CurrentState = CurrentState(keyboard_class=MyProfile,
                                               state_class=ProfileStates)
    branchManager: BranchManager = BranchManager()

    @classmethod
    async def select_menu(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await contextManager.select()
        await ProfileStates.select_menu.set()

    @classmethod
    async def context_manager(cls, message: Message, state: FSMContext) -> None:
        await cls.current_state.set_state(state)
        await contextManager.send(current_state=cls.current_state,
                                  required_state=ProfileStates.info_about,
                                  image="dashboard_profile")
        await cls.info_about(message=message,
                             state=state)


    @classmethod
    async def info_about(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await cls.current_state.update_classes(keyboard_class=MyProfile,
                                               state_class=MyProfile)
        await cls.current_state.set_state(state)
        await ProfileStates.info_about.set()
        await contextManager.edit(current_state=cls.current_state,
                                  image="dashboard_profile")
        image = open('img/reg_data_board.png', 'rb')

        if not await contextManager.states_equals():
            response = await UserAPI.get_user(telegram_id=state.user)
            user: BaseUser = BaseUser().model_validate(response.data)
            await contextManager.appent_delete_list(
                await bot.send_photo(chat_id=state.chat,
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
    async def my_gigs(cls, message: Message, state: FSMContext) -> None:
        await cls.current_state.update_classes(keyboard_class=MyProfile,
                                               state_class=MyProfile)
        await ProfileStates.gigs.set()
        await contextManager.edit(current_state=cls.current_state,
                                  image="dashboard_profile")
        if not await contextManager.states_equals():
            preview = open('img/423.png', 'rb')
            await contextManager.appent_delete_list(
                await bot.send_photo(chat_id=state.chat,
                                     caption="Я знайшов *чорну куртку*.\n"
                                             "📍 *Кременчук*\n"
                                             "⌚ *Сьогодні, об 16:56*",
                                     photo=preview,
                                     reply_markup={"inline_keyboard": [[{"text": "⚙  Налаштування️", "callback_data": "3754t6"}]]},
                                     parse_mode="Markdown")
            )
            preview = open('img/sh.png', 'rb')
            await contextManager.appent_delete_list(
                await bot.send_photo(chat_id=state.chat,
                                     caption="Я знайшов *шапку*.\n"
                                             "📍 *Кременчук*\n"
                                             "⌚ *Учора, об 11:32*",
                                     photo=preview,
                                     reply_markup={
                                         "inline_keyboard": [[{"text": "⚙  Налаштування️", "callback_data": "3754t6"}]]},
                                     parse_mode="Markdown")
            )
            preview = open('img/pas.png', 'rb')
            await contextManager.appent_delete_list(
                await bot.send_photo(chat_id=state.chat,
                                     caption="Я знайшов *паспорт на ім'я* \*\*\*\*\*\* \*\*\*\*\*\*\*\*\*\*.\n"
                                             "📍 *Кременчук*\n"
                                             "⌚ *25.10.23*",
                                     photo=preview,
                                     reply_markup={
                                         "inline_keyboard": [[{"text": "⚙  Налаштування️", "callback_data": "3754t6"}],
                                                             [{"text": "Додати оголошення ➕", "callback_data": "add_gig"}]]},
                                     parse_mode="Markdown")
            )


    @classmethod
    async def edit_menu(cls, callback: CallbackQuery, state: FSMContext) -> None:

        await cls.current_state.update_classes(keyboard_class=UpdateProfile,
                                               state_class=ProfileStates)
        await ProfileStates.edit_menu.set()
        await contextManager.select(current_state=cls.current_state,
                                          delete_messages=True,
                                          reply_markup=UpdateProfile.keyboard())


class UpdateDescriptionMH:

    currentState: CurrentState = CurrentState(keyboard_class=UpdateProfile,
                                              state_class=UpdateDescriptionStates)
    branchManager: BranchManager = BranchManager()
    data_for_send: UpdateDescription = None

    @classmethod
    async def modify_description(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await cls.currentState.set_state(state)
        await UpdateDescriptionStates.description.set()
        cls.data_for_send = UpdateDescription()
        message = await contextManager.edit(text="⌨️ *Уведіть новий опис Вашого профіля:*",
                                            image="dashboard_profile",
                                            reply_markup=UpdateProfile.base_keyboard(with_save=False),
                                            with_placeholder=False)

        await cls.branchManager.set(current_state=cls.currentState,
                                    message=message)

        await cls.branchManager.set_data(state_name=UpdateDescriptionStates.backward_description,
                                         caption="*Ви точно хочете закінчити редагування?*",
                                         image_name="test35459468345687456")

    @classmethod
    async def check_description(cls, message: Message, state: FSMContext) -> None:
        await UpdateDescriptionStates.input_description.set()
        await contextManager.edit(text="👆 Натисніть *\"Зберегти\"* або уведіть *новий опис*:",
                                  image="dashboard_profile",
                                  reply_markup=UpdateProfile.base_keyboard(),
                                  with_placeholder=False)
        if "data" not in message:
            await cls.update_data(message=message,
                                  state=state)

    @classmethod
    async def update_data(cls, message: Message, state: FSMContext) -> None:
        cls.data_for_send.user_data.description = message.text
        await message.delete()

    @classmethod
    async def confirm_backward(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await UpdateDescriptionStates.backward_description.set()
        await cls.branchManager.edit()

    @classmethod
    async def save_data(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await UpdateDescriptionStates.confirm_description.set()
        cls.data_for_send.telegram_id = state.user
        await UserAPI.update_description(data=cls.data_for_send.model_dump())
        await MyProfileMH.edit_menu(callback=callback,
                                    state=state)

class UpdateUsernameMH:

    @classmethod
    async def modify_username(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await callback.answer(text="Недоступно",
                              show_alert=True)


class CreateGig:

    current_state: CurrentState = CurrentState(keyboard_class=UpdateProfile,
                                               state_class=CreateGigStates)
    branch_manager: BranchManager = BranchManager()
    list_menu_manager: ListMenuManager = ListMenuManager()

    data_for_send: GigCreate = None
    select_date = Calendar()

    @classmethod
    async def enter_name(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await cls.current_state.set_state(state)
        await CreateGigStates.name.set()
        cls.data_for_send = GigCreate()
        cls.data_for_send.default()
        print(cls.data_for_send.model_dump())
        edited_message = await contextManager.edit(current_state=cls.current_state,
                                                   text=f"⌨️ *Уведіть назву оголошення:*",
                                                   image="dashboard_profile",
                                                   reply_markup=CreateGigMenu.keyboard(),
                                                   with_placeholder=False)

        await cls.branch_manager.set(current_state=cls.current_state,
                                     message=edited_message,
                                     state=await cls.current_state.state_attr())
        await cls.branch_manager.set_data(state_name=CreateGigStates.backward,
                                          caption="*Ви точно хочете закінчити редагування?*",
                                          image_name="test35459468345687456")


    @classmethod
    async def check_name(cls, message: Message, state: FSMContext) -> None:

        # TODO: text validation
        cls.data_for_send.data.name = message.text
        await message.delete()
        edited_message = await contextManager.edit(text=f"Ви увели: *{message.text}*\n\n"
                                                        f""
                                                        f"👆 Натисніть *\"Далі\"* або уведіть *іншу назву*:",
                                                   image="dashboard_profile",
                                                   reply_markup=CreateGigMenu.keyboard(with_next=True),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message)

    @classmethod
    async def enter_description(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await CreateGigStates.description.set()
        edited_message = await contextManager.edit(text=f"⌨️ *Уведіть опис оголошення:*",
                                                   image="dashboard_profile",
                                                   reply_markup=CreateGigMenu.keyboard(),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message,
                                     state=await cls.current_state.state_attr())

    @classmethod
    async def check_description(cls, message: Message, state: FSMContext) -> None:
        cls.data_for_send.data.description = message.text
        await message.delete()
        edited_message = await contextManager.edit(text=f"Ви увели: *{message.text}*\n\n"
                                                        f""
                                                        f"👆 Натисніть *\"Далі\"* або уведіть *інший опис*:",
                                                   image="dashboard_profile",
                                                   reply_markup=CreateGigMenu.keyboard(with_next=True),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message)

    @classmethod
    async def load_image(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await CreateGigStates.photo.set()
        edited_message = await contextManager.edit(text=f"⌨️ *Відправте фотографію предмета, який знайшли:*",
                                                   image="dashboard_profile",
                                                   reply_markup=CreateGigMenu.keyboard(with_faq=True),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message,
                                     state=await cls.current_state.state_attr())

    @classmethod
    async def check_image(cls, message: Message, state: FSMContext) -> None:

        file_id = utils.file_id(message=message)
        async with state.proxy() as data:
            data.update({
                "file_id": file_id
            })

        await message.delete()
        edited_message = await contextManager.edit(text=f"▲ Ви відправили фотографію\n\n"
                                                        f""
                                                        f"👆 Натисніть *\"Далі\"* або відправте *іншу фотографію*:",
                                                   file_id=file_id,
                                                   reply_markup=CreateGigMenu.keyboard(with_next=True),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message)

    @classmethod
    async def enter_location(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await CreateGigStates.location.set()
        edited_message = await contextManager.edit(text=f"⌨️ *Відправте локацію місця, де ви знайшли річ:*",
                                                   image="dashboard_profile",
                                                   reply_markup=CreateGigMenu.keyboard(with_faq=True),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message,
                                     state=await cls.current_state.state_attr())

    @classmethod
    async def check_location(cls, message: Message, state: FSMContext) -> None:
        location = utils.location(message=message)
        address = await LocationAPI.get_address(**location)
        city = await LocationStructure(location=address.data).get_city(with_type=True)
        cls.data_for_send.data.address = address.data
        cls.data_for_send.data.location = location
        await message.delete()
        edited_message = await contextManager.edit(text=f"Ви вказали: *{city}*\n\n"
                                                        f""
                                                        f"👆 Натисніть *\"Далі\"* або відправте локацію *іншого місця*:",
                                                   image="dashboard_profile",
                                                   reply_markup=CreateGigMenu.keyboard(with_next=True),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message)
        print(f"{city}\n{location}")

    @classmethod
    async def enter_date(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await CreateGigStates.date.set()
        await cls.select_date.update_dates()
        edited_message = await contextManager.edit(text=f"⌨️ *Оберіть дату, коли була знайдена річ:*",
                                                   image="dashboard_profile",
                                                   reply_markup=cls.select_date.reply_markup(),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message,
                                     state=await cls.current_state.state_attr())

    @classmethod
    async def set_date(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await callback.answer()
        if callback.data.startswith("now"):
            timestamp = utils.now()
        else:
            timestamp = int(callback.data.split("_")[0])
        date = utils.date(timestamp=timestamp)
        edited_message = await contextManager.edit(text=f"Ви обрали *{date}*\n\n"
                                                        f""
                                                        f"👆 Натисніть *\"Далі\"* або оберіть *іншу дату*:",
                                                   reply_markup=cls.select_date.reply_markup(with_next=True),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message)
        print(timestamp, datetime.datetime.fromtimestamp(timestamp))
        cls.data_for_send.data.date = timestamp

    @classmethod
    async def enter_tags(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await CreateGigStates.tags.set()
        edited_message = await contextManager.edit(text=f"⌨️ *Уведіть до 5 тегів для Вашого оголошення:*",
                                                   image="dashboard_profile",
                                                   reply_markup=ListMenu.keyboard(with_skip=True),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message,
                                     state=await cls.current_state.state_attr())

    @classmethod
    async def add_tag(cls, message: Message, state: FSMContext) -> None:
        reple_markup = await cls.list_menu_manager.add(message=message)
        edited_message = await contextManager.edit(text=f"❌ *Натисніть на тег, щоб видалити його.*\n\n"
                                                        f""
                                                        f"👆 Натисніть *\"Далі\"* або *додайте більше тегів*:",
                                                   reply_markup=reple_markup,
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message)

    @classmethod
    async def confirm_create(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await CreateGigStates.check_data.set()
        cls.data_for_send.data.tags = cls.list_menu_manager.elements_list
        async with state.proxy() as data:
            file_id = data["file_id"]
        address = await LocationStructure(location=cls.data_for_send.data.address).get_city(with_type=True)
        date = utils.date(timestamp=cls.data_for_send.data.date)

        n = "\n"
        text = f"🔍 *Перевірте інформацію:*\n\n"\
               f""\
               f"Назва: *{cls.data_for_send.data.name}*\n"\
               f"Опис: *{cls.data_for_send.data.description}*\n"\
               f"Дата: *{date}*\n"\
               f"Місце: *{address}*\n"\
               f"{'Теги: *#*' + ' *#*'.join(cls.data_for_send.data.tags) + f'{n}{n}' if cls.data_for_send.data.tags else n}"\
               f""\
               f"*Публікуємо оголошення?*"

        edited_message = await contextManager.edit(text=text,
                                                   file_id=file_id,
                                                   reply_markup=YesOrNo.keyboard(is_inline_keyboard=True),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message,
                                     state=await cls.current_state.state_attr())

    @classmethod
    async def create(cls, callback: CallbackQuery, state: FSMContext) -> None:
        cls.data_for_send.telegram_id = state.user
        data = cls.data_for_send.model_dump()
        response = await UserAPI.create_gig(data=data)
        response_data = BaseGig().model_validate(response.data)
        async with state.proxy() as data:
            file_id = data["file_id"]
        await photos_db.save(telegram_id=cls.data_for_send.telegram_id,
                             file_id=file_id,
                             gig_id=response_data.id)

        if response.status in range(200, 300):
            await callback.answer(text=f"✅ Успішно!",
                                  show_alert=True)
        else:
            await callback.answer(text=f"❌ Помилка!\n"
                                  f"Будь ласка, повторіть спробу.",
                                  show_alert=True)

        await MyProfileMH.my_gigs(message=callback.message,
                                  state=state)


    @classmethod
    async def confirm_backward(cls, callback: CallbackQuery, state: FSMContext) -> None:
        if cls.data_for_send.defaults == cls.data_for_send.model_dump():
            await MyProfileMH.my_gigs(message=callback.message,
                                      state=state)
            return
        await CreateGigStates.backward.set()
        await cls.branch_manager.edit()


def register_user_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(
        StartMH.context_manager, commands=["start"], state=None
    )
    dp.register_callback_query_handler(
        StartMH.start_menu, Text(equals="back_to_main"), state=["*"]
    )
    dp.register_message_handler(
        MyProfileMH.context_manager, commands=["profile"], state=None
    )
    dp.register_callback_query_handler(
        MyProfileMH.select_menu, Text(equals="placeholder_callback"), state=ProfileStates.info_about
    )
    dp.register_callback_query_handler(
        MyProfileMH.select_menu, Text(equals="placeholder_callback"), state=ProfileStates.gigs
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
        MyProfileMH.edit_menu, Text(equals=UpdateProfile.yes_callback), state=UpdateDescriptionStates.backward_description
    )
    dp.register_callback_query_handler(
        UpdateDescriptionMH.modify_description, Text(equals=UpdateProfile().description_callback), state=ProfileStates.edit_menu
    )
    dp.register_callback_query_handler(
        UpdateUsernameMH.modify_username, Text(equals=UpdateProfile().username_callback), state=ProfileStates.edit_menu
    )
    dp.register_callback_query_handler(
        UpdateDescriptionMH.confirm_backward, Text(equals=Controls.backward_callback), state=UpdateDescriptionStates.input_description
    )
    dp.register_message_handler(
        UpdateDescriptionMH.update_data, state=UpdateDescriptionStates.input_description
    )
    dp.register_message_handler(
        UpdateDescriptionMH.check_description, state=UpdateDescriptionStates.description
    )
    dp.register_callback_query_handler(
        UpdateDescriptionMH.check_description, Text(equals=YesOrNo.no_callback), state=UpdateDescriptionStates.backward_description
    )
    dp.register_callback_query_handler(
        UpdateDescriptionMH.save_data, Text(equals=UpdateProfile.save_callback), state=UpdateDescriptionStates.input_description
    )

    dp.register_callback_query_handler(
        CreateGig.enter_name, Text(equals="add_gig"), state=ProfileStates.gigs
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
        CreateGig.list_menu_manager.remove, Text(endswith="_list_menu"), state=CreateGigStates.tags
    )
    dp.register_callback_query_handler(
        CreateGig.confirm_create, Text(equals=CreateGigMenu.skip_callback), state=CreateGigStates.tags
    )
    dp.register_callback_query_handler(
        CreateGig.confirm_create, Text(equals=CreateGigMenu.next_callback), state=CreateGigStates.tags
    )
    dp.register_callback_query_handler(
        CreateGig.create, Text(equals=YesOrNo.yes_callback), state=CreateGigStates.check_data
    )
    dp.register_callback_query_handler(
        CreateGig.confirm_backward, Text(equals=YesOrNo.cancel_callback), state=CreateGigStates.name
    )
    dp.register_callback_query_handler(
        CreateGig.confirm_backward, Text(equals=YesOrNo.cancel_callback), state=CreateGigStates.description
    )
    dp.register_callback_query_handler(
        CreateGig.confirm_backward, Text(equals=YesOrNo.cancel_callback), state=CreateGigStates.photo
    )
    dp.register_callback_query_handler(
        CreateGig.confirm_backward, Text(equals=YesOrNo.cancel_callback), state=CreateGigStates.location
    )
    dp.register_callback_query_handler(
        CreateGig.confirm_backward, Text(equals=YesOrNo.cancel_callback), state=CreateGigStates.date
    )
    dp.register_callback_query_handler(
        CreateGig.confirm_backward, Text(equals=YesOrNo.cancel_callback), state=CreateGigStates.tags
    )
    dp.register_callback_query_handler(
        MyProfileMH.my_gigs, Text(equals=YesOrNo.yes_callback), state=CreateGigStates.backward
    )
    dp.register_callback_query_handler(
        CreateGig.branch_manager.reset_message, Text(equals=YesOrNo.no_callback), state=CreateGigStates.backward
    )
    dp.register_callback_query_handler(
        CreateGig.select_date.move_forward, Text(equals=Controls.forward_callback), state=CreateGigStates.date
    )
    dp.register_callback_query_handler(
        CreateGig.select_date.move_bacward, Text(equals=Controls.backward_callback), state=CreateGigStates.date
    )
