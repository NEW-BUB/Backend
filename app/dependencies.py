from sqlalchemy.orm import Session
from .database import engineconn

def get_db():
    engine = engineconn()
    session = engine.sessionmaker()
    try:
        yield session
    finally:
        session.close()
