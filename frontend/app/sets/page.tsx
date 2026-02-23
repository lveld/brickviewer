"use client"

import { useEffect, useState } from "react"
import { getSets, getThemes } from "@/lib/api"
import { SetCard } from "@/components/set-card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import type { PaginatedSets, Theme } from "@/types/api"
import { useRouter, useSearchParams } from "next/navigation"

function SetGridSkeleton() {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
      {Array.from({ length: 24 }).map((_, i) => (
        <div key={i} className="space-y-2">
          <Skeleton className="aspect-square rounded-lg" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </div>
      ))}
    </div>
  )
}

export default function SetsPage() {
  const searchParams = useSearchParams()
  const router = useRouter()

  const [search, setSearch] = useState(searchParams.get("search") ?? "")
  const [themeId, setThemeId] = useState<number | null>(
    searchParams.get("theme_id") ? Number(searchParams.get("theme_id")) : null
  )
  const [page, setPage] = useState(1)
  const [data, setData] = useState<PaginatedSets | null>(null)
  const [themes, setThemes] = useState<Theme[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getThemes().then(setThemes).catch(console.error)
  }, [])

  useEffect(() => {
    setLoading(true)
    getSets({ page, page_size: 24, search: search || undefined, theme_id: themeId })
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [page, search, themeId])

  const totalPages = data ? Math.ceil(data.total / 24) : 1

  function handleSearch(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setPage(1)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4">
        <form onSubmit={handleSearch} className="flex gap-2 flex-1">
          <Input
            placeholder="Zoek sets..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            className="max-w-sm"
          />
        </form>
        <select
          className="rounded-md border border-input bg-background px-3 py-2 text-sm"
          value={themeId ?? ""}
          onChange={(e) => { setThemeId(e.target.value ? Number(e.target.value) : null); setPage(1) }}
        >
          <option value="">Alle thema&apos;s</option>
          {themes.map((t) => (
            <option key={t.id} value={t.id}>{t.name}</option>
          ))}
        </select>
      </div>

      {data && (
        <p className="text-sm text-muted-foreground">
          {data.total.toLocaleString("nl-NL")} sets gevonden
        </p>
      )}

      {loading ? (
        <SetGridSkeleton />
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
          {data?.results.map((set) => <SetCard key={set.set_num} set={set} />)}
        </div>
      )}

      {/* Pagination */}
      {data && totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button variant="outline" size="sm" onClick={() => setPage(1)} disabled={page === 1}>
            «
          </Button>
          <Button variant="outline" size="sm" onClick={() => setPage(p => p - 1)} disabled={page === 1}>
            ‹
          </Button>
          <span className="text-sm text-muted-foreground px-4">
            Pagina {page} van {totalPages}
          </span>
          <Button variant="outline" size="sm" onClick={() => setPage(p => p + 1)} disabled={page === totalPages}>
            ›
          </Button>
          <Button variant="outline" size="sm" onClick={() => setPage(totalPages)} disabled={page === totalPages}>
            »
          </Button>
        </div>
      )}
    </div>
  )
}
