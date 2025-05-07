from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base

class Party(Base):
    __tablename__ = "parties"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    img = Column(String)

    keyword_contributions = relationship("KeywordPartyContribution", back_populates="party")
    law_contributions = relationship("PartyContribution", back_populates="party")
