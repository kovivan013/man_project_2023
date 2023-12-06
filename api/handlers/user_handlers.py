import datetime

from fastapi import APIRouter, Depends, Response, Request
from starlette import status
from sqlalchemy.orm import Session

from man_project_2023.api.db_connect.db_connect import get_db
from man_project_2023.api.models.models import User
from man_project_2023.api.classes.db_requests import PostRequest
from man_project_2023.api.schemas.request_schemas import UserCreate, GigCreate, UpdateUser, BaseUser, BaseGig
from man_project_2023.api.schemas.data_schemas import DataStructure
from man_project_2023.api.utils import exceptions
from man_project_2023.api.utils.utils import Utils

user_router = APIRouter()

utils = Utils()

@user_router.post("/create_user")
def create_user(request_data: UserCreate.Request, response: Response, request: Request, db: Session = Depends(get_db)):
    result = DataStructure()
    user_exists = db.query(User).filter(User.telegram_id == request_data.telegram_id).first() is not None
    if user_exists:
        raise exceptions.ItemExistsException

    data = BaseUser(data=request_data.as_dict())

    result.status = status.HTTP_201_CREATED
    result._success()
    result.message = "test"
    result.data = data.as_dict()

    return PostRequest(db=db,
                       response=response,
                       data=data.as_dict(),
                       result=result).send_request()

@user_router.post("/create_gig")
def create_gig(request_data: GigCreate.Request, response: Response, request: Request, db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == request_data.telegram_id).first()
    if user is None:
        raise exceptions.ItemNotFoundException
    user_instance = BaseUser(data=user.as_dict())
    print(user_instance.as_dict())
    data = BaseGig(data=request_data.as_dict())

    data.id = utils.get_uuid()

    user_instance.gigs.active[data.id] = data.id=data.as_dict()
    user.gigs = user_instance.gigs.as_dict()
    print(user.gigs)
    db.commit()

    result.data = data.as_dict()
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


@user_router.patch("/update_description")
def update_description(request_data: UpdateUser.Description, response: Response, db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == request_data.telegram_id).first()

    if user is None:
        raise exceptions.ItemNotFoundException
    user_instance = BaseUser(data=user.as_dict())

    user_instance.user_data.description = request_data.description

    user.user_data = user_instance.user_data.as_dict()
    db.commit()

    result.data = request_data.as_dict()
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

