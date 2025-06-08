from typing import List

from fastapi import FastAPI
from app.database import engineconn
from app import models
from app.models import *
import uvicorn
import json
from fastapi.middleware.cors import CORSMiddleware
import os

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
from datetime import datetime, date

def getCategory(key):
  news_source = {
    "연합뉴스": {
      "categories": [
        "정치",
        "경제",
        "경제",
        "산업",
        "사회",
        "지역",
        "국제",
        "문화·라이프",
        "건강",
        "문화·라이프",
        "스포츠"
      ],
      "csv_file": "연합뉴스 데이터.csv",
    },
    "경향신문": {
      "categories": [
        "정치",
        "경제",
        "사회",
        "지역",
        "국제",
        "문화·라이프",
        "스포츠",
        "과학",
        "문화·라이프"
      ],
      "csv_file": "경향신문 데이터.csv",
    },
    "동아일보": {
      "categories": [
        "정치",
        "사회",
        "경제",
        "국제",
        "과학",
        "문화·라이프",
        "스포츠",
        "건강"
      ],
      "csv_file": "동아일보 데이터.csv",
    },
    "한겨레": {
      "categories": [
        "정치",
        "경제",
        "사회",
        "국제",
        "문화·라이프",
        "스포츠",
        "과학"
        ],
      "csv_file": "한겨레 데이터.csv",
    },
    "jtbc": {
      "categories": [
        "정치",
        "경제",
        "사회",
        "국제",
        "문화·라이프",
        "문화·라이프",
        "스포츠"
      ],
      "csv_file": "jtbc 데이터.csv",
    }
  }
  
  return list(set([category for category in news_source[key]["categories"]]))

def getCategoryId(categories):
  try:
      # categories 리스트에서 각 카테고리에 해당하는 id를 조회
    category_data = session.query(Category.name, Category.id).filter(Category.name.in_(categories)).all()

    # dictionary 형태로 category를 key, id를 value로 설정
    category_dict = {name: category_id for name, category_id in category_data}

    return category_dict
  except Exception as e:
    print("Error:", e)
    return {}

def getKeywordId(keywords):
  try:
      # categories 리스트에서 각 카테고리에 해당하는 id를 조회
    keyword_data = session.query(Keyword.name, Keyword.id).filter(Keyword.name.in_(keywords)).all()

    # dictionary 형태로 category를 key, id를 value로 설정
    keyword_dict = {name: keyword_id for name, keyword_id in keyword_data}

    return keyword_dict
  except Exception as e:
    print("Error:", e)
    return {}
  
def getPartyId():
  try:
      # categories 리스트에서 각 카테고리에 해당하는 id를 조회
    party_data = session.query(Party.name, Party.id).all()

    # dictionary 형태로 category를 key, id를 value로 설정
    party_dict = {name: party_id for name, party_id in party_data}

    return party_dict
  except Exception as e:
    print("Error:", e)
    return {}

def createCategories():
  categories = getCategory("연합뉴스")
  
  for category in categories:
    try:
      category_model = models.Category(
        name=category
      )
      
      session.add(category_model)

    except Exception as e:
        print(f"Error processing record {category}: {e}")

