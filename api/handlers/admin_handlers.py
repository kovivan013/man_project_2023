from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from man_project_2023.api.db_connect.db_connect import get_db
from man_project_2023.api.models.models import User
from man_project_2023.api.schemas.request_schemas import UserCreate
from man_project_2023.api.utils import exceptions
from man_project_2023.api.utils.utils import as_dict

admin_router = APIRouter()
