from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base

class KeywordNews(Base):
    __tablename__ = "keyword_news"

    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"))
    news_id = Column(Integer, ForeignKey("news.id"))

    keyword = relationship("Keyword", back_populates="news")
    news = relationship("News", back_populates="keyword")
