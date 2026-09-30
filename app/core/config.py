import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Personal Learning OS"
    app_env: str = "development"
    database_url: str = "sqlite:///./learning_os.db"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

def allowed_origins():
    raw=os.getenv("ALLOWED_ORIGINS","http://localhost:3000,http://127.0.0.1:3000")
    return [x.strip().rstrip("/") for x in raw.split(",") if x.strip()]

def is_production():
    return os.getenv("APP_ENV","development").lower()=="production"
