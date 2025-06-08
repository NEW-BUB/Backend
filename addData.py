from typing import List

from fastapi import FastAPI
from app.database import engineconn
from app import models
from app.models import *
import uvicorn
import json
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from app.models import *

app = FastAPI()


engine = engineconn()

models.Base.metadata.create_all(bind=engine.engine)

session = engine.sessionmaker()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

@app.get("/")
def main():
  
  news_model = models.News(title="title1",
                            date="1998-12-31 23:59:59",
                            img="img1",
                            author="['작성자1', '작성자2']",
                            link="link1")
  
  
  session.add(news_model)
  session.commit()
  return ""