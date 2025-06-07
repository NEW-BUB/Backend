from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from typing import List

from app.models.category import Category
from app.models.category_keyword import CategoryKeyword
from app.models.keyword import Keyword

class KeywordService:
    def __init__(self, db: Session):
        self.db = db

    def get_keywords_list(self, offset: int, overflow_limit: int = 30, search: str = "", category: str = "") -> List[str]:
        query = self.db.query(Keyword)

        if category:
            query = query.join(CategoryKeyword).join(Category).filter(Category.name.ilike(f"%{category}%"))

        if search and search.strip():
            search_term = f"%{search.lower()}%"
            query = query.filter(Keyword.name.ilike(search_term))

        query = query.order_by(Keyword.count.desc()).offset(offset).limit(overflow_limit).all()
        return [keyword.name for keyword in query]
