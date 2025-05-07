from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base

class PartyContribution(Base):
    __tablename__ = "party_contributions"

    id = Column(Integer, primary_key=True)
    law_id = Column(Integer, ForeignKey("laws.id"))
    party_id = Column(Integer, ForeignKey("parties.id"))
    count = Column(Integer)

    law = relationship("Law", back_populates="party_contributions")
    party = relationship("Party", back_populates="law_contributions")
