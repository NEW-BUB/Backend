from pydantic_settings import BaseSettings

class Settings(BaseSettings):
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