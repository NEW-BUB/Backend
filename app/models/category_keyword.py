from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class CategoryKeyword(Base):
    __tablename__ = 'category_keyword'

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id'))
    keyword_id = Column(Integer, ForeignKey('keywords.id'))

    category = relationship('Category', back_populates='keyword')
    keyword = relationship('Keyword', back_populates='category')
