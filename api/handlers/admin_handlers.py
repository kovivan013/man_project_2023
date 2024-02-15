from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.db_connect.db_connect import get_db
from api.models.models import User
from utils.schemas.api_schemas import UserCreate
from utils.debug import exceptions

admin_router = APIRouter()
