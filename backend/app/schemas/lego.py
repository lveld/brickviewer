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


class SetFullDetail(SetDetail):
    minifigs: list[MinifigSummary] = []
    parts: list[InventoryPartDetail] = []


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
