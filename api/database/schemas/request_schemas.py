from pydantic import BaseModel

class UserCreate(BaseModel):
    telegram_id: int
    username: str
    firstname: dict = {}
    status: int = 0