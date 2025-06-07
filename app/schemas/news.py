from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime

class NewsBase(BaseModel):
    title: str
    img: Optional[str] = None
    date: datetime

class NewsCreate(NewsBase):
    author: str
    link: str
    text: str
    keywords: List[str] = []
    categories: List[str]

class NewsListItem(NewsBase):
    id: int

class NewsResponse(NewsBase):
    id: int
    author: str
    link: str
    text: str
    keywords: List[str] = []
    related_laws: List[Dict[str, Any]] = []
    categories: List[str] = []
    related_news: List[NewsListItem] = []

class NewsList(BaseModel):
    news: List[NewsListItem]
    has_more: bool
