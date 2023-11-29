import asyncio

from man_project_2023.telegram_bot.config import BASE_API_URL
from man_project_2023.telegram_bot.api.request_classes import GetRequest, PostRequest, PatchRequest, DataStructure
from man_project_2023.telegram_bot.api.utils_schemas import LocationStructure


class API:
    __BASE_SERVER_URL: str = BASE_API_URL

    @classmethod
    async def _get_request(cls, endpoint: str, data: dict = None, base_request: bool = True):
        if base_request:
            url: str = cls.__BASE_SERVER_URL + endpoint
        else:
            url: str = endpoint
        return await GetRequest(url=url,
                                data=data).send_request()

    @classmethod
    async def _post_request(cls, endpoint: str, data: dict, base_request: bool = True):
        if base_request:
            url: str = cls.__BASE_SERVER_URL + endpoint
        else:
            url: str = endpoint
        return await PostRequest(url=url,
                                 data=data).send_request()

    @classmethod
    async def _patch_request(cls, endpoint: str, data: dict, base_request: bool = True):
        if base_request:
            url: str = cls.__BASE_SERVER_URL + endpoint
        else:
            url: str = endpoint
        return await PatchRequest(url=url,
                                  data=data).send_request()


class UserAPI(API):
    __prefix = lambda endpoint: "/user" + endpoint

    @classmethod
    async def create_user(cls, telegram_id: int, username: str):
        endpoint: str = cls.__prefix("/create_user")
        data: dict = {
            "telegram_id": telegram_id,
            "username": username,
            "description": ""
        }

        return await cls._post_request(endpoint=endpoint,
                                       data=data)

    @classmethod
    async def get_user_data(cls, telegram_id: int) -> DataStructure:
        endpoint: str = cls.__prefix(f"/{telegram_id}/user_data")
        return await cls._get_request(endpoint=endpoint)

    @classmethod
    async def update_description(cls, telegram_id: int, description: str):
        endpoint: str = cls.__prefix("/update_description")

        data: dict = {
            "telegram_id": telegram_id,
            "description": description
        }

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
        endpoint: str = cls.__URL

        data: dict = {
            "format": "json",
            "lat": latitude,
            "lon": longitude
        }

        return await cls._get_request(endpoint=endpoint,
                                      data=data,
                                      base_request=False)


# import asyncio
#
# resp = asyncio.run(LocationAPI.get_address(latitude=49.00523,
#                                            longitude=31.39220))
#
# print(resp._as_dict())
# a = AddressUtils(location=resp.data)
# print(asyncio.run(a.get_city()))

