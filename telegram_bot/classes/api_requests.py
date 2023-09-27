import asyncio

from man_project_2023.telegram_bot.config import BASE_API_URL
from man_project_2023.telegram_bot.api.request_classes import GetRequest, PostRequest


class API:
    __BASE_SERVER_URL: str = BASE_API_URL

    @classmethod
    async def _get_request(cls, endpoint: str):
        url: str = cls.__BASE_SERVER_URL + endpoint
        return await GetRequest(url=url).send_request()

    @classmethod
    async def _post_request(cls, endpoint: str, data: dict):
        url: str = cls.__BASE_SERVER_URL + endpoint
        return await PostRequest(url=url,
                                 data=data).send_request()


class UserAPI(API):
    __prefix = lambda endpoint: "/user" + endpoint

    @classmethod
    async def create_user(cls, telegram_id: int, username: str,
                          firstname: str):
        endpoint: str = cls.__prefix("/create_user")
        data: dict = {
            "telegram_id": telegram_id,
            "username": username
        }

        return await cls._post_request(endpoint=endpoint,
                                       data=data)

    @classmethod
    async def get_user_status(cls, telegram_id: int):
        endpoint: str = cls.__prefix(f"/{telegram_id}/status")
        return await cls._get_request(endpoint=endpoint)


class AdminAPI(API):
    __prefix = lambda endpoint: "/admin" + endpoint


class SystemAPI(API):
    __prefix = lambda endpoint: "/system" + endpoint