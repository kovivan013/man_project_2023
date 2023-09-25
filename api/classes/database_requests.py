from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

class RequestSender(ABC):

    def _as_dict(self, data) -> dict:
        return dict(data)

    def __init__(self, data: dict = None):
        self._payload = self._as_dict(data)

    @abstractmethod
    def _send(self):
        pass

    def post_request(self, db: Session):
        pass

    def put_request(self):
        pass

    def patch_request(self):
        pass

    def delete_request(self):
        pass


