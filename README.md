# BrickViewer

Een moderne website met de complete database van alle LEGO sets ooit uitgebracht.

**Databronnen:**
- [Rebrickable](https://rebrickable.com) — sets, onderdelen, minifigs, inventarissen
- [Brickset](https://brickset.com) — prijzen, datums, afmetingen, ratings, tags

## Tech Stack

| Laag | Technologie |
|---|---|
| Frontend | Next.js 14 (App Router) + TypeScript + Tailwind CSS + shadcn/ui |
| Backend | FastAPI (Python) + SQLAlchemy + Alembic |
| Database | PostgreSQL via Docker Compose |
| Package manager | uv (Python), npm (Node) |

## Lokaal opstarten

### Vereisten

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Node.js 18+
- Python 3.11+ met [uv](https://docs.astral.sh/uv/)
- Brickset API key — gratis aanvragen op https://brickset.com/tools/webservices/requestkey

### 1. Repo klonen

```bash
git clone https://github.com/lveld/brickviewer.git
cd brickviewer
```

### 2. Omgevingsvariabelen instellen

```bash
cp .env.example .env
# Vul BRICKSET_API_KEY in met je eigen key
```

### 3. Database starten

```bash
docker compose up -d
```

> PostgreSQL draait op poort **5433** (niet 5432, om conflicten met lokale installaties te vermijden).

### 4. Backend installeren en migraties uitvoeren

```bash
cd backend
uv sync
uv run alembic upgrade head
```

### 5. Data importeren

```bash
# Rebrickable: ~5-10 minuten, downloadt ~15MB aan CSV's
uv run python scripts/import_csv.py

# Brickset: ~2-3 minuten, 78-95 API calls
uv run python scripts/sync_brickset.py
```

### 6. Backend starten

```bash
uv run uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Interactieve docs: http://localhost:8000/docs

### 7. Frontend starten (nieuwe terminal)

```bash
cd frontend
npm install
npm run dev
```

- Website: http://localhost:3000

---

## Project structuur

```
brickviewer/
├── backend/
│   ├── app/
│   │   ├── api/routes/     # FastAPI endpoints (sets, themes, minifigs, stats)
│   │   ├── models/         # SQLAlchemy modellen
│   │   ├── schemas/        # Pydantic response schemas
│   │   └── core/           # Config, database connectie
│   ├── scripts/
│   │   ├── import_csv.py   # Eenmalige Rebrickable CSV import
│   │   └── sync_brickset.py # Brickset data sync
│   └── alembic/            # Database migraties
├── frontend/
│   ├── app/                # Next.js App Router pagina's
│   ├── components/         # React componenten
│   ├── lib/                # API client
│   └── types/              # TypeScript types
├── docs/
│   └── data-updates.md     # Update-strategie voor beide databronnen
└── docker-compose.yml
```

---

## API endpoints

| Methode | Pad | Beschrijving |
|---|---|---|
| GET | `/api/sets` | Sets (paginering, filter op thema/jaar/zoekterm) |
| GET | `/api/sets/{set_num}` | Set detail incl. onderdelen, minifigs en Brickset data |
| GET | `/api/themes` | Alle thema's |
| GET | `/api/minifigs` | Minifigs (paginering, zoekterm) |
| GET | `/api/stats` | Database statistieken |

---

## Data bijhouden

Zie **[docs/data-updates.md](docs/data-updates.md)** voor de volledige update-strategie.

Kort samengevat:

```bash
cd backend

# Wekelijkse update (beide bronnen)
rm -rf scripts/data/ && uv run python scripts/import_csv.py
uv run python scripts/sync_brickset.py --days 7
```

---

## Roadmap

- [x] v0.1 — Basis database + browser (Rebrickable + Brickset)
- [ ] v0.2 — Data analyse en grafieken
- [ ] v0.3 — Eigen collectie bijhouden
- [ ] v1.0 — Productie deployment
