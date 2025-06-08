from pydantic import BaseModel
from typing import List
from app.schemas.keyword import KeywordBase

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

class PartyDetailItem(BaseModel):
    keyword: str
    top5_party: List[PartyKeywordContribution]

class PartyDetail(BaseModel):
    has_more: bool
    issues: List[PartyDetailItem]

class KeywordContribution(PartyDetail):
    has_more: bool

class ContributionItem(BaseModel):
    keyword: str
    count: int

class PartyContribution(PartyBase):
    img: str
    contribution: List[ContributionItem]
    max_count: int
