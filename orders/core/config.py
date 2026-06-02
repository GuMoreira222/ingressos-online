from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str
    VERSION: str
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    EVENTS_SERVICE_URL: str
    PAYMENTS_SERVICE_URL: str
    HTTP_TIMEOUT_SECONDS: float = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
