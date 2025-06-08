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

import csv
import ast
from datetime import datetime

@app.get("/")
def main():
  news_files = ["연합뉴스 데이터.csv", "경향신문 데이터.csv", "동아일보 데이터.csv", "한겨레 데이터.csv", "jtbc 데이터.csv"]
  csv_file = news_files[0]
  try:
    with open(csv_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        existing_data = {row["link"]: row for row in reader}
  except FileNotFoundError:
      existing_data = {}
  
  # date_format에 맞는 날짜 형식으로 입력해야 함
  date_format = "%a, %d %b %Y %H:%M:%S %z"

  # 예외 처리 및 효율적인 데이터 삽입
  for key in existing_data.keys():
    try:
      # 날짜 문자열을 datetime 객체로 변환
      date_str = existing_data[key]["pubDate"]
      dt = datetime.strptime(date_str, date_format)
      date = dt.replace(tzinfo=None)  # tzinfo 제거
      

      author = ast.literal_eval(existing_data[key]["author"])
      if not author:
        author = None
      
      text = existing_data[key]["text"] 
      # text = text.replace("'", "''") 
      print(text)

      # News 모델 생성
      news_model = models.News(
        title=existing_data[key]["title"],
        date=date,
        img=existing_data[key]["img_src"],
        author=author,
        link=existing_data[key]["link"],
        text=text
      )

      # 세션에 뉴스 모델 추가
      session.add(news_model)

    except Exception as e:
        print(f"Error processing record {key}: {e}")

# 모든 데이터를 추가한 후 한 번만 커밋
  session.commit()
  
  
  return ""