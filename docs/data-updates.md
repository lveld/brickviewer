# Data updates

BrickViewer haalt data op uit twee bronnen: **Rebrickable** (sets, onderdelen, minifigs, inventarissen) en **Brickset** (prijzen, datums, afmetingen, ratings, tags). Ze hebben elk een eigen update-strategie.

---

## Rebrickable

### Wat komt er vandaan?

Rebrickable biedt dagelijks bijgewerkte CSV-dumps aan via https://rebrickable.com/downloads/. We gebruiken deze bestanden:

| Bestand | Inhoud |
|---|---|
| `colors.csv` | Alle LEGO kleuren met RGB-waarden |
| `themes.csv` | Thema-hiërarchie (parent_id voor sub-thema's) |
| `part_categories.csv` | Categorieën van onderdelen |
| `parts.csv` | Alle onderdelen (~61k stuks) |
| `part_relationships.csv` | Relaties tussen onderdelen (mould, print, etc.) |
| `elements.csv` | Onderdeel+kleur combinaties met element-ID |
| `sets.csv` | Alle sets met jaar, thema, onderdelen-aantal |
| `minifigs.csv` | Alle minifiguren |
| `inventories.csv` | Koppelt set-nummers aan inventaris-IDs |
| `inventory_parts.csv` | Welke onderdelen zitten in welke inventaris (~1,5M rijen) |
| `inventory_minifigs.csv` | Welke minifigs zitten in welke inventaris |
| `inventory_sets.csv` | Sets-in-sets (bijv. bij CMF series) |

### Initiële import (eenmalig)

```bash
cd backend
uv run python scripts/import_csv.py
```

- Duurt **5–10 minuten**
- Downloadt alle CSV's automatisch naar `backend/scripts/data/`
- Slaat download over als bestand al aanwezig is
- Importeert in de juiste volgorde (FK-afhankelijkheden)

### Periodieke updates (aanbevolen: wekelijks)

Rebrickable voegt regelmatig nieuwe sets en minifigs toe. Omdat de CSV's dagelijks bijgewerkt worden, is het verwijderen van de lokale cache en opnieuw importeren de eenvoudigste aanpak:

```bash
cd backend

# Stap 1: lokale CSV cache verwijderen
rm -rf scripts/data/

# Stap 2: opnieuw importeren met verse data
uv run python scripts/import_csv.py
```

**Wat gebeurt er bij een herimporten?**

- `colors`, `themes`, `part_categories`, `parts`, `elements`, `sets`, `minifigs`, `inventories` → `ON CONFLICT DO NOTHING`: nieuwe rijen worden toegevoegd, bestaande rijen onaangeroerd gelaten
- `part_relationships`, `inventory_parts`, `inventory_minifigs`, `inventory_sets` → `TRUNCATE` + herinsert: worden volledig vervangen

> **Noot:** `ON CONFLICT DO NOTHING` betekent dat gewijzigde bestaande rijen (bijv. een set krijgt een gecorrigeerd onderdelen-aantal) niet automatisch bijgewerkt worden. Wil je ook updates van bestaande rijen, vervang dan het import-commando door een volledige herinstallatie of switch naar `ON CONFLICT DO UPDATE` in het script. Voor de meeste use-cases is `DO NOTHING` voldoende.

### Rebrickable API

Rebrickable heeft ook een REST API (https://rebrickable.com/api/) voor real-time data. De API heeft een limiet van ~60 req/min en is vooral nuttig voor:
- **Gebruikerscollecties** (toekomstige feature)
- **Individuele set lookups** voor de meest actuele data

De API is momenteel nog niet geïmplementeerd in de update-pipeline; de CSV-aanpak is voor bulkdata efficiënter.

---

## Brickset

### Wat komt er vandaan?

Brickset biedt extra set-informatie via hun API v3 (https://brickset.com/api/v3.asmx). Dit zijn velden die Rebrickable niet heeft:

| Veld | Beschrijving |
|---|---|
| `price_us/uk/ca/de` | Adviesprijs in USD, GBP, CAD en EUR |
| `launch_date` | Datum eerste beschikbaarheid |
| `exit_date` | Datum uit productie |
| `availability` | Status (bijv. "LEGO exclusive", "Retail") |
| `packaging_type` | Verpakkingstype (bijv. "Box", "Polybag") |
| `age_min / age_max` | Aanbevolen leeftijdsbereik |
| `height/width/depth_mm` | Afmetingen van de doos in mm |
| `weight_g` | Gewicht in gram |
| `barcode_ean / barcode_upc` | Barcodes |
| `rating` | Gemiddelde gebruikersbeoordeling (0–5) |
| `review_count` | Aantal reviews |
| `owned_by / wanted_by` | Community statistieken |
| `description` | Officiële HTML-beschrijving van LEGO |
| `tags` | Inhoudstags (bijv. "Starfighter", "D2C", "Han Solo") |

### API limieten

- **100 calls per dag** (alleen `getSets` telt mee)
- **Max 500 sets per call**
- Met pageSize=500 zijn ~78 calls nodig voor een volledige sync → past in één dag

### Initiële sync (eenmalig)

```bash
cd backend
uv run python scripts/sync_brickset.py
```

- Itereert **jaar voor jaar** van 1949 tot heden
- ~78–95 API calls (jaren met >500 sets krijgen meerdere pagina's)
- Duurt **2–3 minuten**
- Slaat alleen sets op die ook in de Rebrickable database staan

### Periodieke updates (aanbevolen: wekelijks)

Gebruik de `--days` parameter voor een delta-sync. Dit haalt alleen sets op die Brickset in de afgelopen N dagen heeft bijgewerkt:

```bash
cd backend

# Alleen sets gewijzigd in de laatste 7 dagen (~1–5 API calls)
uv run python scripts/sync_brickset.py --days 7
```

Voor een maandelijkse run:
```bash
uv run python scripts/sync_brickset.py --days 30
```

### Enkele set bijwerken

```bash
cd backend
uv run python scripts/sync_brickset.py --set-num 75192-1
```

Handig om snel te controleren of data klopt, of om een set handmatig te vernieuwen.

### Volledige hersync

Als je alle Brickset data wil verversen (bijv. na een lange periode of na schema-wijzigingen):

```bash
cd backend
uv run python scripts/sync_brickset.py
```

De script gebruikt `ON CONFLICT DO UPDATE`, dus alle bestaande rijen worden overschreven met de nieuwste data.

---

## Gecombineerde update-routine

Aanbevolen weekelijkse routine (bijv. elke maandag):

```bash
cd /pad/naar/brickviewer/backend

# 1. Rebrickable: verse CSV's ophalen en importeren
rm -rf scripts/data/
uv run python scripts/import_csv.py

# 2. Brickset: alleen gewijzigde sets bijwerken
uv run python scripts/sync_brickset.py --days 7
```

Later (bij productie-deployment) kan dit als een cron-job of scheduled task worden ingericht.

---

## Databronnen vergelijking

| | Rebrickable | Brickset |
|---|---|---|
| **Sterkte** | Onderdelen, inventarissen, minifigs | Prijzen, datums, community, beschrijvingen |
| **Update frequentie** | Dagelijks (CSV) | Continu (API) |
| **Onze sync** | Wekelijks via CSV herdownload | Wekelijks via `--days 7` |
| **API limiet** | 60 req/min | 100 req/dag (`getSets`) |
| **Bulk aanpak** | CSV download (<15MB totaal) | Jaar-voor-jaar iteratie |
| **Sets die ontbreken** | ~2.600 sets die Brickset wél heeft | ~enkele sets die Rebrickable wél heeft |

> Sets die in Brickset maar niet in Rebrickable staan worden **niet opgeslagen** (Rebrickable is de gezaghebbende bron voor set-nummers).
