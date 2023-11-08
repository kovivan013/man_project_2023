from pydantic import BaseModel

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