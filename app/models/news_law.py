from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base

class NewsLaw(Base):
    __tablename__ = "news_laws"

    id = Column(Integer, primary_key=True)
    law_id = Column(Integer, ForeignKey("laws.id"))
    news_id = Column(Integer, ForeignKey("news.id"))

    law = relationship("Law", back_populates="news")
    news = relationship("News", back_populates="laws")
