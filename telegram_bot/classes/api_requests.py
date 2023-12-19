import asyncio

from man_project_2023.telegram_bot.config import BASE_API_URL
from man_project_2023.telegram_bot.api.request_classes import GetRequest, PostRequest, PatchRequest
from man_project_2023.utils.schemas.schemas import DataStructure
from man_project_2023.utils.schemas.api_schemas import GigCreate, UserCreate, BaseUser, BaseGig
from man_project_2023.telegram_bot.api.utils_schemas import LocationStructure


class API:
    __BASE_SERVER_URL: str = BASE_API_URL

    @classmethod
    async def _get_request(cls, endpoint: str, data: dict = None):
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
    async def get_user_data(cls, telegram_id: int) -> 'DataStructure':
        user = await cls.get_user(telegram_id=telegram_id)
        return user.data["user_data"]

    @classmethod
    async def update_description(cls, data: dict) -> 'DataStructure':
        endpoint: str = cls.__prefix("/update_description")
        return await cls._patch_request(endpoint=endpoint,
                                        data=data)

    @classmethod
    async def get_user_mode(cls, telegram_id: int):
        endpoint: str = cls.__prefix(f"/{telegram_id}/mode")
        return await cls._get_request(endpoint=endpoint)


class AdminAPI(API):
    __prefix = lambda endpoint: "/admin" + endpoint


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


# import asyncio
# r = asyncio.run(UserAPI.get_user(telegram_id=1125858430))
# print(r.as_dict())
#
# resp = asyncio.run(UserAPI.create_gig(telegram_id=1,
#                                       mode=1,
#                                       name="dfgeg",
#                                       description="dsfhg",
#                                       location={"latitude": 1.23476,
#                                                 "longitude": 1.45873},
#                                       address={"l": 1},
#                                       date=1701900690,
#                                       tags=[]))
# print(resp)
# resp = asyncio.run(UserAPI.create_user(telegram_id=12341122,
#                                        username="sjhg",
#                                        description=""))
# print(resp)

