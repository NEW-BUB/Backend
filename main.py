from fastapi import FastAPI
from app.database import engineconn
from app import models
from app.models import *

app = FastAPI()

engine = engineconn()

models.Base.metadata.create_all(bind=engine.engine)

session = engine.sessionmaker()

@app.get("/")
def main():
    return ""

@app.get("/hello")
def hello():
    return {"message": "hello world"}

@app.get("/news")
async def get_news():
    example = session.query(News).all()
    return example