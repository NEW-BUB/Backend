from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

USER = settings.USER
PASSWORD = settings.PASSWORD
HOST = settings.HOST
PORT = settings.PORT
DBNAME = settings.DBNAME

print(USER)

DB_URL = 'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'.format(
    USER=USER,
    PASSWORD=PASSWORD,
    HOST=HOST,
    PORT=PORT,
    DBNAME=DBNAME
)
print("----------------------------------------"+DB_URL)

class engineconn:

    def __init__(self):
        self.engine = create_engine(DB_URL, pool_recycle = 500)

    def sessionmaker(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

    def connection(self):
        conn = self.engine.connect()
        return conn