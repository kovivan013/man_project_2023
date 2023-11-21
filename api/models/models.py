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

    pass1 = Column(String, default=1)
    pass2 = Column(String, default=1)

    created_at = Column(BigInteger, default=0)
    updated_at = Column(BigInteger, default=0)

    def as_dict(self) -> dict:
        return self.__dict__
