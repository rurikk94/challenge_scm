
import os
from sqlalchemy.engine import url as sql_url
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: sql_url.URL = sql_url.URL.create(
                drivername="mysql+pymysql",
                username=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASS'),
                database=os.environ.get('DB_NAME'),
                host=os.environ.get('DB_HOST'),
                query={'charset': 'utf8mb4'}
            )

    TEMPLATES_FOLDER: str = str(Path(__file__).resolve().parent / "templates")

    RESULT_REPORTS_FOLDER: str = str(Path(__file__).resolve().parent / "res")

settings = Settings()