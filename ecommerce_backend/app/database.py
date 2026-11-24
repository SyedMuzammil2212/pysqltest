from sqlalchemy import create_engine,Column,String,Integer,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, sessionmaker,relationship,Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.config import settings

DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass

session_local = sessionmaker(autocommit=False,autoflush=False,bind=engine)


Base.metadata.create_all(bind=engine)

def get_db():
    db = session_local()
    try:
        yield db

    finally:
        db.close()

