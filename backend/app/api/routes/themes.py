from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.lego import Set, Theme
from app.schemas.lego import Theme as ThemeSchema

router = APIRouter(prefix="/themes", tags=["themes"])


@router.get("", response_model=list[ThemeSchema])
def list_themes(db: Session = Depends(get_db)):
    themes = db.scalars(select(Theme).order_by(Theme.name)).all()
    return [ThemeSchema.model_validate(t) for t in themes]


@router.get("/{theme_id}/sets-count")
def theme_set_count(theme_id: int, db: Session = Depends(get_db)):
    count = db.scalar(select(func.count()).where(Set.theme_id == theme_id))
    return {"theme_id": theme_id, "count": count or 0}
