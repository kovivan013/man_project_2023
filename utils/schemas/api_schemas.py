from pydantic import BaseModel
from typing import List, Dict, Union
from enum import Enum
from api.utils.utils import Utils


class Description(BaseModel):
    description: str = ""

class Badges(BaseModel):
    badges: list = []

class Mode(BaseModel):
    mode: int = 0

class UserData(BaseModel):
    description: str = ""
    badges: list = []

class UserGigs(BaseModel):
    active: dict = {}
    completed: dict = {}
    archived: dict = {}
    pending: dict = {}

class GigsCount(BaseModel):
    active: int = 0
    completed: int = 0
    archived: int = 0
    pending: int = 0

class BaseUser(BaseModel):
    telegram_id: int = 0
    username: str = ""
    mode: int = 0
    user_data: UserData = UserData()
    gigs: UserGigs = UserGigs()

class Town(BaseModel):
    type: str = ""
    name: str = ""

class Location(BaseModel):
    latitude: float = 0.0
    longitude: float = 0.0
    data: Town = Town()

class GigData(BaseModel):
    name: str = ""
    description: str = ""
    address: dict = {}
    date: int = 0
    tags: list = []
    location: Location = Location()

class BaseGig(BaseModel):
    telegram_id: int = 0
    id: str = ""
    mode: int = 0
    status: int = 0
    data: GigData = GigData()

class GigsResponse(BaseModel):
    key: Union[int, str] = ""
    pages: int = 0
    page: int = 0
    gigs: int = 0
    status: str = "active"
    count: GigsCount = GigsCount()

class GigsEnum(Enum):
    active: str = "active"
    completed: str = "completed"
    archived: str = "archived"
    pending: str = "pending"

class DateEnum(Enum):
    oldest: str = "oldest"
    latest: str = "latest"

    @property
    def _value(self):
        return self.value

    @_value.getter
    def _value(self):
        return self.value == self.latest.value

class UserCreate(BaseModel):
    telegram_id: int = 0
    username: str = ""
    user_data: Description = Description()

class GigCreate(BaseModel):
    telegram_id: int = 0
    mode: int = 0
    data: GigData = GigData()

# class UpdateUsername(BaseModel):
#     username: str = ""

class UpdateDescription(BaseModel):
    telegram_id: int = 0
    user_data: Description = Description()

class UpdateMode(Mode):
    pass

# class UpdateDescription(Description):
#     pass