from pydantic import BaseModel
from typing import List
from app.schemas.keyword import KeywordBase

class PartyBase(BaseModel):
    name: str = ""

class PartyListItem(PartyBase):
    id: int = 1
    img: str = ""

class PartyList(BaseModel):
    parties: List[PartyListItem] = []

class PartyKeywordContribution(PartyBase):
    id: int = 1
    rate: float = 0.0

class PartyDetailItem(BaseModel):
    keyword: str = ""
    top5_party: List[PartyKeywordContribution] = []

class PartyDetail(BaseModel):
    has_more: bool = False
    issues: List[PartyDetailItem] = []

class KeywordContribution(PartyDetail):
    has_more: bool = False

class ContributionItem(BaseModel):
    keyword: str = ""
    count: int = 0

class PartyContribution(PartyBase):
    img: str = ""
    contribution: List[ContributionItem] = []
    max_count: int = 0
