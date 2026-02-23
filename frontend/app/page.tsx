import { getStats } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { Stats } from "@/types/api"
import Link from "next/link"

async function StatsCards({ stats }: { stats: Stats }) {
  const items = [
    { label: "Sets", value: stats.total_sets.toLocaleString("nl-NL") },
    { label: "Thema's", value: stats.total_themes.toLocaleString("nl-NL") },
    { label: "Onderdelen", value: stats.total_parts.toLocaleString("nl-NL") },
    { label: "Minifigs", value: stats.total_minifigs.toLocaleString("nl-NL") },
    { label: "Kleuren", value: stats.total_colors.toLocaleString("nl-NL") },
    { label: "Jaren", value: `${stats.year_min} – ${stats.year_max}` },
  ]

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
      {items.map((item) => (
        <Card key={item.label}>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">{item.label}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{item.value}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

export default async function HomePage() {
  let stats: Stats | null = null
  try {
    stats = await getStats()
  } catch {
    // DB not yet populated
  }

  return (
    <div className="space-y-12">
      {/* Hero */}
      <section className="text-center space-y-4 py-12">
        <h1 className="text-5xl font-extrabold tracking-tight">
          <span className="text-yellow-400">Brick</span>Viewer
        </h1>
        <p className="text-xl text-muted-foreground max-w-xl mx-auto">
          De complete database van alle LEGO sets ooit uitgebracht.
          Doorzoek meer dan {stats ? stats.total_sets.toLocaleString("nl-NL") : "…"} sets.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/sets"
            className="inline-flex items-center justify-center rounded-md bg-yellow-400 text-black font-semibold px-6 py-2 hover:bg-yellow-300 transition-colors"
          >
            Blader door sets
          </Link>
          <Link
            href="/themes"
            className="inline-flex items-center justify-center rounded-md border border-border px-6 py-2 font-semibold hover:bg-muted transition-colors"
          >
            Thema&apos;s
          </Link>
        </div>
      </section>

      {/* Stats */}
      {stats ? (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-muted-foreground">Database overzicht</h2>
          <StatsCards stats={stats} />
        </section>
      ) : (
        <section className="text-center py-8 text-muted-foreground">
          <p>Database nog niet gevuld. Voer het import script uit om te beginnen.</p>
          <code className="block mt-2 text-sm bg-muted rounded px-4 py-2 inline-block">
            cd backend &amp;&amp; uv run python scripts/import_csv.py
          </code>
        </section>
      )}

      {/* Top themes */}
      {stats && stats.top_themes.length > 0 && (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-muted-foreground">Top thema&apos;s</h2>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {stats.top_themes.map((theme) => (
              <Card key={theme.name} className="hover:bg-muted/50 transition-colors">
                <CardContent className="pt-4">
                  <p className="font-semibold text-sm truncate">{theme.name}</p>
                  <p className="text-muted-foreground text-xs mt-1">{theme.count} sets</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
