from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from man_project.api.database.db_connect.db_connect import get_db
from man_project.api.database.models.models import User
from man_project.api.database.schemas.request_schemas import UserCreate
from man_project.api.database.utils import exceptions
from man_project.api.database.utils.utils import as_dict

user_router = APIRouter()


@user_router.post("/create_user")
def create_user(user_params: UserCreate, db: Session = Depends(get_db())):
    is_user_exists: bool = db.query(User).filter(User.telegram_id == user_params.telegram_id) \
                           is not None
    if is_user_exists:
        raise exceptions.ItemExistsException
    payload = User(**as_dict(user_params))
    db.add(payload)
    db.commit()


