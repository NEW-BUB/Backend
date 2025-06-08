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
    limit: int = Query(14, ge=1, description="Limit of keywords per page"),
    db: Session = Depends(get_db)
):
    party_service = PartyService(db=db)
    top5 = party_service.get_keyword_party_contributions(overflow_limit=limit)
    return top5

@router.get("/party_detail")
async def get_keyword_top5_party(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(14, ge=1, description="Limit of keywords per page"),
    db: Session = Depends(get_db)
):
    overflow_limit = limit + 1
    offset = (page - 1) * limit

    party_service = PartyService(db=db)
    top5 = party_service.get_keyword_party_contributions(offset=offset, overflow_limit=overflow_limit)

    has_more = len(top5) > limit
    if has_more:
        top5 = top5[:limit]

    return {
        "has_more": has_more,
        "issues": top5
    }

@router.get("/{party_id}")
async def get_party_by_id(
    party_id: int,
    db: Session = Depends(get_db)
):
    party_service = PartyService(db=db)
    party = party_service.get_party_by_id(party_id)
    if not party:
        return {"error": "Party not found"}

    contrib_info = party_service.get_party_keyword_contributions(party_id)
    return contrib_info
    