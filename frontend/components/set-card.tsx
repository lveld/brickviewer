import Link from "next/link"
import Image from "next/image"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { SetSummary } from "@/types/api"

export function SetCard({ set }: { set: SetSummary }) {
  return (
    <Link href={`/sets/${set.set_num}`}>
      <Card className="hover:bg-muted/50 transition-colors overflow-hidden group">
        <div className="aspect-square bg-muted relative">
          {set.img_url ? (
            <Image
              src={set.img_url}
              alt={set.name}
              fill
              className="object-contain p-2 group-hover:scale-105 transition-transform"
              sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center text-4xl text-muted-foreground">
              ⬛
            </div>
          )}
        </div>
        <CardContent className="pt-3 pb-4 space-y-1">
          <p className="font-semibold text-sm leading-tight line-clamp-2">{set.name}</p>
          <div className="flex items-center justify-between">
            <Badge variant="secondary" className="text-xs">{set.set_num}</Badge>
            <span className="text-xs text-muted-foreground">{set.year}</span>
          </div>
          <p className="text-xs text-muted-foreground">{set.num_parts} onderdelen</p>
        </CardContent>
      </Card>
    </Link>
  )
}
