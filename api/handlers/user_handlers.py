import datetime
import json

from fastapi import APIRouter, Depends, Response, Request, Query
from starlette import status
from sqlalchemy.orm import Session

from db_connect.db_connect import get_db
from db_connect.db_requests import PostRequest
from models.models import User
from schemas.schemas import UserCreate, GigCreate, UpdateDescription, BaseGig, BaseUser, GigsEnum, DateEnum, GigsResponse, UpdateMode, Mode, SendMessage
from schemas.data_schemas import DataStructure
from services import exceptions
from services.utils import Utils
from services.errors_reporter import Reporter

user_router = APIRouter()

utils = Utils()

@user_router.post("/create_user")
def create_user(request_data: UserCreate, response: Response, request: Request, db: Session = Depends(get_db)):
    result = DataStructure()
    user_exists = db.query(User).filter(User.telegram_id == request_data.telegram_id).first() is not None
    if user_exists:
        return Reporter.api_exception(exception=exceptions.ItemExistsException,
                                      message="User already exists")

    data = BaseUser().model_validate(request_data.model_dump())
    data.created_at = int(datetime.datetime.now().timestamp())

    result._status = status.HTTP_201_CREATED
    result.data = data.model_dump()

    db.close()
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
    user_instance.gigs.pending.update({data.id: data.model_dump()})
    user.gigs = user_instance.gigs.model_dump()

    db.commit()
    result.data = data.model_dump()
    result._status = status.HTTP_200_OK

    db.close()
    return result


@user_router.get("/all_users")
def get_all_users(response: Response, db: Session = Depends(get_db)):
    result = DataStructure()

    users = db.query(User.telegram_id).all()
    user = db.query(User).filter(User.telegram_id == 345).first()
    result.data = [int(i[0]) for i in users]

    # users = db.query(User).all()
    # for i in users:
    #     user = BaseUser().model_validate(i.as_dict())
    #     result.data.update({
    #         user.telegram_id: user.model_dump()
    #     })
    result._status = status.HTTP_200_OK

    db.close()
    return result


@user_router.get("/all_gigs/")
def get_gigs(limit: int = 1, page: int = 1, type: GigsEnum = Query(default=GigsEnum.active), db: Session = Depends(get_db)):
    result = DataStructure()
    document = GigsResponse()
    gigs = db.query(User.gigs).all()
    all_gigs: list = []

    for i in gigs:
        user = BaseUser().gigs.model_validate(i[0])
        if values := getattr(user, f"{type.value}"):
            for j, k in values.items():
                all_gigs.append({
                    j: k
                })

    if all_gigs:
        end = limit * page
        start = end - limit
        [result.data.update(i) for i in all_gigs]
        sorted_gigs = Utils.sort_by(obj=result.data,
                                    path=["data", "date"])
        result.data.clear()
        for i, v in enumerate(sorted_gigs.items()):
            if i in range(start, end):
                gig_id, data = v
                result.data.update({
                    gig_id: data
                })

    rest = 0
    if len(all_gigs) % limit:
        rest = 1

    document.gigs = len(all_gigs)
    document.pages = len(all_gigs) // limit + rest
    document.page = page

    result.data["response"] = document
    result._status = status.HTTP_200_OK

    db.close()
    return result

@user_router.get("/get_latest_gigs")
def get_latest_gigs(mode: int = 0, city: str = "", limit: int = 1, page: int = 1, from_date: DateEnum = Query(default=DateEnum.latest),
             type: GigsEnum = Query(default=GigsEnum.active), db: Session = Depends(get_db)):
    result = DataStructure()
    document = GigsResponse()
    response: dict = {}
    gigs = db.query(User.gigs).all()
    all_gigs: list = []
    result.data["gigs"] = {}

    for i in gigs:
        user = BaseUser().gigs.model_validate(i[0])
        if values := getattr(user, f"{type.value}"):
            for j, k in values.items():
                gig = BaseGig().model_validate(k)
                if gig.mode == mode:
                    all_gigs.append({
                        j: k
                    })

    if city and city != "all":
        sorted_gigs: list = []
        for i in all_gigs:
            data = BaseGig().model_validate(list(i.values())[0])
            if data.data.location.data.name.lower() in city.lower():
                sorted_gigs.append(i)
        all_gigs = sorted_gigs

    if all_gigs:
        end = limit * page
        start = end - limit
        [response.update(i) for i in all_gigs]
        sorted_gigs = Utils.sort_by(obj=response,
                                    path=["data", "date"],
                                    reverse=from_date._value)
        response.clear()

        for i, v in enumerate(sorted_gigs.items()):
            if i in range(start, end):
                gig_id, data = v
                result.data["gigs"].update({
                    gig_id: data
                })

    rest = 0
    if len(all_gigs) % limit:
        rest = 1

    document.gigs = len(all_gigs)
    document.pages = len(all_gigs) // limit + rest
    document.page = page
    document.status = type.value

    result.data["response"] = document

    result._status = status.HTTP_200_OK

    db.close()
    return result


