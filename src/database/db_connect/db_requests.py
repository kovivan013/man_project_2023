from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

from api.models.models import User
from api.handlers.user_handlers import Response
from utils.schemas.schemas import DataStructure

class RequestSender(ABC):

    def _as_dict(self, data) -> dict:
        return dict(data)

    def __init__(self, db: Session, response: Response,
                 data: dict = None, result: DataStructure = None):
        self.db = db
        self.response = response
        self._payload = self._as_dict(data)
        self.result = result

    @abstractmethod
    def _send(self, data: dict,
              result: dict):
        pass

    def send_request(self):
        try:
            data_for_send = User(**self._payload)
            answer = self._send(data=data_for_send,
                                result=self.result)
            self.db.commit()
        except Exception as err:
            raise Exception(err)

        return answer


class PostRequest(RequestSender):
    def _send(self, data, result: dict):
        self.db.add(data)
        return result

class PutRequest(RequestSender):
    def _send(self, data, result: dict):
        self.db.refresh(data)
        return {}

class PatchRequest(RequestSender):
    def _send(self, data, result: dict):
        self.db.refresh(data)
        return {}

class DeleteRequest(RequestSender):
    def _send(self, data, result: dict):
        self.db.delete(data)
        return {}





