import aiohttp
from abc import ABC, abstractmethod


class RequestSender(ABC):

    def __init__(self, url: str = ""):
        self.url: str = url
        self._payload: dict = {}

    @abstractmethod
    async def _send(self):
        pass

    async def send_request(self):

        self._payload: dict = {
            "url": self.url
        }

        session_params: dict = {
            "trust_env": True,
            "connector": aiohttp.TCPConnector()
        }

        try:
            async with aiohttp.ClientSession(**session_params) as session:
                answer: dict = await self._send(session)
        except Exception as err:
            raise Exception(err)

        return answer["answer_data"]


class GetRequest(RequestSender):
    async def _send(self, session) -> dict:
        async with session.get(**self._payload) as response:
            return {
                "status": response.status,
                "answer_data": await response.json()
            }


class PostRequest(RequestSender):
    def __init__(self, url: str = "", data: dict = None):
        super().__init__(url)
        self._data_for_send: dict = data

    async def _send(self, session):
        self._payload.update(json=self._data_for_send)
        async with session.post(**self._payload) as response:
            return {
                "status": response.status,
                "answer_data": await response.json()
            }
