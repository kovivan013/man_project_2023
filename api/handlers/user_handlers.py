import datetime

from fastapi import APIRouter, Depends, Response, Request
from starlette import status
from sqlalchemy.orm import Session

from man_project_2023.api.db_connect.db_connect import get_db
from man_project_2023.api.models.models import User
from man_project_2023.api.classes.db_requests import PostRequest
from man_project_2023.api.schemas.request_schemas import UserCreate, UpdateUser, BaseUser
from man_project_2023.api.schemas.data_schemas import DataStructure
from man_project_2023.api.utils import exceptions
from man_project_2023.api.utils.utils import as_dict

user_router = APIRouter()


@user_router.post("/create_user")
def create_user(user: UserCreate, response: Response, request: Request, db: Session = Depends(get_db)):
    result = DataStructure()
    user_exists = db.query(User).filter(User.telegram_id == user.telegram_id).first() is not None
    if user_exists:
        raise exceptions.ItemExistsException

    data: dict = {
          "telegram_id": user.telegram_id,
          "username": user.username,
          "user_data": {
              "description": user.description,
              "badges": []
          }
        }

    result.status = status.HTTP_201_CREATED
    result.success = True
    result.message = "test"

    return PostRequest(db=db,
                       response=response,
                       data=data,
                       result=result).send_request()


@user_router.get("/{telegram_id}/user_data")
def user_data(telegram_id: int, db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user is None:
        raise exceptions.ItemNotFoundException

    result.success = True
    result.data = user.user_data

    return result


@user_router.patch("/update_description")
def update_description(data: UpdateUser, response: Response, db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == data.telegram_id).first()
    if user is None:
        raise exceptions.ItemNotFoundException

    user_data: dict = dict(user.user_data)

    user_data["description"] = data.description
    user.user_data = user_data
    db.commit()

    result.success = True
    return result


@user_router.get("/{telegram_id}/mode")
def user_mode(telegram_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user is None:
        raise exceptions.ItemNotFoundException

    return user.mode

