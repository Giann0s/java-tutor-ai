from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str
    secret_key_refresh: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    admin_email: str
    admin_password: str
    gemini_api_key: str


    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
