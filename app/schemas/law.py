from pydantic import BaseModel
from typing import List, Dict, Any


class LawBase(BaseModel):
    name: str = ""
    processing_status: int = 1

class LawCreate(LawBase):
    pass

class LawListItem(LawBase):
    id: int = 1

class LawList(BaseModel):
    laws: List[LawListItem] = []
    has_more: bool = False

class LawResponse(LawBase):
    id: int = 1
    number: int = 1
    proponent: str = ""
    date: str = "" # datetime → str로 변경 
    processing_result: str = ""
    summary: str = ""
    keywords: List[str] = []
    parties: List[Dict[str, Any]] = []
    link: str = ""
