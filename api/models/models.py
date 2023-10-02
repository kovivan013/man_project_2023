from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, BigInteger, JSON, SmallInteger

BaseModel = declarative_base()

class User(BaseModel):
    __tablename__ = "users"
    telegram_id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, default="")
    userinfo = Column(JSON, default={})
    mode = Column(SmallInteger, default=0)

    def as_dict(self) -> dict:
        return self.__dict__
