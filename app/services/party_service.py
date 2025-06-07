from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import party
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

    def get_keyword_party_contributions(self) -> List[dict]:
        subquery = (
                self.db.query(Party, KeywordPartyContribution)
                .join(KeywordPartyContribution)
                .order_by(KeywordPartyContribution.count.desc())
                .join(Keyword)
                .order_by(Keyword.count.desc())
                .limit(5)
                .all()
        )

        if not subquery:
            return [{"name": "", "top5_party": []}]
            
        result = []

        for party, contrib in subquery:
            counts = [contrib.count for party, contrib in subquery]
            rates = self.calculate_percentile(counts)

            top5_party = [
                {
                    "id": party.id,
                    "name": party.name,
                    "rate": rates[i]
                }
                for i, (party,contribution) in enumerate(subquery)
            ]

            result.append({"name": party.name, "top5_party": top5_party})

        return result

    def get_party_by_id(self, party_id: int) -> Optional[Party]:
        return self.db.query(Party).filter(Party.id == party_id).first()

    def get_party_keyword_contributions(self, party_id: int, limit: int) -> dict:
        party = self.get_party_by_id(party_id)
        if not party:
            return {}

        keyword_contributions = (
            self.db.query(KeywordPartyContribution, Keyword)
            .join(Keyword, Keyword.id == KeywordPartyContribution.keyword_id)
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

        counts = [contrib.count for contrib, keyword in keyword_contributions]
        max_count = max(counts)

        contributions = [
            {
                "name": keyword.name,
                "count": contrib.count
            }
            for contrib, keyword in keyword_contributions
        ]

        return {
            "name": party.name,
            "img": party.img,
            "contribution": contributions,
            "max_count": max_count
        }
