from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    count = Column(Integer)

    news = relationship("KeywordNews", back_populates="keyword")
    law = relationship("KeywordLaw", back_populates="keyword")
    party_contribution = relationship("KeywordPartyContribution", back_populates="keyword")
    category = relationship("CategoryKeyword", back_populates="keyword")
