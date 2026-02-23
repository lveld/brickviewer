import { getSet } from "@/lib/api"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { BricksetInfo } from "@/types/api"
import Image from "next/image"
import Link from "next/link"
import { notFound } from "next/navigation"

function StarRating({ rating }: { rating: number }) {
  const full = Math.floor(rating)
  const half = rating % 1 >= 0.5
  return (
    <span className="flex items-center gap-0.5" title={`${rating}/5`}>
      {Array.from({ length: 5 }).map((_, i) => (
        <span key={i} className={i < full ? "text-yellow-400" : half && i === full ? "text-yellow-400/50" : "text-muted"}>
          ★
        </span>
      ))}
      <span className="ml-1 text-sm text-muted-foreground">{rating.toFixed(1)}</span>
    </span>
  )
}

function PriceCard({ bs }: { bs: BricksetInfo }) {
  const prices = [
    { label: "🇩🇪 DE", value: bs.price_de, currency: "€" },
    { label: "🇬🇧 UK", value: bs.price_uk, currency: "£" },
    { label: "🇺🇸 US", value: bs.price_us, currency: "$" },
    { label: "🇨🇦 CA", value: bs.price_ca, currency: "CA$" },
  ].filter((p) => p.value != null)

  if (!prices.length) return null

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Adviesprijs</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {prices.map((p) => (
            <div key={p.label} className="text-center bg-muted/50 rounded-lg p-3">
              <div className="text-xs text-muted-foreground mb-1">{p.label}</div>
              <div className="font-bold text-lg">
                {p.currency}{p.value!.toLocaleString("nl-NL", { minimumFractionDigits: 2 })}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export default async function SetDetailPage({
  params,
}: {
  params: Promise<{ set_num: string }>
}) {
  const { set_num } = await params

  let set
  try {
    set = await getSet(set_num)
  } catch {
    notFound()
  }

  const bs = set.brickset
  const regularParts = set.parts.filter((p) => !p.is_spare)
  const spareParts = set.parts.filter((p) => p.is_spare)

  return (
    <div className="space-y-8">
      {/* Breadcrumb */}
      <nav className="text-sm text-muted-foreground flex gap-2">
        <Link href="/sets" className="hover:text-foreground">Sets</Link>
        <span>/</span>
        <span>{set.name}</span>
      </nav>

      {/* Header */}
      <div className="flex flex-col md:flex-row gap-8">
        <div className="w-full md:w-64 shrink-0">
          <div className="aspect-square bg-muted rounded-lg relative">
            {set.img_url ? (
              <Image src={set.img_url} alt={set.name} fill className="object-contain p-4" sizes="256px" priority />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center text-6xl text-muted-foreground">⬛</div>
            )}
          </div>
        </div>

        <div className="space-y-4 flex-1">
          <div>
            <div className="flex flex-wrap gap-2 mb-2">
              <Badge variant="secondary">{set.set_num}</Badge>
              {bs?.availability && <Badge variant="outline">{bs.availability}</Badge>}
              {bs?.packaging_type && <Badge variant="outline">{bs.packaging_type}</Badge>}
            </div>
            <h1 className="text-3xl font-bold">{set.name}</h1>
          </div>

          <dl className="grid grid-cols-2 gap-x-8 gap-y-2 text-sm">
            <dt className="text-muted-foreground">Jaar</dt>
            <dd className="font-medium">{set.year}</dd>
            <dt className="text-muted-foreground">Thema</dt>
            <dd className="font-medium">{set.theme.name}</dd>
            <dt className="text-muted-foreground">Onderdelen</dt>
            <dd className="font-medium">{set.num_parts.toLocaleString("nl-NL")}</dd>
            <dt className="text-muted-foreground">Minifigs</dt>
            <dd className="font-medium">{set.minifigs.length}</dd>
            {bs?.age_min != null && (
              <>
                <dt className="text-muted-foreground">Leeftijd</dt>
                <dd className="font-medium">{bs.age_min}{bs.age_max ? `–${bs.age_max}` : "+"} jaar</dd>
              </>
            )}
            {bs?.launch_date && (
              <>
                <dt className="text-muted-foreground">Uitgebracht</dt>
                <dd className="font-medium">{new Date(bs.launch_date).toLocaleDateString("nl-NL", { year: "numeric", month: "long" })}</dd>
              </>
            )}
            {bs?.exit_date && (
              <>
                <dt className="text-muted-foreground">Uit productie</dt>
                <dd className="font-medium">{new Date(bs.exit_date).toLocaleDateString("nl-NL", { year: "numeric", month: "long" })}</dd>
              </>
            )}
            {bs?.height_mm && (
              <>
                <dt className="text-muted-foreground">Afmetingen</dt>
                <dd className="font-medium text-xs">
                  {bs.height_mm}×{bs.width_mm}×{bs.depth_mm} mm
                  {bs.weight_g ? ` · ${bs.weight_g}g` : ""}
                </dd>
              </>
            )}
            {bs?.barcode_ean && (
              <>
                <dt className="text-muted-foreground">EAN</dt>
                <dd className="font-medium font-mono text-xs">{bs.barcode_ean}</dd>
              </>
            )}
          </dl>

          {/* Rating */}
          {bs?.rating != null && bs.rating > 0 && (
            <div className="flex items-center gap-3">
              <StarRating rating={bs.rating} />
              {bs.review_count != null && (
                <span className="text-sm text-muted-foreground">{bs.review_count} reviews</span>
              )}
              {bs.owned_by != null && (
                <span className="text-sm text-muted-foreground">· {bs.owned_by.toLocaleString("nl-NL")} eigenaren</span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Prijs */}
      {bs && <PriceCard bs={bs} />}

      {/* Tags */}
      {bs?.tags && bs.tags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {bs.tags.map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs">{tag}</Badge>
          ))}
        </div>
      )}

      {/* Beschrijving */}
      {bs?.description && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Beschrijving</CardTitle>
          </CardHeader>
          <CardContent>
            <div
              className="text-sm text-muted-foreground leading-relaxed prose prose-invert prose-sm max-w-none"
              dangerouslySetInnerHTML={{ __html: bs.description }}
            />
          </CardContent>
        </Card>
      )}

      {/* Minifigs */}
      {set.minifigs.length > 0 && (
        <Card>
          <CardHeader><CardTitle>Minifiguren ({set.minifigs.length})</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4">
              {set.minifigs.map((fig) => (
                <div key={fig.fig_num} className="text-center space-y-1">
                  <div className="aspect-square bg-muted rounded relative">
                    {fig.img_url ? (
                      <Image src={fig.img_url} alt={fig.name} fill className="object-contain p-1" sizes="150px" />
                    ) : (
                      <div className="absolute inset-0 flex items-center justify-center text-2xl">🧍</div>
                    )}
                  </div>
                  <p className="text-xs leading-tight">{fig.name}</p>
                  <Badge variant="outline" className="text-xs">{fig.fig_num}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Onderdelen */}
      {regularParts.length > 0 && (
        <Card>
          <CardHeader><CardTitle>Onderdelen ({regularParts.length} unieke)</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
              {regularParts.slice(0, 60).map((part, i) => (
                <div key={i} className="flex items-center gap-3 text-sm py-1.5 border-b border-border/40 last:border-0">
                  <div className="w-4 h-4 rounded-full shrink-0 border border-border" style={{ backgroundColor: `#${part.color_rgb}` }} />
                  <span className="flex-1 truncate">{part.part_name}</span>
                  <span className="text-muted-foreground shrink-0">{part.color_name}</span>
                  <Badge variant="secondary" className="text-xs shrink-0">×{part.quantity}</Badge>
                </div>
              ))}
              {regularParts.length > 60 && (
                <p className="text-sm text-muted-foreground col-span-full pt-2">+ {regularParts.length - 60} meer onderdelen</p>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Reserve-onderdelen */}
      {spareParts.length > 0 && (
        <Card>
          <CardHeader><CardTitle>Reserve-onderdelen ({spareParts.length})</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
              {spareParts.map((part, i) => (
                <div key={i} className="flex items-center gap-3 text-sm py-1.5 border-b border-border/40 last:border-0">
                  <div className="w-4 h-4 rounded-full shrink-0 border border-border" style={{ backgroundColor: `#${part.color_rgb}` }} />
                  <span className="flex-1 truncate">{part.part_name}</span>
                  <Badge variant="secondary" className="text-xs shrink-0">×{part.quantity}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
