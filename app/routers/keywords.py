from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.keyword import *
from app.services.keyword_service import KeywordService
from app.services.law_service import LawService
from app.services.news_service import NewsService

router = APIRouter(prefix="/issue", tags=["issues"])

@router.get("/", response_model=KeywordList)
async def get_keywords_list(
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(30, ge=1, description="Limit of keywords per page"),
        q: str = Query("", description="Query string"),
        category: str = Query(""),
        db: Session = Depends(get_db)
):
    overflow_limit = limit + 1
    offset = (page - 1) * limit

    keyword_service = KeywordService(db=db)

    keyword_names = keyword_service.get_keywords_list(
        offset=offset,
        overflow_limit=overflow_limit,
        search=q,
        category=category
    )

    has_more = len(keyword_names) > limit
    if has_more:
        keyword_names = keyword_names[:limit]

    return {
        "keywords": keyword_names,
        "has_more": has_more
    }

@router.get("/{keyword_nm}")
async def get_laws_news_by_keyword(
        keyword_nm: str,
        limit: int = Query(7, ge=1, description="Limit of keywords per page"),
        db: Session = Depends(get_db)
):  
    law_service = LawService(db=db)
    laws = law_service.get_complete_laws_list(limit=limit, search=keyword_nm)

    news_service = NewsService(db=db)
    news = news_service.get_complete_news_list(limit=limit, search=keyword_nm)

    return [{"laws": laws}, {"news": news}]
