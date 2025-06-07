from pydantic import BaseModel
from typing import List

class KeywordBase(BaseModel):
    name: str

class KeywordList(BaseModel):
    keywords: List[str]
    has_more: bool
