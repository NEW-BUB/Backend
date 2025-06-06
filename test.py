from typing import List

from fastapi import FastAPI
from app.database import engineconn
from app import models
from app.models import *
import uvicorn
import json
from fastapi.middleware.cors import CORSMiddleware

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
    return ""

@app.get("/hello")
def hello():
    return {"message": "hello world"}

@app.get("/laws")
def laws_list(page: int = 1, limit: int = 30, q: str = ""):
    overflow_limit = limit + 1
    offset = (page - 1) * limit

    laws_data = filtered_laws(
        offset = offset,
        overflow_limit = overflow_limit,
        search = q
    )

    has_more = len(laws_data) > limit
    if has_more:
        laws_data = laws_data[:limit]

    data = {
        "has_more": has_more,
        "laws": laws_data
    }


    return data

def filtered_laws(offset: int, overflow_limit: int, search: str):
    all_laws = [
        {"law_id": i, "law_nm": f"법안{i}", "processing_status": i % 5 + 1,
         "keywords": [f'키워드{i}', f'키워드{i+1}']}
        for i in range(1, 20)  # 100개의 샘플 데이터
    ]


    if search != "" and search.strip():
        search_lower = search.lower()
        all_laws = [
            news for news in all_laws
            if search_lower in news["law_nm"].lower() or
               any(search_lower in keyword.lower() for keyword in news["keywords"])
        ]

    return all_laws[offset:offset + overflow_limit]

@app.get("/laws/{law_id}")
def law(law_id: int):
    law = {
        "law_id": law_id,
        "law_nm": f"법안1{law_id}",
        "keywords": ["키워드1", "키워드2", "키워드3"],
        "law_dt": "2025-05-22",
        "law_link": f"링크{law_id}",
        "processing_result": "원안가결"
    }
    return law


@app.get("/issue")
def issue_list(page: int = 1, limit: int = 30, q: str = "", category: str = '정치'):
    overflow_limit = limit + 1
    offset = (page - 1) * limit

    keywords = filtered_keywords(
        offset = offset,
        overflow_limit = overflow_limit,
        search = q,
        category = category
    )

    has_more = len(keywords) > limit
    if has_more:
        keywords = keywords[:limit]

    keywords_data = {
        "keywords": keywords,
        "has_more": has_more
    }

    return keywords_data

def filtered_keywords(offset: int, overflow_limit: int, search: str, category: str):
    all_keywords = [
        {"keyword_nm": f'키워드{i}', "category": f'정치' if i % 2 == 0 else f'경제'}
        for i in range(1, 20)  # 100개의 샘플 데이터
    ]

    if category:
        all_keywords = [keyword for keyword in all_keywords if keyword["category"] == category]

    if search != "" and search.strip():
        search_lower = search.lower()
        all_keywords = [
            keywords for keywords in all_keywords
            if search_lower in keywords["keyword_nm"].lower() or
               any(search_lower in keywords.lower() for keywords in keywords["keyword_nm"])
        ]

    return all_keywords[offset:offset + overflow_limit]

@app.get("/issue/{keyword_name}")
def keyword(keyword_name: str):
    pass

@app.get("/news")
def news_list(page: int = 1, limit: int = 30, q: str = '', category: str = '정치'):
    overflow_limit = limit + 1
    offset = (page - 1) * limit
    news_data = filtered_news(
        offset=offset,
        overflow_limit=overflow_limit,
        search=q,
        category=category
    )

    has_more = len(news_data) > limit
    if has_more:
        news_data = news_data[:limit]

    newslist = {
        "has_more": has_more,
        "news": news_data
    }

    return newslist

def filtered_news(offset: int, overflow_limit: int, search: str, category: str):
    all_news = [
        {"news_id": i, "title": f"뉴스 {i}", "img": "https://img.khan.co.kr/news/2025/05/22/l_2025052301000641500065161.jpg",
         "news_dt": "2025-06-05", "keywords": [f'키워드{i}', f'키워드{i+1}'],"category": "정치" if i % 2 == 0 else "경제"}
        for i in range(1, 20)  # 100개의 샘플 데이터
    ]

    if category:
        all_news = [news for news in all_news if news["category"] == category]

    if search != "" and search.strip():
        search_lower = search.lower()
        all_news = [
            news for news in all_news
            if search_lower in news["title"].lower() or
               any(search_lower in keyword.lower() for keyword in news["keywords"])
        ]

    return all_news[offset:offset + overflow_limit]


@app.get("/news/{news_id}")
def news_detail(news_id: int):
    news_id = 1
    news = {
        "news_id": news_id,
        "title": "뉴스1",
        "news_dt": "2025-05-22 05:22",
        "related_laws": [
            {
                "law_id": 1,
                "law_nm": "법안1"
            },
            {
                "law_id": 2,
                "law_nm": "법안2"
            }
        ]
    }
    return news

@app.get("/party")
def party():
    issue_list = {
        "issues": [
            {
                "keyword_nm": f"키워드{i}",
                "parties": [
                    {"id": i, "name": f'정당{i}', "rate": 6 - i}
                    for i in range(1, 6)
                ]
            }
            for i in range(1, 6)
        ]
    }


    parties_list = {
        "parties": [
            {"party_id": i, "party_nm": f'정당{i}', "img": f'img{i}.jpg'}
            for i in range(1, 9)
        ]
    }

    return issue_list, parties_list

@app.get("/party/party_detail")
def party_detail(page: int = 1):
    PAGE_SIZE = 15
    offset = (page - 1) * PAGE_SIZE
    limit = PAGE_SIZE + 1

    all_keyword_contribution = {
        "issues": [
            {
                "keyword_nm": f'키워드{i}',
                "top5_party": [
                    {
                        "party_id": j,
                        "party_nm": f'정당{j}',
                        "rate": 10 + 5 * (j - 1)
                    } for j in range(1, 6)
                ]
            } for i in range(1, 19)
        ]
    }

    page_data = all_keyword_contribution["issues"][offset:offset + limit]

    has_more = len(page_data) > PAGE_SIZE
    if has_more:
        page_data = page_data[:PAGE_SIZE]

    contribution = {
        "has_more": has_more,
        "data": page_data
    }

    return contribution

@app.get("/party/{party_id}")
def party_contribution(party_id: int):
    party_data = {
        "party_nm": f'정당{party_id}',
        "img": f'img{party_id}.jpg',
        "contribution": [
            {
                "keyword_nm": f'키워드{i}',
                "count": i,
                "max_count": 50
            }
            for i in range(1, 30)
        ]
    }
    return party_data

# if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    # uvicorn test:app --reload --host=0.0.0.0 --port=8000
