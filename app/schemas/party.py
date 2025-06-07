from pydantic import BaseModel
from typing import List
from .keyword import *

class PartyBase(BaseModel):
    name: str

class PartyListItem(PartyBase):
    id: int
    img: str

class PartyList(BaseModel):
    parties: List[PartyListItem]

class PartyKeywordContribution(PartyBase):
    id: int
    rate: float

class PartyDetailItem(KeywordBase):
    top5_party: List[PartyKeywordContribution]

class PartyDetail(BaseModel):
    issues: List[PartyDetailItem]

class KeywordContribution(KeywordBase):
    count: int

class PartyContribution(PartyBase):
    img: str
    contribution: List[KeywordContribution]
    max_count: int
