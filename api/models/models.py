from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, BigInteger, JSON, SmallInteger, DateTime

BaseModel = declarative_base()

class User(BaseModel):
    __tablename__ = "users"
    telegram_id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, default="")
    user_data = Column(JSON, default={})
    gigs = Column(JSON, default={})
    mode = Column(SmallInteger, default=0)
    created_at = Column(BigInteger, default=0)
    phone_number = Column(BigInteger, default=0)
    messages = Column(JSON, default={})

    def as_dict(self) -> dict:
        return self.__dict__

