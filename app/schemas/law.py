from pydantic import BaseModel, HttpUrl
from typing import List
from datetime import datetime

class LawBase(BaseModel):
    law_nm: str
    processing_status: int

class LawCreate(LawBase):
    pass

class LawListItem(LawBase):
    law_id: int

class LawResponse(LawBase):
    law_id: int
    law_no:int
    proponent: str
    law_dt: datetime
    processing_result: str
    summary: str
    keywords_nm: List[str] = []
    parties_id: List[int] = []
    law_link: HttpUrl

class LawList(BaseModel):
    laws: List[LawListItem]
    has_more: bool
