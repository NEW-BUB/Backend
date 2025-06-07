from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

from app.schemas.party import PartyList


class LawBase(BaseModel):
    name: str
    processing_status: int

class LawCreate(LawBase):
    pass

class LawListItem(LawBase):
    id: int

class LawList(BaseModel):
    laws: List[LawListItem]
    has_more: bool

class LawResponse(LawBase):
    id: int
    number:int
    proponent: str
    date: datetime
    processing_result: str
    summary: str
    keywords: List[str] = []
    parties: List[Dict[str, Any]] = []
    link: str
