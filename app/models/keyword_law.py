from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base

class KeywordLaw(Base):
    __tablename__ = "keyword_laws"

    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"))
    law_id = Column(Integer, ForeignKey("laws.id"))

    keyword = relationship("Keyword", back_populates="law")
    law = relationship("Law", back_populates="keyword")
