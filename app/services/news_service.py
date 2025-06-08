from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.category_news import CategoryNews
from app.models.keyword import Keyword
from app.models.keyword_news import KeywordNews
from app.models.law import Law
from app.models.news import News
from app.models.news_law import NewsLaw
from app.schemas.news import *


from fastapi import Depends
from app.dependencies import get_db


class NewsService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_news_list(self, offset: int, overflow_limit: int = 30, search: str = "", category: str = "정치") -> List[NewsListItem]:
        query = self.db.query(News)
        if not query:
            return None

        if category:
            category_subquery = (
                self.db.query(CategoryNews.news_id)
                .join(Category)
                .filter(Category.name.ilike(f"%{category}%"))
            )
            query = query.filter(News.id.in_(category_subquery))

        if search and search.strip():
            search_term = f"%{search.lower()}%"
            keyword_subquery = (
                self.db.query(KeywordNews.news_id)
                .join(Keyword)
                .filter(Keyword.name.ilike(search_term))
            )
            query = query.filter(News.id.in_(keyword_subquery))

        query = query.order_by(News.date.desc()).offset(offset).limit(overflow_limit)
        query = query.all()

        news = [
            {
                "id": news.id,
                "title": news.title,
                "img": news.img,
                "date": news.date
            }
            for news in query
        ]
        return news

    def get_complete_news_list(self, limit: int = 30, search: str = "") -> List[dict]:
        query = self.db.query(News)
        if not query:
            return None

        if search and search.strip():
            search_term = search.lower()
            keyword_subquery = (
                self.db.query(KeywordNews.news_id)
                .join(Keyword)
                .filter(Keyword.name==search_term)
            )
            query = query.filter(News.id.in_(keyword_subquery))

        query = query.order_by(News.date.desc()).limit(limit)
        query = query.all()

        news = [
            {
                "id": news.id,
                "title": news.title,
                "img": news.img,
                "date": news.date
            }
            for news in query
        ]
        return news


    def get_news_by_id(self, news_id: int) -> Optional[NewsResponse]:
        query = self.db.query(News).filter(News.id == news_id).first()

        print(query.text)

        categories = self.get_news_categories(news_id)

        news_detail = {
            "id": news_id,
            "title": query.title,
            "img": query.img,
            "date": query.date,
            "author": query.author,
            "text": query.text,
            "link": query.link,
            # "keywords": [],
            "keywords": self.get_news_keywords(news_id),
            "categories": categories
        }
        return news_detail

    def get_news_keywords(self, news_id: int) -> List[str]:
        keywords = self.db.query(Keyword).join(KeywordNews).filter(KeywordNews.news_id == news_id).all()
        return [keyword.name for keyword in keywords]

    def get_news_categories(self, news_id: int) -> List[str]:
        query = self.db.query(Category).join(CategoryNews).filter(CategoryNews.news_id == news_id).all()
        return [category.name for category in query]

    def get_news_related_news(self, categories: List[str]) -> List[NewsListItem]:
        query = self.db.query(News).join(CategoryNews).join(Category).filter(Category.name.in_(categories))
        query = query.order_by(News.date.desc()).limit(5)
        query = query.all()

        news = [
            {
                "id": news.id,
                "title": news.title,
                "img": news.img,
                "date": news.date
            }
            for news in query
        ]
        return news
