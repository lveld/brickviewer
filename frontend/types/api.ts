export interface Theme {
  id: number
  name: string
  parent_id: number | null
}

export interface SetSummary {
  set_num: string
  name: string
  year: number
  theme_id: number
  num_parts: number
  img_url: string | null
}

export interface BricksetInfo {
  price_us: number | null
  price_uk: number | null
  price_ca: number | null
  price_de: number | null
  launch_date: string | null
  exit_date: string | null
  availability: string | null
  packaging_type: string | null
  age_min: number | null
  age_max: number | null
  height_mm: number | null
  width_mm: number | null
  depth_mm: number | null
  weight_g: number | null
  barcode_ean: string | null
  rating: number | null
  review_count: number | null
  owned_by: number | null
  wanted_by: number | null
  description: string | null
  tags: string[] | null
  last_synced: string | null
}

export interface SetDetail extends SetSummary {
  theme: Theme
  parts: InventoryPartDetail[]
  minifigs: MinifigSummary[]
  brickset: BricksetInfo | null
}

export interface MinifigSummary {
  fig_num: string
  name: string
  num_parts: number
  img_url: string | null
}

export interface InventoryPartDetail {
  part_num: string
  part_name: string
  color_id: number
  color_name: string
  color_rgb: string
  quantity: number
  is_spare: boolean
  img_url: string | null
}

export interface PaginatedSets {
  total: number
  page: number
  page_size: number
  results: SetSummary[]
}

export interface PaginatedMinifigs {
  total: number
  page: number
  page_size: number
  results: MinifigSummary[]
}

export interface Stats {
  total_sets: number
  total_themes: number
  total_parts: number
  total_minifigs: number
  total_colors: number
  year_min: number
  year_max: number
  sets_per_year: { year: number; count: number }[]
  top_themes: { name: string; count: number }[]
}
