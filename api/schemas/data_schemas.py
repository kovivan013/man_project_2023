from pydantic import BaseModel
from man_project_2023.api.utils.utils import Utils


class DataStructure(BaseModel):
    status: int = 200
    success: bool = False
    message: str = ""
    data: dict = {}

    def _success(self):
        self.success = True

    def _as_dict(self) -> dict:
        return self.__dict__

