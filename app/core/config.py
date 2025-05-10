from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    NAVER_CLIENT_ID: str
    NAVER_CLIENT_SECRET: str
    NEWS_API_KEY: str
    THE_NEWS_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()