from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

from man_project_2023.api.models.models import User

class RequestSender(ABC):

    def _as_dict(self, data) -> dict:
        return dict(data)

    def __init__(self, db: Session, data: dict = None):
        self.db = db
        self._payload = self._as_dict(data)

    @abstractmethod
    def _send(self):
        pass

    def send_request(self):
        try:
            data_for_send = User(**self._payload)
            answer = self._send(data_for_send)
            self.db.commit()
        except Exception as err:
            raise Exception(err)

        return answer


class PostRequest(RequestSender):
    def _send(self, data):
        self.db.add(data)
        return {}

class PutRequest(RequestSender):
    def _send(self, data):
        self.db.refresh(data)
        return {}

class PatchRequest(RequestSender):
    def _send(self, data):
        self.db.refresh(data)
        return {}

class DeleteRequest(RequestSender):
    def _send(self, data):
        self.db.delete(data)
        return {}





