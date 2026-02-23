from datetime import date, datetime

from pydantic import BaseModel


class ThemeBase(BaseModel):
    id: int
    name: str
    parent_id: int | None = None


class Theme(ThemeBase):
    model_config = {"from_attributes": True}


class ThemeTree(Theme):
    children: list["ThemeTree"] = []


class ColorSchema(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    name: str
    rgb: str
    is_trans: bool


class SetSummary(BaseModel):
    model_config = {"from_attributes": True}
    set_num: str
    name: str
    year: int
    theme_id: int
    num_parts: int
    img_url: str | None = None


class SetDetail(SetSummary):
    theme: Theme


class MinifigSummary(BaseModel):
    model_config = {"from_attributes": True}
    fig_num: str
    name: str
    num_parts: int
    img_url: str | None = None


class InventoryPartDetail(BaseModel):
    model_config = {"from_attributes": True}
    part_num: str
    part_name: str
    color_id: int
    color_name: str
    color_rgb: str
    quantity: int
    is_spare: bool
    img_url: str | None = None


class BricksetInfo(BaseModel):
    model_config = {"from_attributes": True}
    price_us: float | None = None
    price_uk: float | None = None
    price_ca: float | None = None
    price_de: float | None = None
    launch_date: date | None = None
    exit_date: date | None = None
    availability: str | None = None
    packaging_type: str | None = None
    age_min: int | None = None
    age_max: int | None = None
    height_mm: float | None = None
    width_mm: float | None = None
    depth_mm: float | None = None
    weight_g: float | None = None
    barcode_ean: str | None = None
    rating: float | None = None
    review_count: int | None = None
    owned_by: int | None = None
    wanted_by: int | None = None
    description: str | None = None
    tags: list[str] | None = None
    last_synced: datetime | None = None


class SetFullDetail(SetDetail):
    minifigs: list[MinifigSummary] = []
    parts: list[InventoryPartDetail] = []
    brickset: BricksetInfo | None = None


class PaginatedSets(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[SetSummary]


class PaginatedMinifigs(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[MinifigSummary]


class Stats(BaseModel):
    total_sets: int
    total_themes: int
    total_parts: int
    total_minifigs: int
    total_colors: int
    year_min: int
    year_max: int
    sets_per_year: list[dict]
    top_themes: list[dict]
