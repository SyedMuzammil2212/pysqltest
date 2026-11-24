from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main.models import Base
import os 
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine,
                            autoflush=False,
                            autocommit= False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()
        
    
def create_tables():
    Base.metadata.create_all(bind=engine)
    
    
    
