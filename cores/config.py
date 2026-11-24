from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME : str = "E-commerce"
    APP_VERSION : str = "1.0.0"
    DEBUG : bool = False

    DATABASE_URL : str

    DELIVERY_FEE : float

    JWT_SECRET_KEY : str
    JWT_ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int

    SMTP_HOST : str
    SMTP_PORT : int
    SMTP_USERNAME : str
    SMTP_PASSWORD : str
    # SMTF_USE_TLS : bool
    MAIL_FROM : str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()