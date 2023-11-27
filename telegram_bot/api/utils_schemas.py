from pydantic import BaseModel

class PayloadStructure:
    def add(self,
            telegram_id: int = None,
            username: str = None,
            name: str = None,
            description: str = None,
            photo: str = None,
            tags: list = None,
            location: dict = None,
            date: int = None
            ):
        data: dict = locals()
        data.pop("self")
        for i, v in data.items():
            if v is not None:
                setattr(self, i, v)

    def as_dict(self) -> dict:
        return self.__dict__

class DataStructure(BaseModel):
    status: int = 200
    success: bool = False
    message: str = ""
    data: dict = {}

    def _as_dict(self) -> dict:
        return self.__dict__

class ResponseStructure:
    def __init__(self, status: int, data: dict):
        self.status = status
        self.data = data

    def _as_dict(self) -> dict:
        return self.__dict__

class AddressUtils:

    def __init__(self, location: dict) -> None:
        self.location = location

    async def get_city(self):
        address: dict = self.location["address"]

        keys: list = ['city', 'town', 'village', 'municipality']

        for i in keys:
            if i in address.keys():
                return address[i]




