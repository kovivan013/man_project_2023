from fastapi import APIRouter, Depends, Response
from starlette import status
from sqlalchemy.orm import Session

from man_project_2023.api.db_connect.db_connect import get_db
from man_project_2023.api.models.models import User
from man_project_2023.api.classes.db_requests import PostRequest
from man_project_2023.api.schemas.request_schemas import UserCreate
from man_project_2023.api.utils import exceptions
from man_project_2023.api.utils.utils import as_dict

user_router = APIRouter()


@user_router.post("/create_user")
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    user_exists = db.query(User).filter(User.telegram_id == user.telegram_id).first() is not None
    if user_exists:
        raise exceptions.ItemExistsException

    response.status_code = status.HTTP_201_CREATED
    return PostRequest(db=db,
                       data=user).send_request()

@user_router.get("/{telegram_id}/mode")
def get_user_mode(telegram_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user is None:
        raise exceptions.ItemNotFoundException

    return user.mode