def createNews():
  news_files = ["연합뉴스 데이터.csv", "경향신문 데이터.csv", "동아일보 데이터.csv", "한겨레 데이터.csv", "jtbc 데이터.csv"]
  news_keys = ["연합뉴스", "경향신문", "동아일보", "한겨레", "jtbc"]
  
  categories = getCategory(news_keys[0])
  category_ids = getCategoryId(categories)
  
  for csv_file in [news_files[0]]:
    try:
      with open(csv_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        existing_data = {row["link"]: row for row in reader}
    except FileNotFoundError:
      existing_data = {}
    
    # 날짜 형식에 맞춰 파싱
    date_format = "%a, %d %b %Y %H:%M:%S %z"

    for key in existing_data.keys():
      try:
        # 날짜 문자열을 datetime 객체로 변환
        date_str = existing_data[key]["pubDate"]
        dt = datetime.strptime(date_str, date_format)
        dt = dt.replace(tzinfo=None)  # tzinfo 제거

        categories = ast.literal_eval(existing_data[key]["categories"])
        keywords = ast.literal_eval(existing_data[key]["keywords"])
        author = ast.literal_eval(existing_data[key]["author"])
        
        if not author:
          author = None
        text = existing_data[key]["text"] 

        # 뉴스 모델 생성
        news_model = models.News(
          title=existing_data[key]["title"],
          date=dt,
          img=existing_data[key]["img_src"],
          author=author,
          link=existing_data[key]["link"],
          text=text
        )
        
        session.add(news_model)
        
        session.commit()
        
        print(news_model.id)
        
        # 카테고리별 뉴스 모델 추가
        for category in categories:
          if category in category_ids:  # category가 category_ids에 존재하는지 확인
            category_news_model = models.CategoryNews(
              category_id=category_ids[category],
              news_id=news_model.id
            )
            session.add(category_news_model)
        
        keyword_ids = getKeywordId(keywords)
        for keyword in keywords:
          keyword_news_model = models.KeywordNews(
            keyword_id=keyword_ids[keyword],
            news_id=news_model.id
          )
          session.add(keyword_news_model)

      except Exception as e:
        print(f"Error processing record {key}: {e}")

    # 데이터베이스에 한 번에 커밋
    session.commit()

def createBills():
  bill_file = "bill_data.csv"
  try:
    with open(bill_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        existing_data = {row["number"]: row for row in reader}
  except FileNotFoundError:
      existing_data = {}
  
  # date_format에 맞는 날짜 형식으로 입력해야 함
  date_format = "%Y-%m-%d"

  party_ids = getPartyId()

  # 예외 처리 및 효율적인 데이터 삽입
  for key in existing_data.keys():
    try:
      # 날짜 문자열을 datetime 객체로 변환
      date_str = existing_data[key]["date"]
      dt = datetime.strptime(date_str, date_format)  # 문자열을 datetime으로 변환
      dt = dt.replace(tzinfo=None)  # tzinfo 제거

      parties = ast.literal_eval(existing_data[key]["parties"])
      proponent = ast.literal_eval(existing_data[key]["proponents"])[0]
      keywords = ast.literal_eval(existing_data[key]["keywords"])
        
      if not proponent:
        proponent = None
        proponents = []

      # News 모델 생성
      law_model = models.Law(
        name=existing_data[key]["name"],
        number=existing_data[key]["number"],
        proponent=proponent,
        date=dt,
        processing_status=existing_data[key]["processing_status"],
        processing_result=existing_data[key]["processing_result"],
        summary=existing_data[key]["summary"],
        link=existing_data[key]["link"],
      )

      # 세션에 뉴스 모델 추가
      session.add(law_model)
      
      session.commit()
      
      print(law_model.id)
      
      for party in set(parties):
        print(parties.count(party))
        print(party_ids[party])
        law_party_model = models.LawPartyContribution(
          law_id=law_model.id,
          party_id=party_ids[party],
          count=parties.count(party)
        )
        session.add(law_party_model)
      
      keyword_ids = getKeywordId(keywords)
      for keyword in keywords:
        keyword_news_model = models.KeywordLaw(
          keyword_id=keyword_ids[keyword],
          law_id=law_model.id
        )
        session.add(keyword_news_model)

    except Exception as e:
        print(f"Error processing record {key}: {e}")
  session.commit()

def createKeywords(file):
  try:  
    with open(file, "r", encoding="utf-8") as f:
      existing_data = json.load(f)
      key_list = [key for key in existing_data.keys()]
  except FileNotFoundError:
    existing_data = {}
  
  try:  
    with open("party_keywords.json", "r", encoding="utf-8") as f:
      party_data = json.load(f)
  except FileNotFoundError:
    party_data = {}
  
  categories = getCategory("연합뉴스")
  category_ids = getCategoryId(categories)
  
  print(categories)

  party_ids = getPartyId()

  # 예외 처리 및 효율적인 데이터 삽입
  for item in key_list[:]:
    try:
      # News 모델 생성
      keyword_model = models.Keyword(
        name=item,
        count=0,
      )

      session.add(keyword_model)
        
      session.commit()
      
      print(keyword_model.id)
      
      # 카테고리별 뉴스 모델 추가
      for category in existing_data[item]:
        if category in category_ids:  # category가 category_ids에 존재하는지 확인
          category_news_model = models.CategoryKeyword(
            category_id=category_ids[category],
            keyword_id=keyword_model.id
          )
          session.add(category_news_model)
          
      for party in party_data.keys():
        print(f"{item}, {party} : {party_data[party].count(item)}")
        if item in party_data[party]:  # category가 category_ids에 존재하는지 확인
          keyword_party_model = models.KeywordPartyContribution(
            party_id=party_ids[party],
            keyword_id=keyword_model.id,
            count=party_data[party].count(item)
          )
          session.add(keyword_party_model)

    except Exception as e:
      print(f"Error processing record {item}: {e}")
    
  session.commit()

def createParties():
  parties = [
    {
      "name": "더불어민주당",
      "eraco":22,
      "seat":167,
      "img":"https://github.com/user-attachments/assets/2428aca4-81bb-4475-926f-8353b49f9fbe",
    },
    {
      "name": "국민의힘",
      "eraco":22,
      "seat":107,
      "img":"https://github.com/user-attachments/assets/b10c3de8-fad2-467f-8c7a-fb9e2b3873fc",
    },
    {
      "name": "조국혁신당",
      "eraco":22,
      "seat":12,
      "img":"https://github.com/user-attachments/assets/6459c62b-5ec5-4463-93c3-aa36f2fc9f4e",
    },
    {
      "name": "개혁신당",
      "eraco":22,
      "seat":3,
      "img":"https://github.com/user-attachments/assets/37b348e3-7515-499c-8ec4-6a5e04d67338",
    },
    {
      "name": "진보당",
      "eraco":22,
      "seat":3,
      "img":"https://github.com/user-attachments/assets/40c2e944-d234-458d-944a-f5e4c9300a66",
    },
    {
      "name": "기본소득당",
      "eraco":22,
      "seat":1,
      "img":"https://github.com/user-attachments/assets/217bbaba-03f1-4d8a-bb10-3afeb16fcfb9",
    },
    {
      "name": "사회민주당",
      "eraco":22,
      "seat":1,
      "img":"https://github.com/user-attachments/assets/62e4ccc9-310d-4b3c-87f9-8130ff5986b5",
    },
    {
      "name": "무소속",
      "eraco":22,
      "seat":2,
      "img":"https://github.com/user-attachments/assets/2f042fcd-a721-4739-9b05-79e2f1a18006",
    },
  ]
  
  # 예외 처리 및 효율적인 데이터 삽입
  for party in parties:
    try:
      party_model = models.Party(
        name=party["name"],
        eraco=party["eraco"],
        seat=party["seat"],
        img=party["img"]
      )
      
      session.add(party_model)

    except Exception as e:
        print(f"Error processing record {party}: {e}")


@app.get("/")
def main():
  createCategories()
  createParties()
  createKeywords("keyword_category.json")
  createNews()
  createBills()

  session.commit()
  
  return ""