from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.lego import Minifig
from app.schemas.lego import MinifigSummary, PaginatedMinifigs

router = APIRouter(prefix="/minifigs", tags=["minifigs"])


@router.get("", response_model=PaginatedMinifigs)
def list_minifigs(
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=100),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(Minifig)
    if search:
        query = query.where(Minifig.name.ilike(f"%{search}%"))

    total = db.scalar(select(func.count()).select_from(query.subquery()))
    minifigs = db.scalars(
        query.order_by(Minifig.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return PaginatedMinifigs(
        total=total or 0,
        page=page,
        page_size=page_size,
        results=[MinifigSummary.model_validate(m) for m in minifigs],
    )
