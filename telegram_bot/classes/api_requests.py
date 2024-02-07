import asyncio
import requests

from man_project_2023.telegram_bot.config import BASE_API_URL
from man_project_2023.telegram_bot.api.request_classes import GetRequest, PostRequest, PatchRequest, DeleteRequest
from man_project_2023.utils.schemas.schemas import DataStructure
from man_project_2023.utils.schemas.api_schemas import GigCreate, UserCreate, BaseUser, BaseGig
from man_project_2023.telegram_bot.api.utils_schemas import LocationStructure


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
    async def get_user_gigs(cls, telegram_id: int, city: str = "", limit: int = 1,
                            page: int = 1, from_date: str = "latest", type: str = "active") -> 'DataStructure':
        endpoint: str = cls.__prefix(f"/{telegram_id}/gigs{f'?city={city}&' if city else '?'}limit={limit}&page={page}&from_date={from_date}&type={type}")
        return await cls._get_request(endpoint=endpoint)

    @classmethod
    async def get_gigs(cls, request: str, city: str = "", limit: int = 1,
                       page: int = 1, from_date: str = "latest", type: str = "active"):
        endpoint: str = cls.__prefix(f"/v2/gigs/?title={request}{f'&city={city}' if city else ''}&limit={limit}&page={page}&from_date={from_date}&type={type}")
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





# import asyncio

# r = asyncio.run(UserAPI.delete_gig(telegram_id=1125858430, gig_id="bf93dd85-f8f4-4546-8303-9c765c354b20"))
# print(r)
# r2 = asyncio.run(LocationAPI.get_address(**r))
# print(r2)
# print(r.model_dump())
# import asyncio
# r = asyncio.run(UserAPI.get_gigs(type="co"))
# print(r)
# print(r.model_dump())

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

