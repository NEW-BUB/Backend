from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base

class Party(Base):
    __tablename__ = "parties"

    id = Column(Integer, primary_key=True)
    name = Column(String(10))

    keyword_contribution = relationship("KeywordPartyContribution", back_populates="party")
    law_contribution = relationship("LawPartyContribution", back_populates="party")
