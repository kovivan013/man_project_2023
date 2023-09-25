from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from man_project_2023.api.db_connect.db_connect import get_db
from man_project_2023.api.models.models import User
from man_project_2023.api.schemas.request_schemas import UserCreate
from man_project_2023.api.utils import exceptions
from man_project_2023.api.utils.utils import as_dict

user_router = APIRouter()


@user_router.post("/create_user")
def create_user(user_params: UserCreate, db: Session = Depends(get_db)):
    user_exists = db.query(User).filter(User.telegram_id == user_params.telegram_id).first() is not None
    if user_exists:
        raise exceptions.ItemExistsException
    data: dict = dict(user_params)
    payload = User(**data)
    db.add(payload)
    db.commit()

# @user_router.post("/create_user")
# def create_user(user: UserCreate, db: Session = Depends(get_db)):
#
# user_exists = db.query(User).filter(User.telegram_id == user.telegram_id).first() is not None
# if user_exists:
#     raise exceptions.ItemExistsException
#     data: dict = dict(user)
#
#     new_user = User(**data)
#     db.add(new_user)
#     db.commit()
#     return {}
