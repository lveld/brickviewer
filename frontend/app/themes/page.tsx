import { getThemes, getSets } from "@/lib/api"
import { Card, CardContent } from "@/components/ui/card"
import Link from "next/link"

export default async function ThemesPage() {
  let themes: Awaited<ReturnType<typeof getThemes>> = []
  try {
    themes = await getThemes()
  } catch {
    // API not available
  }

  // Group by parent
  const rootThemes = themes.filter((t) => t.parent_id === null)
  const childrenMap = new Map<number, typeof themes>()
  for (const t of themes) {
    if (t.parent_id !== null) {
      const list = childrenMap.get(t.parent_id) ?? []
      list.push(t)
      childrenMap.set(t.parent_id, list)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Thema&apos;s</h1>
      <p className="text-muted-foreground">{themes.length} thema&apos;s totaal</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {rootThemes.map((theme) => {
          const children = childrenMap.get(theme.id) ?? []
          return (
            <Card key={theme.id} className="hover:bg-muted/50 transition-colors">
              <CardContent className="pt-4 space-y-2">
                <Link
                  href={`/sets?theme_id=${theme.id}`}
                  className="font-semibold hover:text-yellow-400 transition-colors"
                >
                  {theme.name}
                </Link>
                {children.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {children.slice(0, 6).map((child) => (
                      <Link
                        key={child.id}
                        href={`/sets?theme_id=${child.id}`}
                        className="text-xs text-muted-foreground hover:text-foreground bg-muted rounded px-2 py-0.5 transition-colors"
                      >
                        {child.name}
                      </Link>
                    ))}
                    {children.length > 6 && (
                      <span className="text-xs text-muted-foreground px-2 py-0.5">
                        +{children.length - 6} meer
                      </span>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
