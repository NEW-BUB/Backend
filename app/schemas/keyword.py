from pydantic import BaseModel
from typing import List

class KeywordBase(BaseModel):
    keyword_nm: str

class KeywordList(BaseModel):
    keywords: List[KeywordBase]
    has_more: bool
