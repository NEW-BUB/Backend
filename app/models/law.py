from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base

class Law(Base):
    __tablename__ = "laws"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    number = Column(Integer)
    proponent = Column(String)
    date = Column(Date)
    processing_status = Column(String)
    processing_result = Column(String)
    contents = Column(String)
    link = Column(String)


    keyword = relationship("KeywordLaw", back_populates="law")
    news = relationship("NewsLaw", back_populates="law")
    party_contribution = relationship("LawPartyContribution", back_populates="law")
