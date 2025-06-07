from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.law import LawList, LawResponse
from app.services.law_service import LawService

router = APIRouter(prefix="/laws", tags=["laws"])

@router.get("/", response_model=LawList)
async def list_laws(
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(30, ge=1, description="Limit of keywords per page"),
        q: str = Query("", description="Query string"),
        db: Session = Depends(get_db)
):
    overflow_limit = limit + 1
    offset = (page - 1) * limit

    laws_service = LawService(db)

    laws_list = laws_service.get_laws_list(
        offset=offset,
        overflow_limit=overflow_limit,
        search=q
    )

    has_more = len(laws_list) > limit
    if has_more:
        laws_list = laws_list[:limit]

    return {
        "has_more": has_more,
        "laws": laws_list
    }

@router.get("/{law_id}", response_model=LawResponse)
async def get_law_by_id(
        law_id: int,
        db: Session = Depends(get_db)
):
    law_service = LawService(db)

    return law_service.get_law_by_id(law_id)
