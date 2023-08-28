import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.config import settings

engine = create_engine(
    settings.DB_URL,
    pool_size=20,
    max_overflow=20,
    pool_timeout=60,
)

Base = declarative_base()

Session = sessionmaker(bind=engine)
