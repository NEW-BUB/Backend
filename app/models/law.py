from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base

class Law(Base):
    __tablename__ = "laws"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    pdf_link = Column(String)
    processing_status = Column(String)

    keywords = relationship("KeywordLaw", back_populates="law")
    news = relationship("NewsLaw", back_populates="law")
    party_contributions = relationship("PartyContribution", back_populates="law")
