from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class CategoryNews(Base):
    __tablename__ = 'category_news'

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id'))
    news_id = Column(Integer, ForeignKey('news.id'))

    category = relationship('Category', back_populates='news')
    news = relationship('News', back_populates='category')
