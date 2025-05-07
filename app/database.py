from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Python 기본 패키지에 포함 되어있는 sqlite 사용
SQLALCHEMY_DATABASE_URL = "sqlite:///./fastapi-scrap.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# DB 세션 객체 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()