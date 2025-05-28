from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(15))

    keyword = relationship('CategoryKeyword', back_populates='category')
    news = relationship('CategoryNews', back_populates='category')
