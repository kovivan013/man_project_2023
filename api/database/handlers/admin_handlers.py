from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from man_project.api.database.db_connect.db_connect import get_db
from man_project.api.database.models.models import User
from man_project.api.database.schemas.request_schemas import UserCreate
from man_project.api.database.utils import exceptions
from man_project.api.database.utils.utils import as_dict

admin_router = APIRouter()
