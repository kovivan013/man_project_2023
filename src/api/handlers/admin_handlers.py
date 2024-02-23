from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db_connect.db_connect import get_db
from models.models import User
from schemas.schemas import UserCreate
from schemas.data_schemas import DataStructure
from services import exceptions

admin_router = APIRouter()
