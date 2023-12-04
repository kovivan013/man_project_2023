from pydantic import BaseModel
from man_project_2023.api.utils.utils import Utils


class DataStructure(BaseModel):
    status: int = 200
    success: bool = False
    message: str = ""
    data: dict = {}

    def _as_dict(self) -> dict:
        return self.__dict__


class Str(Utils):

    def __init__(self):
        self.data = self.Data()

    class Data:
        def __init__(self):
            self.status: int = 200
            self.success: bool = False
            self.message: str = ""

#
# s = Str()
# print(s.as_dict())
# print(as_dict(data=s.as_dict()))


# print(s.as_dict(data=s.data))

