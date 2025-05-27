from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.database import Base

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    date = Column(Date)
    img = Column(String(255))
    author = Column(String(255))
    text = Column(String(255))
    link = Column(String(255))

    keyword = relationship("KeywordNews", back_populates="news")
    law = relationship("NewsLaw", back_populates="news")
    category = relationship("CategoryNews", back_populates="news")
