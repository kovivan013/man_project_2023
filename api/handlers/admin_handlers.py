from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from db_connect.db_connect import get_db
from services.errors_reporter import Reporter
from models.models import User
from schemas.schemas import UserCreate, BaseUser, BaseGig
from schemas.data_schemas import DataStructure
from services import exceptions

admin_router = APIRouter()

@admin_router.get("/{telegram_id}/{gig_id}/accept_create")
def accept_create(telegram_id: int, gig_id: str, db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if user is None:
        return Reporter.api_exception(exception=exceptions.ItemNotFoundException,
                                      message="❌ Користувача не існує!")

    gigs = BaseUser().gigs.model_validate(user.gigs)
    pending_gigs = gigs.pending

    if gig_id not in pending_gigs:
        return Reporter.api_exception(exception=exceptions.ItemNotFoundException,
                                      message="❌ Такого оголошення не існує!")

    gig = BaseGig().model_validate(pending_gigs[gig_id])

    pending_gigs.pop(gig_id)
    gig.status = 0
    gigs.active.update({
        gig_id: gig.model_dump()
    })

    user.gigs = gigs.model_dump()
    db.commit()

    result.data = gig.model_dump()
    result.message = "✅ Успішно створено!"
    result._status = status.HTTP_200_OK

    db.close()
    return result

@admin_router.get("/{telegram_id}/{gig_id}/decline_create")
def decline_create(telegram_id: int, gig_id: str, db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if user is None:
        return Reporter.api_exception(exception=exceptions.ItemNotFoundException,
                                      message="❌ Користувача не існує!")

    gigs = BaseUser().gigs.model_validate(user.gigs)
    pending_gigs = gigs.pending.copy()

    if gig_id not in pending_gigs:
        return Reporter.api_exception(exception=exceptions.ItemNotFoundException,
                                      message="❌ Такого оголошення не існує!")
    gigs.pending.pop(gig_id)
    user.gigs = gigs.model_dump()
    db.commit()

    result.data = pending_gigs[gig_id]
    result.message = "✅ Успішно відхилено!"
    result._status = status.HTTP_200_OK

    db.close()
    return result