@user_router.get("/v2/gigs/")
def get_gigs(title: str, city: str = "", limit: int = 1, page: int = 1, from_date: DateEnum = Query(default=DateEnum.latest),
             type: GigsEnum = Query(default=GigsEnum.active), db: Session = Depends(get_db)):
    result = DataStructure()
    document = GigsResponse()
    response: dict = {}
    gigs = db.query(User.gigs).all()
    all_gigs: list = []
    result.data["gigs"] = {}

    for i in gigs:
        user = BaseUser().gigs.model_validate(i[0])
        if values := getattr(user, f"{type.value}"):
            for j, k in values.items():
                gig = BaseGig().model_validate(k)
                if gig.mode:
                # if gig.mode: # парсить только то, что нашел детектив в своем моде (1)
                #TODO: сделать при подключении модов в сервисе
                    name = gig.data.name.lower()
                    if name in title.lower() or title.lower() in name:
                        all_gigs.append({
                            j: k
                        })
                    else:
                        for i in gig.data.tags:
                            if i.lower() in title.lower():
                                all_gigs.append({
                                    j: k
                                })
                                break

    if city and city != "all":
        sorted_gigs: list = []
        for i in all_gigs:
            data = BaseGig().model_validate(list(i.values())[0])
            if data.data.location.data.name.lower() in city.lower():
                sorted_gigs.append(i)
        all_gigs = sorted_gigs

    if all_gigs:
        end = limit * page
        start = end - limit
        [response.update(i) for i in all_gigs]
        sorted_gigs = Utils.sort_by(obj=response,
                                    path=["data", "date"],
                                    reverse=from_date._value)
        response.clear()

        for i, v in enumerate(sorted_gigs.items()):
            if i in range(start, end):
                gig_id, data = v
                result.data["gigs"].update({
                    gig_id: data
                })

    rest = 0
    if len(all_gigs) % limit:
        rest = 1

    document.key = title
    document.gigs = len(all_gigs)
    document.pages = len(all_gigs) // limit + rest
    document.page = page
    document.status = type.value

    result.data["response"] = document

    result._status = status.HTTP_200_OK

    db.close()
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
    result._status = status.HTTP_200_OK

    db.close()
    return result


