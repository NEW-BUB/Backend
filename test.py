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
        {"id": i, "name": f"법안{i}", "processing_status": i % 5 + 1,
         "keywords": [f'키워드{i}', f'키워드{i+1}']}
        for i in range(1, 20)  # 100개의 샘플 데이터
    ]


    if search != "" and search.strip():
        search_lower = search.lower()
        all_laws = [
            law for law in all_laws
            if search_lower in law["name"].lower() or
               any(search_lower in keyword.lower() for keyword in law["keywords"])
        ]

    return all_laws[offset:offset + overflow_limit]

@app.get("/laws/{law_id}")
def law(law_id: int):
    law = {
        "id": law_id,
        "number": 1,
        "name": f"법안1{law_id}",
        "keywords": ["키워드1", "키워드2", "키워드3"],
        "date": "2025-05-22",
        "proponent": "제안자",
        "link": f"링크{law_id}",
        "processing_status": 1,
        "processing_result": "원안가결",
        "summary": "제안이유 및 주요내용",
        "parties": [
            {
                "id": 1,
                "name": "정당1",
                "img": "정당이미지1"
            },
            {
                "id": 1,
                "name": "정당1",
                "img": "정당이미지1"
            }
        ]
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
    # KeywordList
    return keywords_data

def filtered_keywords(offset: int, overflow_limit: int, search: str, category: str):
    all_keywords = [
        {"name": f'키워드{i}', "categories": ['정치'] if i % 2 == 0 else ['경제', '문화']}
        for i in range(1, 20)  # 100개의 샘플 데이터
    ]

    if category:
        all_keywords = [keyword for keyword in all_keywords if category in keyword["categories"]]

    if search != "" and search.strip():
        search_lower = search.lower()
        all_keywords = [
            keywords for keywords in all_keywords
            if search_lower in keywords["name"].lower() or
               any(search_lower in keywords.lower() for keywords in keywords["name"])
        ]

    all_keywords = [keyword["name"] for keyword in all_keywords]
    return all_keywords[offset:offset + overflow_limit]

@app.get("/issue/{keyword_name}")
def issues_related_news_laws(keyword_name: str):
    news = {
        "news": [
            {
                "id": 100,
                "title": "뉴스100",
                "img": "뉴스이미지100",
                "date": "2025-05-22 05:22"
            },
            {
                "id": 100,
                "title": "뉴스100",
                "img": "뉴스이미지100",
                "date": "2025-05-22 05:22"
            },
            {
                "id": 100,
                "title": "뉴스100",
                "img": "뉴스이미지100",
                "date": "2025-05-22 05:22"
            }
        ]
    }

    laws = {
        "laws": [
            {
                "id": 100,
                "name": "의안100"
            },
            {
                "id": 100,
                "name": "의안100"
            },
            {
                "id": 100,
                "name": "의안100"
            }
        ]
    }

    return [laws, news]



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
    # NewList
    return newslist

def filtered_news(offset: int, overflow_limit: int, search: str, category: str):
    all_news = [
        {"id": i, "title": f"뉴스 {i}", "img": "https://img.khan.co.kr/news/2025/05/22/l_2025052301000641500065161.jpg",
         "date": "2025-06-05", "keywords": [f'키워드{i}', f'키워드{i+1}'],"category": ["정치"] if i % 3 == 0 else ["정치", "경제"]}
        for i in range(1, 20)  # 100개의 샘플 데이터
    ]

    if category:
        all_news = [news for news in all_news if category in news["category"]]

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
    news = {
        "id": news_id,
        "title": "뉴스1",
        "date": "2025-05-22 05:22",
        "img": "뉴스이미지1",
        "author": "저자1",
        "link": "뉴스링크1",
        "text": "뉴스내용",
        "keywords": ["키워드1", "키워드2", "키워드3"],
        "related_laws": [
            {
                "id": 1,
                "name": "법안1"
            },
            {
                "id": 2,
                "name": "법안2"
            }
        ],
        "categories": ["정치", "경제", "문화"],
        "related_news": [
            {
                "id": {news_id+1},
                "title": f'뉴스{news_id+1}',
                "img": f'뉴스이미지{news_id+1}',
                "date": "2025-05-22 05:22"
            },
            {
                "id": {news_id+2},
                "title": f'뉴스{news_id+2}',
                "img": f'뉴스이미지{news_id+2}',
                "date": "2025-05-22 05:22"
            },
            {
                "id": {news_id+3},
                "title": f'뉴스{news_id+3}',
                "img": f'뉴스이미지{news_id+3}',
                "date": "2025-05-22 05:22"
            }
        ]
    }
    # NewsResponse
    return news

@app.get("/party")
def party():
    # PartyDetail
    issue_list = {
        "issues": [
            {
                "keyword": f"키워드{i}",
                "top5_party": [
                    {"id": i, "name": f'정당{i}', "rate": 6 - i}
                    for i in range(1, 6)
                ]
            }
            for i in range(1, 6)
        ]
    }

    # PartyList
    parties_list = {
        "parties": [
            {"id": i, "name": f'정당{i}', "img": f'img{i}.jpg'}
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
                "keyword": f'키워드{i}',
                "top5_party": [
                    {
                        "id": j,
                        "name": f'정당{j}',
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
        "issues": page_data
    }
    # KeywordContribution
    return contribution

@app.get("/party/{party_id}")
def party_contribution(party_id: int):
    party_data = {
        "name": f'정당{party_id}',
        "img": f'img{party_id}.jpg',
        "contribution": [
            {
                "keyword": f'키워드{i}',
                "count": i
            }
            for i in range(1, 30)
        ],
        "max_count": 29
    }
    return party_data

# if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    # uvicorn test:app --reload --host=0.0.0.0 --port=8000
