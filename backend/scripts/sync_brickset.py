"""
Synchroniseer Brickset data naar de brickset_data tabel.

Gebruik:
    # Volledige sync (alle sets)
    uv run python scripts/sync_brickset.py

    # Delta sync (alleen sets gewijzigd in de laatste N dagen)
    uv run python scripts/sync_brickset.py --days 7

    # Enkele set testen
    uv run python scripts/sync_brickset.py --set-num 75192-1

De Brickset API staat 100 calls/dag toe. Met pageSize=500 zijn ~52 calls
nodig voor de volledige dataset (~26.000 sets) — past ruim in één dag.
"""

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.lego import BricksetData, Set
import app.models  # noqa: F401

API_BASE = "https://brickset.com/api/v3.asmx"
PAGE_SIZE = 500
RATE_LIMIT_DELAY = 1.2  # seconden tussen API calls


# ---------------------------------------------------------------------------
# Brickset API client
# ---------------------------------------------------------------------------

def _api_call(method: str, params: dict) -> dict:
    params = {"apiKey": settings.brickset_api_key, **params}
    url = f"{API_BASE}/{method}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_page(page: int, updated_since: str | None = None) -> dict:
    """Delta sync: haal recent gewijzigde sets op."""
    query: dict = {"pageSize": PAGE_SIZE, "pageNumber": page, "extendedData": 1,
                   "updatedSince": updated_since}
    return _api_call("getSets", {"params": json.dumps(query), "userHash": ""})


def fetch_year_page(year: int, page: int) -> dict:
    """Haal alle sets voor een specifiek jaar op (vereist voor bulk sync)."""
    query: dict = {"pageSize": PAGE_SIZE, "pageNumber": page, "year": year, "extendedData": 1}
    return _api_call("getSets", {"params": json.dumps(query), "userHash": ""})


def fetch_by_set_number(set_number: str) -> dict:
    """Haal één set op via Brickset set-nummer formaat (bijv. '75192-1')."""
    return _api_call("getSets", {
        "params": json.dumps({"setNumber": set_number, "extendedData": 1}),
        "userHash": "",
    })


# ---------------------------------------------------------------------------
# Data mapping
# ---------------------------------------------------------------------------

def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        # Vervang Z door +00:00 zodat fromisoformat het herkent (Python 3.11+)
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def _parse_float(value) -> float | None:
    try:
        v = float(value)
        return v if v > 0 else None
    except (TypeError, ValueError):
        return None


def _parse_int(value) -> int | None:
    try:
        v = int(value)
        return v if v >= 0 else None
    except (TypeError, ValueError):
        return None


def _clean_tag(tag: str) -> str:
    """Verwijder Brickset tag-annotaties zoals '|n' (proper noun marker)."""
    return tag.split("|")[0].strip()


def map_set(bs: dict, set_num: str) -> dict:
    lego = bs.get("LEGOCom") or {}
    dims = bs.get("dimensions") or {}
    barcodes = bs.get("barcode") or {}
    age = bs.get("ageRange") or {}
    ext = bs.get("extendedData") or {}

    # Prijzen per regio
    def region_price(code: str) -> float | None:
        return _parse_float((lego.get(code) or {}).get("retailPrice"))

    # Launch date: eerst top-level launchDate, dan uit LEGOCom regio's
    launch_date = _parse_date(bs.get("launchDate"))
    if not launch_date:
        for code in ("US", "UK", "DE", "CA"):
            launch_date = _parse_date((lego.get(code) or {}).get("dateFirstAvailable"))
            if launch_date:
                break

    # Exit date: uit LEGOCom regio's
    exit_date = None
    for code in ("US", "UK", "DE", "CA"):
        exit_date = _parse_date((lego.get(code) or {}).get("dateLastAvailable"))
        if exit_date:
            break

    # Tags opschonen
    raw_tags = ext.get("tags") or []
    if isinstance(raw_tags, str):
        raw_tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
    tags = [_clean_tag(t) for t in raw_tags if t] or None

    return {
        "set_num": set_num,
        "brickset_id": _parse_int(bs.get("setID")),
        "price_us": region_price("US"),
        "price_uk": region_price("UK"),
        "price_ca": region_price("CA"),
        "price_de": region_price("DE"),
        "launch_date": launch_date,
        "exit_date": exit_date,
        "availability": bs.get("availability") or None,
        "packaging_type": bs.get("packagingType") or None,
        "age_min": _parse_int(age.get("min")),
        "age_max": _parse_int(age.get("max")),
        "height_mm": _parse_float(dims.get("height")),
        "width_mm": _parse_float(dims.get("width")),
        "depth_mm": _parse_float(dims.get("depth")),
        "weight_g": _parse_float(dims.get("weight")),
        "barcode_ean": barcodes.get("EAN") or None,
        "barcode_upc": barcodes.get("UPC") or None,
        "item_number": bs.get("itemNumbers") or None,
        "rating": _parse_float(bs.get("rating")),
        "review_count": _parse_int(bs.get("reviewCount")),
        "owned_by": _parse_int((bs.get("collections") or {}).get("ownedBy")),
        "wanted_by": _parse_int((bs.get("collections") or {}).get("wantedBy")),
        "description": ext.get("description") or None,
        "tags": tags,
        "last_synced": datetime.now(timezone.utc).replace(tzinfo=None),
    }


# ---------------------------------------------------------------------------
# Database upsert
# ---------------------------------------------------------------------------

def upsert_rows(session, rows: list[dict]) -> None:
    if not rows:
        return
    stmt = insert(BricksetData).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["set_num"],
        set_={col: stmt.excluded[col] for col in rows[0] if col != "set_num"},
    )
    session.execute(stmt)
    session.commit()