@user_router.get("/{telegram_id}")
def get_user(telegram_id: int, db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user is None:
        return Reporter.api_exception(exception=exceptions.ItemNotFoundException)
    user_instance = BaseUser().model_validate(user.as_dict())
    result.data = user_instance.model_dump()
    result._status = status.HTTP_200_OK

    db.close()
    return result


@user_router.get("/{telegram_id}/gigs")
def get_user_gigs(telegram_id: int,
                  mode: int,
                  city: str = "",
                  limit: int = 1,
                  page: int = 1,
                  from_date: DateEnum = Query(default=DateEnum.latest),
                  type: GigsEnum = Query(default=GigsEnum.active),
                  db: Session = Depends(get_db)):
    result = DataStructure()
    document = GigsResponse()
    response: dict = {}
    result.data["gigs"] = {}
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if user is None:
        return Reporter.api_exception(exceptions.ItemNotFoundException)

    gigs = BaseUser().gigs.model_validate(user.gigs)
    count_data = document.count.model_dump()
    all_gigs: list = []
    for i, v in gigs.model_dump().items():
        for j, k in v.items():
            if k["mode"] == mode:
                count_data[i] += 1
                if i == type.value:
                    all_gigs.append({
                        j: k
                    })
    document.count = count_data

    if city:
        sorted_gigs: list = []
        for i in all_gigs:
            data = BaseGig().model_validate(list(i.values())[0])
            if data.data.location.data.name.lower() in city.lower():
                sorted_gigs.append(i)
        all_gigs = sorted_gigs

    if all_gigs:
        end = limit * page
        start = end - limit
        [response.update(i) for i in all_gigs]
        sorted_gigs = Utils.sort_by(obj=response,
                                    path=["data", "date"],
                                    reverse=from_date._value)
        response.clear()

        result.data["response"] = document
        for i, v in enumerate(sorted_gigs.items()):
            if i in range(start, end):
                gig_id, data = v
                result.data["gigs"].update({
                    gig_id: data
                })

    rest = 0
    if len(all_gigs) % limit:
        rest = 1

    document.gigs = len(all_gigs)
    document.pages = len(all_gigs) // limit + rest
    document.page = page
    document.status = type.value
    result.data["response"] = document

    result._status = status.HTTP_200_OK

    db.close()
    return result

@user_router.get("/{telegram_id}/gigs/{gig_id}")
def get_gig(telegram_id: int,
            gig_id: str,
            db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if user is None:
        return Reporter.api_exception(exceptions.ItemNotFoundException)

    gigs = BaseUser().gigs.model_validate(user.gigs).model_dump()
    all_gigs: dict = {}
    for i in gigs.values():
        for j, k in i.items():
            all_gigs.update({
                j: k
            })

    if gig_id not in all_gigs:
        return Reporter.api_exception(exceptions.ItemNotFoundException)

    result.data = all_gigs[gig_id]
    result._status = status.HTTP_200_OK

    db.close()
    return result

@user_router.delete("/{telegram_id}/gigs/{gig_id}")
def delete_gig(telegram_id: int,
               gig_id: str,
               db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if user is None:
        return Reporter.api_exception(exception=exceptions.ItemNotFoundException,
                                      message="❌ Виникла несподівана помилка!\nСпробуйте знову.")

    gigs = BaseUser().gigs.model_validate(user.gigs)
    active_gigs = gigs.active

    if gig_id not in active_gigs:
        return Reporter.api_exception(exception=exceptions.ItemNotFoundException,
                                      message="❌ Неможливо видалити це оголошення!")

    gig = BaseGig().model_validate(active_gigs[gig_id])
    if gig.telegram_id != telegram_id:
        return Reporter.api_exception(exception=exceptions.NoAccess,
                                      message="❌ У вас немає дозволу на видалення цього оголошення!")

    active_gigs.pop(gig_id)
    gig.status = 3
    gigs.archived.update({
        gig_id: gig.model_dump()
    })

    user.gigs = gigs.model_dump()
    db.commit()

    result.data = gig.model_dump()
    result.message = "✅ Успішно!"
    result._status = status.HTTP_200_OK

    db.close()
    return result



@user_router.get("/{telegram_id}/user_data")
def user_data(telegram_id: int, db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if user is None:
        raise exceptions.ItemNotFoundException

    result.data = user.user_data
    result._status = status.HTTP_200_OK

    db.close()
    return result


@user_router.get("/{telegram_id}/mode")
def user_mode(telegram_id: int, db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user is None:
        raise exceptions.ItemNotFoundException

    result.data = Mode(mode=user.mode).model_dump()
    result._status = status.HTTP_200_OK

    db.close()
    return result

@user_router.patch("/{telegram_id}/mode")
def update_user_mode(telegram_id: int, request_data: UpdateMode, db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user is None:
        raise exceptions.ItemNotFoundException

    user.mode = request_data.mode
    result.data = request_data.model_dump()
    result._status = status.HTTP_200_OK

    db.commit()
    db.close()
    return result

@user_router.delete("/{telegram_id}/delete_gigs")
def delete_gigs(telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if user is None:
        return Reporter.api_exception(exceptions.ItemNotFoundException)

    gigs = BaseUser().gigs.model_validate(user.gigs)
    gigs.active.clear()
    user.gigs = gigs.model_dump()

    db.commit()
    db.close()

@user_router.get("/{telegram_id}/messages")
def get_messages(telegram_id: int, offset: int = 10, db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if user is None:
        return Reporter.api_exception(exceptions.ItemNotFoundException)
    key = max(list(map(int, user.messages.keys())), default=0)
    partial_data = {}
    print(key)
    if key:
        for i, v in enumerate(range(key, key-offset if offset < key else 0, -1), start=1):
            print(user.messages[str(v)])
            partial_data.update({
                i: user.messages[str(v)]
            })
    else:
        result.message = f"*Поки що, у вас немає повідомлень...*"
    print(partial_data)
    result.data = partial_data
    result._status = status.HTTP_200_OK

    db.close()
    return result

@user_router.post("/{telegram_id}/send_message")
def send_message(telegram_id: int, request_data: SendMessage, db: Session = Depends(get_db)):
    result = DataStructure()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if user is None:
        return Reporter.api_exception(exceptions.ItemNotFoundException)

    request_data.timestamp = int(datetime.datetime.now().timestamp())
    messages: dict = user.messages.copy()
    key = max(list(map(int, messages.keys())), default=0) + 1
    messages.update({
        key: (data := request_data.model_dump())
    })
    user.messages = messages
    db.commit()

    result.data = data
    result._status = status.HTTP_200_OK

    db.close()
    return result
