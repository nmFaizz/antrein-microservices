import os

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(find_dotenv())


class Settings(BaseSettings):
    PROJECT_NAME: str = "User Service"
    API_V1_STR: str = "/api/v1"

    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "jwt-secret",
    )

    JWT_ALGORITHM: str = "HS256"

    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv(
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
            "60",
        )
    )

    @property
    def DATABASE_URL(self) -> str:
        host = (
            os.getenv("USER_DB_HOST")
            or os.getenv("DB_HOST")
            or "localhost"
        )

        port = (
            os.getenv("USER_DB_PORT")
            or os.getenv("DB_PORT")
            or "5432"
        )

        name = (
            os.getenv("USER_DB_NAME")
            or os.getenv("DB_NAME")
            or "user_db"
        )

        user = (
            os.getenv("USER_DB_USER")
            or os.getenv("DB_USER")
            or "postgres"
        )

        password = (
            os.getenv("USER_DB_PASSWORD")
            or os.getenv("DB_PASSWORD")
            or ""
        )

        return (
            f"postgresql://"
            f"{user}:{password}@{host}:{port}/{name}"
        )


settings = Settings()