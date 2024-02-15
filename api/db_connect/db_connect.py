from api.config import db

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(db.get_db_endpoint())
localSession = sessionmaker(autoflush=False, autocommit=False, bind=engine)

engine.dispose()

def get_db():
    db = localSession()
    try:
        yield db
    except:
        db.close()
