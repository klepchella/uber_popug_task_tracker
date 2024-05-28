from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from task_tracker.settings import settings_


engine = create_engine(
    f"postgresql://{settings_.postgres_user}:{settings_.postgres_password}@{settings_.postgres_host}:5432/{settings_.postgres_db}",
)
Base = declarative_base()
session = sessionmaker(engine, class_=Session)

metadata = MetaData()
