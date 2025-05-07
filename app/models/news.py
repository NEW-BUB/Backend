from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.database import Base

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    date = Column(Date)
    img = Column(String)
    author = Column(String)
    text = Column(String)

    keywords = relationship("KeywordNews", back_populates="news")
    laws = relationship("NewsLaw", back_populates="news")
