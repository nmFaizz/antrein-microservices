import os
from dotenv import load_dotenv, find_dotenv
from pydantic_settings import BaseSettings

load_dotenv(find_dotenv())

class Settings(BaseSettings):
    PROJECT_NAME: str = "Menu Preorder Service"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    QUEUE_SERVICE_URL: str = os.getenv("QUEUE_SERVICE_URL") or "http://queue-service:8000"
    
    @property
    def DATABASE_URL(self) -> str:
        # Read from OS environment variables (hydrated from .env or docker env)
        host = os.getenv("MENU_PREORDER_DB_HOST") or os.getenv("DB_HOST") or "localhost"
        port = os.getenv("MENU_PREORDER_DB_PORT") or os.getenv("DB_PORT") or "5432"
        name = os.getenv("MENU_PREORDER_DB_NAME") or os.getenv("DB_NAME") or "menu_preorder_db"
        user = os.getenv("MENU_PREORDER_DB_USER") or os.getenv("DB_USER") or "postgres"
        password = os.getenv("MENU_PREORDER_DB_PASSWORD") or os.getenv("DB_PASSWORD") or ""
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"

settings = Settings()
