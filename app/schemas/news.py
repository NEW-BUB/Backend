from pydantic import BaseModel, HttpUrl, Any
from typing import List, Dict, Optional
from datetime import datetime

class NewsBase(BaseModel):
    title: str
    img: Optional[HttpUrl] = None
    news_dt: datetime

class NewsCreate(NewsBase):
    author: str
    new_link: str
    texts: str
    keywords: List[str] = []
    category: str

class NewsListItem(NewsBase):
    news_id: int

class NewsResponse(NewsBase):
    news_id: int
    author: str
    new_link: HttpUrl
    texts: str
    keywords_nm: List[str] = []
    related_laws: List[Dict[str, Any]] = []

class NewsList(BaseModel):
    news: List[NewsListItem]
    has_more: bool
