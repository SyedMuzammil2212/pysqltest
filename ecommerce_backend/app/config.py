
# 
# from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from decimal import Decimal

# BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DELIVERY_FEE: Decimal = Decimal("0.00")

    SMTP_HOST: str
    SMTP_PORT: int

    SMTP_USERNAME: str
    SMTP_PASSWORD: str

    SMTP_USE_TLS: bool

    MAIL_FROM: str
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()  # pyright: ignore[reportCallIssue]

