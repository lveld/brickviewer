# BrickViewer

Een moderne website met de complete database van alle LEGO sets ooit uitgebracht, powered by [Rebrickable](https://rebrickable.com).

## Tech Stack

- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI (Python) + SQLAlchemy
- **Database**: PostgreSQL (via Docker Compose)
- **Data**: Rebrickable CSV dumps + API

## Lokaal draaien

### Vereisten

- Docker Desktop
- Node.js 18+
- Python 3.11+ met [uv](https://docs.astral.sh/uv/)

### 1. Kloon de repo

```bash
git clone https://github.com/YOUR_USERNAME/brickviewer.git
cd brickviewer
```

### 2. Omgevingsvariabelen instellen

```bash
cp .env.example .env
# Optioneel: voeg je Rebrickable API key toe in .env
```

### 3. Database starten

```bash
docker compose up -d
```

### 4. Backend dependencies installeren

```bash
cd backend
uv sync
```

### 5. Database migraties uitvoeren

```bash
cd backend
uv run alembic upgrade head
```

### 6. Data importeren (eenmalig, ~5-10 minuten)

```bash
cd backend
uv run python scripts/import_csv.py
```

### 7. Backend starten

```bash
cd backend
uv run uvicorn app.main:app --reload
```

De API is beschikbaar op http://localhost:8000
API documentatie: http://localhost:8000/docs

### 8. Frontend starten

```bash
cd frontend
npm install
npm run dev
```

De website is beschikbaar op http://localhost:3000

## Project structuur

```
brickviewer/
├── backend/
│   ├── app/
│   │   ├── api/routes/    # FastAPI endpoints
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── core/          # Config, database
│   ├── scripts/
│   │   └── import_csv.py  # Rebrickable CSV import
│   └── alembic/           # Database migraties
├── frontend/
│   ├── app/               # Next.js App Router pagina's
│   ├── components/        # React componenten
│   ├── lib/               # API client
│   └── types/             # TypeScript types
└── docker-compose.yml
```

## API endpoints

| Methode | Pad | Beschrijving |
|---------|-----|--------------|
| GET | `/api/sets` | Sets ophalen (paginering, filters) |
| GET | `/api/sets/{set_num}` | Set detail |
| GET | `/api/themes` | Alle thema's |
| GET | `/api/minifigs` | Minifigs (paginering, zoek) |
| GET | `/api/stats` | Database statistieken |

## Roadmap

- [ ] v0.1 — Basis database + browser
- [ ] v0.2 — Data analyse en grafieken
- [ ] v0.3 — Eigen collectie bijhouden
- [ ] v1.0 — Productie deployment
