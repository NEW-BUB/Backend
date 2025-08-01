from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from typing import List, Optional

from app.models.category import Category
from app.models.category_keyword import CategoryKeyword
from app.models.keyword import Keyword

from fastapi import Depends
from app.dependencies import get_db

class KeywordService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        
    def get_keywords(self) -> List[dict]:
        query = self.db.query(Keyword)

        query = query.order_by(Keyword.count.desc()).all()

        return [{"id": keyword.id,"name": keyword.name} for keyword in query]

    def get_keywords_list(self, offset: int, overflow_limit: int = 30, search: str = "", category: str = "") -> List[str]:
        query = self.db.query(Keyword)

        if category:
            query = query.join(CategoryKeyword).join(Category).filter(Category.name.ilike(f"%{category}%"))

        if search and search.strip():
            search_term = f"%{search.lower()}%"
            query = query.filter(Keyword.name.ilike(search_term))

        query = query.order_by(Keyword.count.desc()).offset(offset).limit(overflow_limit).all()

        return [keyword.name for keyword in query]

    def increment_keyword_count(self, keyword_nm: str) -> Optional[Keyword]:
        keyword = self.db.query(Keyword).filter(Keyword.name == keyword_nm).first()

        if keyword:
            keyword.count = (keyword.count or 0) + 1
            self.db.commit()
            self.db.refresh(keyword)
            return keyword

        # 만약 insert 도 허용하고 싶으면 아래 주석 해제
        # else:
        #     new_keyword = Keyword(name=keyword_nm, count=1)
        #     self.db.add(new_keyword)
        #     self.db.commit()
        #     self.db.refresh(new_keyword)
        #     return new_keyword

        return None
