import { getSet } from "@/lib/api"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import Image from "next/image"
import Link from "next/link"
import { notFound } from "next/navigation"

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
        {/* Image */}
        <div className="w-full md:w-64 shrink-0">
          <div className="aspect-square bg-muted rounded-lg relative">
            {set.img_url ? (
              <Image
                src={set.img_url}
                alt={set.name}
                fill
                className="object-contain p-4"
                sizes="256px"
                priority
              />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center text-6xl text-muted-foreground">
                ⬛
              </div>
            )}
          </div>
        </div>

        {/* Info */}
        <div className="space-y-4">
          <div>
            <Badge variant="secondary" className="mb-2">{set.set_num}</Badge>
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
          </dl>
        </div>
      </div>

      {/* Minifigs */}
      {set.minifigs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Minifiguren ({set.minifigs.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4">
              {set.minifigs.map((fig) => (
                <div key={fig.fig_num} className="text-center space-y-1">
                  <div className="aspect-square bg-muted rounded relative">
                    {fig.img_url ? (
                      <Image
                        src={fig.img_url}
                        alt={fig.name}
                        fill
                        className="object-contain p-1"
                        sizes="150px"
                      />
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

      {/* Parts */}
      {regularParts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Onderdelen ({regularParts.length} unieke)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
              {regularParts.slice(0, 60).map((part, i) => (
                <div key={i} className="flex items-center gap-3 text-sm py-1.5 border-b border-border/40 last:border-0">
                  <div
                    className="w-4 h-4 rounded-full shrink-0 border border-border"
                    style={{ backgroundColor: `#${part.color_rgb}` }}
                  />
                  <span className="flex-1 truncate">{part.part_name}</span>
                  <span className="text-muted-foreground shrink-0">{part.color_name}</span>
                  <Badge variant="secondary" className="text-xs shrink-0">×{part.quantity}</Badge>
                </div>
              ))}
              {regularParts.length > 60 && (
                <p className="text-sm text-muted-foreground col-span-full pt-2">
                  + {regularParts.length - 60} meer onderdelen
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Spare parts */}
      {spareParts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Reserve-onderdelen ({spareParts.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
              {spareParts.map((part, i) => (
                <div key={i} className="flex items-center gap-3 text-sm py-1.5 border-b border-border/40 last:border-0">
                  <div
                    className="w-4 h-4 rounded-full shrink-0 border border-border"
                    style={{ backgroundColor: `#${part.color_rgb}` }}
                  />
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
