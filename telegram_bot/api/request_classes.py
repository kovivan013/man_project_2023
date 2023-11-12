import aiohttp
from abc import ABC, abstractmethod

from man_project_2023.telegram_bot.api.utils_schemas import DataStructure, ResponseStructure


class RequestSender(ABC):

    def __init__(self, url: str = ""):
        self.url: str = url
        self._payload: dict = {}

    @abstractmethod
    async def _send(self):
        pass

    async def send_request(self) -> DataStructure:

        self._payload: dict = {
            "url": self.url
        }

        session_params: dict = {
            "trust_env": True,
            "connector": aiohttp.TCPConnector()
        }

        try:
            async with aiohttp.ClientSession(**session_params) as session:
                answer: ResponseStructure = await self._send(session)
        except Exception as err:
            raise Exception(err)

        # validate answer data
        result = DataStructure(**answer.data)
        if result.success:
            return result
        elif answer.status not in range(200, 300):
            error_text: str = (
                f"Status: {answer.status}\n"
                f"Url: {self.url}\n"
                f"Error data: {answer.data}"
            )
            return error_text

class GetRequest(RequestSender):
    async def _send(self, session) -> dict:
        async with session.get(**self._payload) as response:
            return ResponseStructure(
                status=response.status,
                data=await response.json()
            )


class PostRequest(RequestSender):
    def __init__(self, url: str = "", data: dict = None):
        super().__init__(url)
        self._data_for_send: dict = data

    async def _send(self, session):
        self._payload.update(json=self._data_for_send)
        async with session.post(**self._payload) as response:
            return ResponseStructure(
                status=response.status,
                data=await response.json()
            )

class PatchRequest(RequestSender):
    def __init__(self, url: str = "", data: dict = None):
        super().__init__(url)
        self._data_for_send: dict = data

    async def _send(self, session):
        self._payload.update(json=self._data_for_send)
        async with session.patch(**self._payload) as response:
            return ResponseStructure(
                status=response.status,
                data=await response.json()
            )