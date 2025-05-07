from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base

class KeywordPartyContribution(Base):
    __tablename__ = "keyword_party_contributions"

    id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"))
    party_id = Column(Integer, ForeignKey("parties.id"))
    count = Column(Integer)

    keyword = relationship("Keyword", back_populates="party_contributions")
    party = relationship("Party", back_populates="keyword_contributions")
