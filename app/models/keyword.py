from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    news = relationship("KeywordNews", back_populates="keyword")
    laws = relationship("KeywordLaw", back_populates="keyword")
    party_contributions = relationship("KeywordPartyContribution", back_populates="keyword")