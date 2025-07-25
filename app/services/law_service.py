from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime

from app.models.law import Law
from app.models.keyword import Keyword
from app.models.keyword_law import KeywordLaw
from app.models.party import Party
from app.models.law_party_contribution import LawPartyContribution
from app.schemas.law import LawListItem, LawResponse, LawList
from app.schemas.party import PartyList

from fastapi import Depends
from app.dependencies import get_db

from sqlalchemy import or_, func

class LawService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_laws_list(self, offset: int, overflow_limit: int, search: str = "") -> List[LawListItem]:
        query = self.db.query(Law)

        if search and search.strip():
            search_term_no_space = search.replace(' ', '').lower()

            keyword_subquery = self.db.query(KeywordLaw.law_id).join(Keyword).filter(
                func.lower(func.replace(Keyword.name, ' ', '')).ilike(f'%{search_term_no_space}%')
            )

            query = query.filter(
                or_(
                    Law.id.in_(keyword_subquery),
                    func.lower(func.replace(Law.name, ' ', '')).ilike(f'%{search_term_no_space}%')
                )
            )

        query = query.order_by(Law.date.desc()).offset(offset).limit(overflow_limit).all()

        law_list_items = [
            {
                "id": law.id,
                "name": law.name,
                "processing_status": law.processing_status
            }
            for law in query
        ]

        return law_list_items


    def get_complete_laws_list(self, limit: int, search: str = "") -> List[dict]:
        query = self.db.query(Law)

        if search and search.strip():
            search_term = search.lower()
            # 정확 일치 검색 → == 유지
            query = query.join(KeywordLaw).join(Keyword).filter(Keyword.name == search_term)

        query = query.order_by(Law.date.desc()).limit(limit).all()

        law_list_items = [
            {
                "id": law.id,
                "name": law.name
            }
            for law in query
        ]
        return law_list_items

    def get_law_by_id(self, law_id: int) -> Optional[LawResponse]:
        query = self.db.query(Law).filter(Law.id == law_id).first()

        if not query:
            return None

        # query.date 가 str 인 경우 처리
        date = (
            datetime.fromisoformat(query.date).strftime("%Y-%m-%d")
            if isinstance(query.date, str)
            else query.date.strftime("%Y-%m-%d")
        )

        law = {
            "id": law_id,
            "name": query.name,
            "number": query.number,
            "processing_status": query.processing_status,
            "processing_result": query.processing_result,
            "date": date,
            "proponent": query.proponent,
            "summary": query.summary,
            "link": query.link,
            "keywords": self.get_law_keywords(law_id),
            "parties": self.get_law_party_contributions(law_id)
        }

        return law

    def get_law_keywords(self, law_id: int) -> List[str]:
        keywords = (
            self.db.query(Keyword)
            .join(KeywordLaw)
            .filter(KeywordLaw.law_id == law_id)
            .all()
        )
        return [keyword.name for keyword in keywords]

    def get_law_party_contributions(self, law_id: int) -> List[dict]:
        parties = (
            self.db.query(Party)
            .join(LawPartyContribution)
            .filter(LawPartyContribution.law_id == law_id)
            .all()
        )
        parties_list = [
            {
                "id": party.id,
                "name": party.name,
                "img": party.img
            }
            for party in parties
        ]

        return parties_list
