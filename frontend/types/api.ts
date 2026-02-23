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

export interface SetDetail extends SetSummary {
  theme: Theme
  parts: InventoryPartDetail[]
  minifigs: MinifigSummary[]
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
