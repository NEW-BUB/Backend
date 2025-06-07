from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.party import PartyList
from app.schemas.party import *
from app.services.party_service import PartyService

router = APIRouter(prefix="/party", tags=["party"])

@router.get("/")
async def get_parties(
        db: Session = Depends(get_db)
):
    party_service = PartyService(db=db)
    parties_list = party_service.get_party_list()
    return parties_list

@router.get("/top5_party/")
async def get_keyword_top5_party(
    db: Session = Depends(get_db)
):
    party_service = PartyService(db=db)
    top5 = party_service.get_keyword_party_contributions()
    return top5

@router.get("/{party_id}")
async def get_party_by_id(
    party_id: int,
    db: Session = Depends(get_db)
):
    party_service = PartyService(db=db)
    party = party_service.get_party_by_id(party_id)
    if not party:
        return {"error": "Party not found"}

    contrib_info = party_service.get_party_keyword_contributions(party_id, limit=30)
    # contrib_info: {"contribution": [...], "max_count": ...}

    return contrib_info
    