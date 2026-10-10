from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    admin_email: str
    admin_password: str
    gemini_api_key: str
    # Το URL για το frontend (προσωρινά εδώ για να μην φτιάχνω και άλλο .env)
    # api_base_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
