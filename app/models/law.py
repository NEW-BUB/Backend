from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base

class Law(Base):
    __tablename__ = "laws"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    number = Column(Integer)
    proponent = Column(String(255))
    date = Column(Date)
    processing_status = Column(String(255))
    processing_result = Column(String(255))
    contents = Column(String(255))
    link = Column(String(255))


    keyword = relationship("KeywordLaw", back_populates="law")
    news = relationship("NewsLaw", back_populates="law")
    party_contribution = relationship("LawPartyContribution", back_populates="law")
