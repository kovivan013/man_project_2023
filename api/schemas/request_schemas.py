from pydantic import BaseModel


class UserCreate(BaseModel):
    telegram_id: int
    username: str
    userinfo: dict = {}
    mode: int = 0

    def as_dict(self) -> dict:
        return self.__dict__

