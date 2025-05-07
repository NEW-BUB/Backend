from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    NAVER_CLIENT_ID: str
    NAVER_CLIENT_SECRET: str

    class Config:
        env_file = ".env"

settings = Settings()