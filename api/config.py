import os

from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 8008


load_dotenv()


class Database:
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    # POSTGRES_DB = "man_project_db"
    # POSTGRES_HOST = "localhost"
    # POSTGRES_PORT = 5433
    # POSTGRES_USER = "postgres"
    # POSTGRES_PASSWORD = "Agent181519137722micro"
    def get_db_endpoint(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
db = Database()