# ---------------------------------------------------------------------------
# Sync logic
# ---------------------------------------------------------------------------

def load_known_set_nums(session) -> set[str]:
    return {row[0] for row in session.execute(select(Set.set_num))}


def _process_page(session, sets: list[dict], known: set[str]) -> tuple[int, int]:
    """Verwerk een pagina sets en sla op in DB. Geeft (synced, skipped) terug."""
    rows = []
    skipped = 0
    for bs in sets:
        set_num = f"{bs.get('number', '')}-{bs.get('numberVariant', 1)}"
        if set_num not in known:
            skipped += 1
            continue
        rows.append(map_set(bs, set_num))
    if rows:
        upsert_rows(session, rows)
    return len(rows), skipped


def sync_all() -> None:
    """Volledige sync: itereer per jaar (78 API-calls voor 1949–2026)."""
    session = SessionLocal()
    known = load_known_set_nums(session)
    print(f"  {len(known)} sets bekend in Rebrickable database")
    print("\nVolledige sync per jaar (1949–2026)...\n")

    current_year = datetime.now().year
    years = range(1949, current_year + 1)

    total_synced = 0
    total_skipped = 0
    api_calls = 0

    for year in years:
        page = 1
        year_synced = 0
        while True:
            print(f"  {year} pagina {page}...", end=" ", flush=True)
            try:
                data = fetch_year_page(year, page)
            except Exception as e:
                print(f"FOUT: {e}")
                break

            api_calls += 1
            sets = data.get("sets") or []
            total_matches = data.get("matches", 0)

            if not sets:
                print("leeg")
                break

            synced, skipped = _process_page(session, sets, known)
            year_synced += synced
            total_skipped += skipped
            print(f"{synced} gesynchroniseerd ({total_matches} totaal in {year})")

            if page * PAGE_SIZE >= total_matches:
                break
            page += 1
            time.sleep(RATE_LIMIT_DELAY)

        total_synced += year_synced

    session.close()
    print(f"\n=== Sync voltooid ===")
    print(f"  API calls: {api_calls}")
    print(f"  Gesynchroniseerd: {total_synced}")
    print(f"  Niet in Rebrickable: {total_skipped}")


def sync_delta(updated_since: str) -> None:
    """Delta sync: alleen sets gewijzigd na een bepaalde datum."""
    session = SessionLocal()
    known = load_known_set_nums(session)
    print(f"  {len(known)} sets bekend in Rebrickable database")
    print(f"\nDelta sync (gewijzigd sinds {updated_since})...\n")

    page = 1
    total_synced = 0
    total_skipped = 0
    api_calls = 0

    while True:
        print(f"  [call {api_calls + 1}] pagina {page}...", end=" ", flush=True)
        try:
            data = fetch_page(page, updated_since)
        except Exception as e:
            print(f"FOUT: {e}")
            break

        api_calls += 1
        sets = data.get("sets") or []
        total_matches = data.get("matches", 0)

        if not sets:
            print("geen gewijzigde sets.")
            break

        synced, skipped = _process_page(session, sets, known)
        total_skipped += skipped
        total_synced += synced
        print(f"{synced} gesynchroniseerd (totaal gewijzigd: {total_matches})")

        if page * PAGE_SIZE >= total_matches:
            break
        page += 1
        time.sleep(RATE_LIMIT_DELAY)

    session.close()
    print(f"\n=== Delta sync voltooid ===")
    print(f"  API calls: {api_calls}")
    print(f"  Gesynchroniseerd: {total_synced}")
    print(f"  Niet in Rebrickable: {total_skipped}")


def sync_single(set_num: str) -> None:
    session = SessionLocal()
    known = load_known_set_nums(session)

    if set_num not in known:
        print(f"Set '{set_num}' niet gevonden in de database.")
        session.close()
        return

    print(f"Ophalen: {set_num}...")
    data = fetch_by_set_number(set_num)
    sets = data.get("sets") or []

    if not sets:
        print(f"Geen Brickset data gevonden voor {set_num}")
        session.close()
        return

    row = map_set(sets[0], set_num)
    upsert_rows(session, [row])
    session.close()

    print(f"  Naam:          {sets[0].get('name')}")
    print(f"  Prijs US:      ${row.get('price_us')}")
    print(f"  Prijs UK:      £{row.get('price_uk')}")
    print(f"  Prijs DE:      €{row.get('price_de')}")
    print(f"  Launch:        {row.get('launch_date')}")
    print(f"  Beschikbaar:   {row.get('availability')}")
    print(f"  Rating:        {row.get('rating')} ({row.get('review_count')} reviews)")
    print(f"  Owned by:      {row.get('owned_by')}")
    print(f"  Tags ({len(row.get('tags') or [])}): {', '.join((row.get('tags') or [])[:8])}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Synchroniseer Brickset data")
    parser.add_argument("--days", type=int, help="Delta sync: alleen sets gewijzigd in laatste N dagen")
    parser.add_argument("--set-num", type=str, help="Sync één set (bijv. 75192-1)")
    args = parser.parse_args()

    if not settings.brickset_api_key:
        print("Fout: BRICKSET_API_KEY niet ingesteld in .env")
        sys.exit(1)

    print("API key valideren...")
    result = _api_call("checkKey", {})
    if result.get("status") != "success":
        print(f"Ongeldige API key: {result}")
        sys.exit(1)
    print("  API key geldig ✓\n")

    if args.set_num:
        sync_single(args.set_num)
    elif args.days:
        since = (datetime.now(timezone.utc) - timedelta(days=args.days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        sync_delta(updated_since=since)
    else:
        sync_all()


if __name__ == "__main__":
    main()
