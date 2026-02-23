from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.lego import BricksetData, Inventory, InventoryMinifig, InventoryPart, Set
from app.schemas.lego import (
    BricksetInfo,
    InventoryPartDetail,
    MinifigSummary,
    PaginatedSets,
    SetDetail,
    SetFullDetail,
    SetSummary,
)

router = APIRouter(prefix="/sets", tags=["sets"])


@router.get("", response_model=PaginatedSets)
def list_sets(
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=100),
    theme_id: int | None = None,
    year_min: int | None = None,
    year_max: int | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(Set)

    if theme_id is not None:
        query = query.where(Set.theme_id == theme_id)
    if year_min is not None:
        query = query.where(Set.year >= year_min)
    if year_max is not None:
        query = query.where(Set.year <= year_max)
    if search:
        query = query.where(Set.name.ilike(f"%{search}%"))

    total = db.scalar(select(func.count()).select_from(query.subquery()))
    sets = db.scalars(
        query.order_by(Set.year.desc(), Set.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return PaginatedSets(
        total=total or 0,
        page=page,
        page_size=page_size,
        results=[SetSummary.model_validate(s) for s in sets],
    )


@router.get("/{set_num}", response_model=SetFullDetail)
def get_set(set_num: str, db: Session = Depends(get_db)):
    lego_set = db.scalar(
        select(Set)
        .options(joinedload(Set.theme))
        .where(Set.set_num == set_num)
    )
    if not lego_set:
        raise HTTPException(status_code=404, detail="Set not found")

    # Brickset verrijkingsdata
    brickset_row = db.scalar(
        select(BricksetData).where(BricksetData.set_num == set_num)
    )
    brickset = BricksetInfo.model_validate(brickset_row) if brickset_row else None

    # Meest recente inventaris ophalen
    inventory = db.scalar(
        select(Inventory)
        .where(Inventory.set_num == set_num)
        .order_by(Inventory.version.desc())
    )

    parts: list[InventoryPartDetail] = []
    minifigs: list[MinifigSummary] = []

    if inventory:
        inv_parts = db.scalars(
            select(InventoryPart)
            .options(joinedload(InventoryPart.part), joinedload(InventoryPart.color))
            .where(InventoryPart.inventory_id == inventory.id)
            .order_by(InventoryPart.part_num)
        ).all()
        parts = [
            InventoryPartDetail(
                part_num=ip.part_num,
                part_name=ip.part.name,
                color_id=ip.color_id,
                color_name=ip.color.name,
                color_rgb=ip.color.rgb,
                quantity=ip.quantity,
                is_spare=ip.is_spare,
                img_url=ip.img_url,
            )
            for ip in inv_parts
        ]

        inv_minifigs = db.scalars(
            select(InventoryMinifig)
            .options(joinedload(InventoryMinifig.minifig))
            .where(InventoryMinifig.inventory_id == inventory.id)
        ).all()
        minifigs = [MinifigSummary.model_validate(im.minifig) for im in inv_minifigs]

    return SetFullDetail(
        **SetDetail.model_validate(lego_set).model_dump(),
        parts=parts,
        minifigs=minifigs,
        brickset=brickset,
    )
