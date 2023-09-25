from pydantic import BaseModel


class UserCreate(BaseModel):
    telegram_id: int
    username: str
    firstname: dict = {}
    status: int = 0

    def as_dict(self) -> dict:
        return self.__dict__
