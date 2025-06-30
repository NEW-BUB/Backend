from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.dependencies import get_db
from app.schemas.news import *
from app.services.news_service import NewsService

router = APIRouter(prefix="/news", tags=["news"])

class NewsKeywordRequest(BaseModel):
    keywords: List[str]

@router.get("/", response_model=NewsList)
def get_news_list(
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(30, ge=1, description="Limit of keywords per page"),
        q: str = Query(""),
        category: str = Query("정치"),
        db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    overflow_limit = limit + 1

    news_service = NewsService(db=db)

    news_list = news_service.get_news_list(
        offset=offset,
        overflow_limit=overflow_limit,
        search=q,
        category=category
    )

    has_more = len(news_list) > limit
    if has_more:
        news_list = news_list[:limit]

    return {
        "has_more": has_more,
        "news": news_list
    }

@router.post("/match-laws/")
async def match_laws_by_keywords(
    req: NewsKeywordRequest,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, description="Limit of keywords per page"),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    overflow_limit = limit + 1

    news_service = NewsService(db=db)
    matched_laws = news_service.get_news_related_laws(offset=offset, overflow_limit=overflow_limit, keywords=req.keywords)

    has_more = len(matched_laws) > limit
    if has_more:
        matched_laws = matched_laws[:limit]

    return {"matched_laws": matched_laws, "has_more": has_more}

@router.get("/{news_id}", response_model=NewsResponse)
async def get_news(
        news_id: int,
        db: Session = Depends(get_db)
):
    news_service = NewsService(db=db)
    news_detail = news_service.get_news_by_id(news_id)
    return news_detail
