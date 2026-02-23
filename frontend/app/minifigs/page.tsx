"use client"

import { useEffect, useState } from "react"
import { getMinifigs } from "@/lib/api"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import Image from "next/image"
import type { PaginatedMinifigs } from "@/types/api"

export default function MinifigsPage() {
  const [search, setSearch] = useState("")
  const [page, setPage] = useState(1)
  const [data, setData] = useState<PaginatedMinifigs | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getMinifigs({ page, page_size: 24, search: search || undefined })
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [page, search])

  const totalPages = data ? Math.ceil(data.total / 24) : 1

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Minifiguren</h1>

      <Input
        placeholder="Zoek minifiguren..."
        value={search}
        onChange={(e) => { setSearch(e.target.value); setPage(1) }}
        className="max-w-sm"
      />

      {data && (
        <p className="text-sm text-muted-foreground">
          {data.total.toLocaleString("nl-NL")} minifiguren gevonden
        </p>
      )}

      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4">
          {Array.from({ length: 24 }).map((_, i) => (
            <div key={i} className="space-y-2">
              <Skeleton className="aspect-square rounded-lg" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4">
          {data?.results.map((fig) => (
            <Card key={fig.fig_num} className="overflow-hidden">
              <div className="aspect-square bg-muted relative">
                {fig.img_url ? (
                  <Image
                    src={fig.img_url}
                    alt={fig.name}
                    fill
                    className="object-contain p-2"
                    sizes="200px"
                  />
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center text-4xl">🧍</div>
                )}
              </div>
              <CardContent className="pt-2 pb-3 space-y-1">
                <p className="text-xs font-medium leading-tight line-clamp-2">{fig.name}</p>
                <Badge variant="secondary" className="text-xs">{fig.fig_num}</Badge>
                <p className="text-xs text-muted-foreground">{fig.num_parts} onderdelen</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {data && totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button variant="outline" size="sm" onClick={() => setPage(1)} disabled={page === 1}>«</Button>
          <Button variant="outline" size="sm" onClick={() => setPage(p => p - 1)} disabled={page === 1}>‹</Button>
          <span className="text-sm text-muted-foreground px-4">Pagina {page} van {totalPages}</span>
          <Button variant="outline" size="sm" onClick={() => setPage(p => p + 1)} disabled={page === totalPages}>›</Button>
          <Button variant="outline" size="sm" onClick={() => setPage(totalPages)} disabled={page === totalPages}>»</Button>
        </div>
      )}
    </div>
  )
}
