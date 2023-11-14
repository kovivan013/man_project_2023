from pydantic import BaseModel

class PayloadStructure:
    def add(self,
             telegram_id: int = None,
             username: str = None,
             description: str = None):
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

