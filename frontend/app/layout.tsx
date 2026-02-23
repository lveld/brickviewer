import type { Metadata } from "next"
import { Geist } from "next/font/google"
import Link from "next/link"
import "./globals.css"

const geist = Geist({ variable: "--font-geist-sans", subsets: ["latin"] })

export const metadata: Metadata = {
  title: "BrickViewer – LEGO Set Database",
  description: "Browse every LEGO set ever released",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="nl" className="dark">
      <body className={`${geist.variable} font-sans min-h-screen bg-background text-foreground antialiased`}>
        <header className="border-b border-border/40 bg-background/95 backdrop-blur sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 h-14 flex items-center gap-8">
            <Link href="/" className="font-bold text-lg tracking-tight flex items-center gap-2">
              <span className="text-yellow-400">⬛</span> BrickViewer
            </Link>
            <nav className="flex items-center gap-6 text-sm text-muted-foreground">
              <Link href="/sets" className="hover:text-foreground transition-colors">Sets</Link>
              <Link href="/themes" className="hover:text-foreground transition-colors">Thema&apos;s</Link>
              <Link href="/minifigs" className="hover:text-foreground transition-colors">Minifigs</Link>
            </nav>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 py-8">
          {children}
        </main>
      </body>
    </html>
  )
}
