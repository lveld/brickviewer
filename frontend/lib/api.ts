import type { PaginatedMinifigs, PaginatedSets, SetDetail, Stats, Theme } from "@/types/api"

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api"

async function fetcher<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { next: { revalidate: 300 } })
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`)
  return res.json() as Promise<T>
}

export function getStats(): Promise<Stats> {
  return fetcher<Stats>("/stats")
}

export function getThemes(): Promise<Theme[]> {
  return fetcher<Theme[]>("/themes")
}

export function getSets(params: {
  page?: number
  page_size?: number
  theme_id?: number | null
  year_min?: number | null
  year_max?: number | null
  search?: string
}): Promise<PaginatedSets> {
  const query = new URLSearchParams()
  if (params.page) query.set("page", String(params.page))
  if (params.page_size) query.set("page_size", String(params.page_size))
  if (params.theme_id) query.set("theme_id", String(params.theme_id))
  if (params.year_min) query.set("year_min", String(params.year_min))
  if (params.year_max) query.set("year_max", String(params.year_max))
  if (params.search) query.set("search", params.search)
  return fetcher<PaginatedSets>(`/sets?${query.toString()}`)
}

export function getSet(setNum: string): Promise<SetDetail> {
  return fetcher<SetDetail>(`/sets/${setNum}`)
}

export function getMinifigs(params: {
  page?: number
  page_size?: number
  search?: string
}): Promise<PaginatedMinifigs> {
  const query = new URLSearchParams()
  if (params.page) query.set("page", String(params.page))
  if (params.page_size) query.set("page_size", String(params.page_size))
  if (params.search) query.set("search", params.search)
  return fetcher<PaginatedMinifigs>(`/minifigs?${query.toString()}`)
}
