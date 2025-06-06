from pydantic import BaseModel, HttpUrl
from typing import List
from .keyword import *

class PartyBase(BaseModel):
    party_nm: str

class PartyListItem(PartyBase):
    party_id: int
    img: HttpUrl

class PartyList(BaseModel):
    parties: List[PartyListItem]

class PartyKeywordContribution(PartyBase):
    party_id: int
    rate: float

class PartyDetailItem(KeywordBase):
    top5_party: List[PartyKeywordContribution]

class PartyDetail(BaseModel):
    issues: List[PartyDetailItem]

class KeywordContribution(KeywordBase):
    count: int
    max_count: int

class PartyContribution(PartyBase):
    img: HttpUrl
    contribution: List[KeywordContribution]
