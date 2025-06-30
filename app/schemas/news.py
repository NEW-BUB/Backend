from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class NewsBase(BaseModel):
    title: str = ""
    img: Optional[str] = None
    date: str = ""

class NewsCreate(NewsBase):
    author: str = ""
    link: str = ""
    text: str = ""

class NewsListItem(NewsBase):
    id: int = 1

class NewsResponse(NewsBase):
    id: int = 1
    author: str = ""
    link: str = ""
    text: str = ""
    keywords: List[str] = []
    categories: List[str] = []

class NewsList(BaseModel):
    news: List[NewsListItem] = []
    has_more: bool = False
