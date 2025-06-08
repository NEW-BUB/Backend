from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.party import Party
from app.models.keyword import Keyword
from app.models.keyword_party_contribution import KeywordPartyContribution


class PartyService:
    def __init__(self, db: Session):
        self.db = db

    def get_party_list(self):
        parties = self.db.query(Party).filter(Party.eraco == 22).order_by(Party.seat.desc()).all()
        return [
            {
                "id": party.id,
                "name": party.name,
                "img": party.img
            }
            for party in parties
        ]


    def calculate_percentile(self, counts: List[int]) -> List[float]:
        if not counts:
            return []
        total = sum(counts)
        percentiles = [(count / total) * 100 for count in counts]
        return percentiles

    def get_keyword_party_contributions(self, offset: int = 0, overflow_limit: int = 15) -> List[dict]:
        # 1. 상위 키워드 조회
        keywords = (
            self.db.query(Keyword)
            .order_by(Keyword.count.desc())
            .offset(offset)
            .limit(overflow_limit)
            .all()
        )

        if not keywords:
            return [{"keyword": "", "top5_party": []}]

        result = []
        for keyword in keywords:
            # 2. 각 키워드별 top5 정당 조회
            party_contribs = (
                self.db.query(Party, KeywordPartyContribution)
                .join(KeywordPartyContribution, Party.id == KeywordPartyContribution.party_id)
                .filter(KeywordPartyContribution.keyword_id == keyword.id)
                .order_by(KeywordPartyContribution.count.desc())
                .limit(5)
                .all()
            )

            counts = [contrib.count for party, contrib in party_contribs]
            rates = self.calculate_percentile(counts) if counts else []

            top5_party = [
                {
                    "id": party.id,
                    "name": party.name,
                    "rate": rates[i] if i < len(rates) else 0.0
                }
                for i, (party, contrib) in enumerate(party_contribs)
            ]
            result.append({
                "keyword": keyword.name,
                "top5_party": top5_party
            })

        return result

    def get_party_by_id(self, party_id: int) -> Optional[Party]:
        return self.db.query(Party).filter(Party.id == party_id).first()

    def get_party_keyword_contributions(self, party_id: int, limit: int = 30) -> dict:
        party = self.get_party_by_id(party_id)
        if not party:
            return {}

        keyword_contributions = (
            self.db.query(Keyword, KeywordPartyContribution)
            .join(KeywordPartyContribution, Keyword.id == KeywordPartyContribution.keyword_id)
            .filter(KeywordPartyContribution.party_id == party_id)
            .order_by(KeywordPartyContribution.count.desc())
            .limit(limit)
            .all()
        )

        if not keyword_contributions:
            return {
                "name": party.name,
                "img": party.img,
                "contribution": [],
                "max_count": 0
            }

        contributions = [
            {
                "keyword": keyword.name,
                "count": contrib.count
            }
            for keyword, contrib in keyword_contributions
        ]
        max_count = max([c["count"] for c in contributions]) if contributions else 0

        return {
            "name": party.name,
            "img": party.img,
            "contribution": contributions,
            "max_count": max_count
        }
