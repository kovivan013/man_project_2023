import asyncio
import requests

from aiogram.dispatcher.storage import FSMContext
from config import BASE_API_URL, bot
from schemas.api_schemas import SendMessage
from api.request_classes import GetRequest, PostRequest, PatchRequest, DeleteRequest
from schemas.data_schemas import DataStructure

class API:
    __BASE_SERVER_URL: str = BASE_API_URL

    @classmethod
    async def _get_request(cls, endpoint: str, data: dict = {}):
        url: str = cls.__BASE_SERVER_URL + endpoint
        return await GetRequest(url=url,
                                data=data).send_request()

    @classmethod
    async def _post_request(cls, endpoint: str, data: dict):
        url: str = cls.__BASE_SERVER_URL + endpoint
        return await PostRequest(url=url,
                                 data=data).send_request()

    @classmethod
    async def _patch_request(cls, endpoint: str, data: dict):
        url: str = cls.__BASE_SERVER_URL + endpoint
        return await PatchRequest(url=url,
                                  data=data).send_request()

    @classmethod
    async def _delete_request(cls, endpoint: str, data: dict = {}):
        url: str = cls.__BASE_SERVER_URL + endpoint
        return await DeleteRequest(url=url,
                                   data=data).send_request()


class UserAPI(API):
    __prefix = lambda endpoint: "/user" + endpoint

    @classmethod
    async def create_user(cls, data: dict) -> 'DataStructure':
        endpoint: str = cls.__prefix("/create_user")
        return await cls._post_request(endpoint=endpoint,
                                       data=data)

    @classmethod
    async def create_gig(cls, data: dict) -> 'DataStructure':
        endpoint: str = cls.__prefix("/create_gig")
        return await cls._post_request(endpoint=endpoint,
                                       data=data)

    @classmethod
    async def get_user(cls, telegram_id: int) -> 'DataStructure':
        endpoint: str = cls.__prefix(f"/{telegram_id}")
        return await cls._get_request(endpoint=endpoint)

    @classmethod
    async def get_user_gigs(cls, telegram_id: int, mode: int, city: str = "", limit: int = 1,
                            page: int = 1, from_date: str = "latest", type: str = "active") -> 'DataStructure':
        endpoint: str = cls.__prefix(f"/{telegram_id}/gigs?mode={mode}&{f'city={city}&' if city else ''}limit={limit}&page={page}&from_date={from_date}&type={type}")
        return await cls._get_request(endpoint=endpoint)

    @classmethod
    async def get_gigs(cls, request: str, city: str = "", limit: int = 1,
                       page: int = 1, from_date: str = "latest", type: str = "active"):
        endpoint: str = cls.__prefix(f"/v2/gigs/?title={request}{f'&city={city}' if city else ''}&limit={limit}&page={page}&from_date={from_date}&type={type}")
        return await cls._get_request(endpoint=endpoint)

    @classmethod
    async def get_latest_gigs(cls, mode: int = 0, city: str = "", limit: int = 1,
                       page: int = 1, from_date: str = "latest", type: str = "active"):
        endpoint: str = cls.__prefix(f"/get_latest_gigs/?mode={mode}{f'&city={city}' if city else ''}&limit={limit}&page={page}&from_date={from_date}&type={type}")
        return await cls._get_request(endpoint=endpoint)

    @classmethod
    async def get_gig(cls, telegram_id: int, gig_id: str):
        endpoint: str = cls.__prefix(f"/{telegram_id}/gigs/{gig_id}")
        return await cls._get_request(endpoint=endpoint)

    @classmethod
    async def delete_gig(cls, telegram_id: int, gig_id: str):
        endpoint: str = cls.__prefix(f"/{telegram_id}/gigs/{gig_id}")
        return await cls._delete_request(endpoint=endpoint)

    @classmethod
    async def update_description(cls, data: dict) -> 'DataStructure':
        endpoint: str = cls.__prefix("/update_description")
        return await cls._patch_request(endpoint=endpoint,
                                        data=data)

    @classmethod
    async def get_mode(cls, telegram_id: int, mode_only: bool = True) -> 'DataStructure':
        endpoint: str = cls.__prefix(f"/{telegram_id}/mode")
        answer = await cls._get_request(endpoint=endpoint)
        return answer.data["mode"] if mode_only else answer

    @classmethod
    async def update_mode(cls, telegram_id: int, data: dict) -> 'DataStructure':
        endpoint: str = cls.__prefix(f"/{telegram_id}/mode")
        return await cls._patch_request(endpoint=endpoint,
                                        data=data)

    @classmethod
    async def get_messages(cls, telegram_id: int, offset: int = 10) -> 'DataStructure':
        endpoint: str = cls.__prefix(f"/{telegram_id}/messages/?offset={offset}")
        return await cls._get_request(endpoint=endpoint)

    @classmethod
    async def send_message(cls, state: FSMContext, telegram_id: int, data: dict) -> 'DataStructure':
        endpoint: str = cls.__prefix(f"/{telegram_id}/send_message")
        response = await cls._post_request(endpoint=endpoint,
                                       data=data)

        if response._success:
            from .utils_classes import context_manager
            partial_data = SendMessage().model_validate(response.data)
            await context_manager.appent_delete_list(
                state=state,
                message=await bot.send_message(chat_id=telegram_id,
                                               text=partial_data.text,
                                               reply_markup=partial_data.reply_markup,
                                               parse_mode="Markdown",
                                               disable_notification=True)
            )

        return response

class AdminAPI(API):
    __prefix = lambda endpoint: "/admin" + endpoint

    @classmethod
    async def accept_create(cls, telegram_id: int, gig_id: str) -> 'DataStructure':
        endpoint: str = cls.__prefix(f"/{telegram_id}/{gig_id}/accept_create")
        return await cls._get_request(endpoint=endpoint)

    @classmethod
    async def decline_create(cls, telegram_id: int, gig_id: str) -> 'DataStructure':
        endpoint: str = cls.__prefix(f"/{telegram_id}/{gig_id}/decline_request")
        return await cls._get_request(endpoint=endpoint)

class SystemAPI(API):
    __prefix = lambda endpoint: "/system" + endpoint

class LocationAPI(API):

    __URL = "https://nominatim.openstreetmap.org/reverse"

    @classmethod
    async def get_address(cls, latitude: float, longitude: float) -> 'DataStructure':
        url: str = cls.__URL

        data: dict = {
            "format": "json",
            "lat": latitude,
            "lon": longitude
        }

        return await GetRequest(url=url,
                                data=data).send_request()

    @classmethod
    async def get_location(cls, name: str) -> 'DataStructure':
        url: str = "https://nominatim.openstreetmap.org/search.php"

        data: dict = {
            "format": "json",
            "city": name,
            "country": "Ukraine"
        }

        response = requests.get(url, params=data).json()
        if response:
            response_data: dict = {
                "latitude": float(response[0]['lat']),
                "longitude": float(response[0]['lon']),
            }

            return response_data
        return None