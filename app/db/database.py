import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect
from langchain_community.utilities import SQLDatabase

from app.config.env_config import settings

engine = create_engine(
    f"mysql+pymysql://{settings.MYSQL_USERNAME}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:3306/{settings.MYSQL_DB_NAME}"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

inspector = inspect(engine)
sql_db = SQLDatabase(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        print(f"Database session exception: {str(e)}")
        raise
    finally:
        db.close()

def get_schema_text():
    schema_text = ""
    for table in inspector.get_table_names():
        schema_text += f"\nTable: {table}\n"

        columns = inspector.get_columns(table)
        for col in columns:
            schema_text += f" - {col['name']} ({col['type']})\n"

    return schema_text