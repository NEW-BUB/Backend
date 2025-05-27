from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    NAVER_CLIENT_ID: str
    NAVER_CLIENT_SECRET: str
    NEWS_API_KEY: str
    THE_NEWS_API_KEY: str
    BILL_INFO_API_KEY: str
    INTEGRATED_BILL_INFO_API_KEY: str
    GEMINI_API_KEY: str
    USER: str
    PASSWORD: str
    HOST: str
    PORT: int
    DBNAME: str

    class Config:
        env_file = ".env"

settings = Settings()