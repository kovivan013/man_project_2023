from pydantic import BaseModel
from typing import List, Dict

class DataStructure(BaseModel):
    status: int = 200
    success: bool = False
    message: str = ""
    data: dict = {}

    @property
    def _success(self):
        return self.success

    @property
    def _status(self):
        return self.status

    @_status.setter
    def _status(self, _value):
        """
        Устанавливает статус-код
        :param _value: status code
        :return:
        """
        self.status = _value
        if _value in range(200, 300):
            self.success = True

    @_success.getter
    def _success(self):
        """
        Возвращает логическое значение успешно ли прошел запрос с учетом статус-кода
        :return:
        """
        if self.status in range(200, 300) and self.success:
            return True
        return False

