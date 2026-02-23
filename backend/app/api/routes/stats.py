from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.lego import Color, Minifig, Part, Set, Theme
from app.schemas.lego import Stats

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=Stats)
def get_stats(db: Session = Depends(get_db)):
    total_sets = db.scalar(select(func.count(Set.set_num))) or 0
    total_themes = db.scalar(select(func.count(Theme.id))) or 0
    total_parts = db.scalar(select(func.count(Part.part_num))) or 0
    total_minifigs = db.scalar(select(func.count(Minifig.fig_num))) or 0
    total_colors = db.scalar(select(func.count(Color.id))) or 0

    year_range = db.execute(select(func.min(Set.year), func.max(Set.year))).one()
    year_min = year_range[0] or 1949
    year_max = year_range[1] or 2025

    sets_per_year_rows = db.execute(
        select(Set.year, func.count(Set.set_num).label("count"))
        .group_by(Set.year)
        .order_by(Set.year)
    ).all()
    sets_per_year = [{"year": row.year, "count": row.count} for row in sets_per_year_rows]

    top_themes_rows = db.execute(
        select(Theme.name, func.count(Set.set_num).label("count"))
        .join(Set, Set.theme_id == Theme.id)
        .group_by(Theme.id, Theme.name)
        .order_by(func.count(Set.set_num).desc())
        .limit(10)
    ).all()
    top_themes = [{"name": row.name, "count": row.count} for row in top_themes_rows]

    return Stats(
        total_sets=total_sets,
        total_themes=total_themes,
        total_parts=total_parts,
        total_minifigs=total_minifigs,
        total_colors=total_colors,
        year_min=year_min,
        year_max=year_max,
        sets_per_year=sets_per_year,
        top_themes=top_themes,
    )
