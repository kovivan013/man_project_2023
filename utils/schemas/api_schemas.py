from pydantic import BaseModel
from typing import List, Dict

from man_project_2023.api.utils.utils import Utils

class Defaults:
    def default(self):
        self.__annotations__ = self.model_dump()

    @property
    def defaults(self):
        return self.__annotations__


class Description(BaseModel):
    description: str = ""


class Badges(BaseModel):
    badges: list = []


class UserData(BaseModel):
    description: str = ""
    badges: list = []


class UserGigs(BaseModel):
    active: dict = {}
    completed: dict = {}
    archived: dict = {}
    pending: dict = {}


class BaseUser(BaseModel, Defaults):
    telegram_id: int = 0
    username: str = ""
    mode: int = 0
    user_data: UserData = UserData()
    gigs: UserGigs = UserGigs()


class Location(BaseModel):
    latitude: float = 0.0
    longitude: float = 0.0


class GigData(BaseModel):
    name: str = ""
    description: str = ""
    address: dict = {}
    date: int = 0
    tags: list = []
    location: Location = Location()


class BaseGig(BaseModel, Defaults):
    telegram_id: int = 0
    id: str = ""
    mode: int = 0
    status: int = 0
    data: GigData = GigData()


class UserCreate(BaseModel, Defaults):
    telegram_id: int = 0
    username: str = ""
    user_data: Description = Description()


class GigCreate(BaseModel, Defaults):
    telegram_id: int = 0
    mode: int = 0
    data: GigData = GigData()


class UpdateDescription(BaseModel, Defaults):
    telegram_id: int = 0
    user_data: Description = Description()