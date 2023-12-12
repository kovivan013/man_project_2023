import datetime
import json

from fastapi import APIRouter, Depends, Response, Request
from starlette import status
from sqlalchemy.orm import Session

from man_project_2023.api.db_connect.db_connect import get_db
from man_project_2023.api.models.models import User
from man_project_2023.api.classes.db_requests import PostRequest
from man_project_2023.api.schemas.request_schemas import UserCreate, GigCreate, UpdateDescription, BaseGig, BaseUser
from man_project_2023.api.schemas.data_schemas import DataStructure
from man_project_2023.api.utils import exceptions
from man_project_2023.api.utils.utils import Utils

user_router = APIRouter()

utils = Utils()


@user_router.post("/create_user")
def create_user(request_data: UserCreate, response: Response, request: Request, db: Session = Depends(get_db)):
    result = DataStructure()
    user_exists = db.query(User).filter(User.telegram_id == request_data.telegram_id).first() is not None
    if user_exists:
        raise exceptions.ItemExistsException

    data = BaseUser().model_validate(request_data.model_dump())

    result.status = status.HTTP_201_CREATED
    result._success()
    result.message = "test"
    result.data = data.model_dump()

    return PostRequest(db=db,
                       response=response,
                       data=result.data,
                       result=result).send_request()


@user_router.post("/create_gig")
def create_gig(request_data: GigCreate, response: Response, request: Request, db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == request_data.telegram_id).first()

    if user is None:
        raise exceptions.ItemNotFoundException

    user_instance = BaseUser().model_validate(user.as_dict())
    data = BaseGig().model_validate(request_data.model_dump())
    data.id = utils.get_uuid()
    user_instance.gigs.active.update({data.id: data.model_dump()})
    user.gigs = user_instance.gigs.model_dump()

    db.commit()
    result.data = data.model_dump()
    result._success()

    return result

@user_router.get("/all_users")
def get_all_users(response: Response, db: Session = Depends(get_db)):
    result = DataStructure()
    users = db.query(User).all()
    for i in users:
        user = BaseUser().model_validate(i.as_dict())
        result.data.update({
            user.telegram_id: user.model_dump()
        })

    return result

@user_router.get("/gigs/active")
def get_active_gigs(response: Response, db: Session = Depends(get_db)):
    result = DataStructure()
    users = db.query(User).all()
    for i in users:
        user = BaseUser().model_validate(i.as_dict())
        if active := user.gigs.active:
            for j, k in active.items():
                result.data.update({
                    j: k
                })

    return result

@user_router.patch("/update_description")
def update_description(request_data: UpdateDescription, response: Response, db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == request_data.telegram_id).first()

    if user is None:
        raise exceptions.ItemNotFoundException

    user_instance = BaseUser().model_validate(request_data.model_dump())
    user.user_data = user_instance.user_data.model_dump()

    db.commit()
    result.data = request_data.model_dump()
    result._success()

    return result

@user_router.get("/{telegram_id}/")
def get_user(telegram_id: int, db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if user is None:
        raise exceptions.ItemNotFoundException

    user_instance = BaseUser().model_validate(user.as_dict())
    result.data = user_instance.model_dump()
    result._success()

    return result

@user_router.get("/{telegram_id}/user_data")
def user_data(telegram_id: int, db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if user is None:
        raise exceptions.ItemNotFoundException

    result.data = user.user_data
    result._success()

    return result


@user_router.get("/{telegram_id}/gigs")
def user_gigs(telegram_id: int, db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if user is None:
        raise exceptions.ItemNotFoundException

    result.data = user.gigs
    result._success()

    return result


@user_router.get("/{telegram_id}/mode")
def user_mode(telegram_id: int, db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user is None:
        raise exceptions.ItemNotFoundException

    result._success()

    return user.mode

