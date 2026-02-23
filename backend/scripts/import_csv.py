"""
Eenmalige import van alle Rebrickable CSV dumps naar PostgreSQL.

Gebruik:
    uv run python scripts/import_csv.py

De CSV bestanden worden automatisch gedownload als ze nog niet aanwezig zijn.
"""

import csv
import gzip
import io
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

from app.core.database import SessionLocal, engine
from app.core.database import Base
import app.models  # noqa: F401

DATA_DIR = Path(__file__).parent / "data"
REBRICKABLE_BASE = "https://cdn.rebrickable.com/media/downloads"

CSV_FILES = {
    "colors": f"{REBRICKABLE_BASE}/colors.csv.gz",
    "themes": f"{REBRICKABLE_BASE}/themes.csv.gz",
    "part_categories": f"{REBRICKABLE_BASE}/part_categories.csv.gz",
    "parts": f"{REBRICKABLE_BASE}/parts.csv.gz",
    "part_relationships": f"{REBRICKABLE_BASE}/part_relationships.csv.gz",
    "elements": f"{REBRICKABLE_BASE}/elements.csv.gz",
    "sets": f"{REBRICKABLE_BASE}/sets.csv.gz",
    "minifigs": f"{REBRICKABLE_BASE}/minifigs.csv.gz",
    "inventories": f"{REBRICKABLE_BASE}/inventories.csv.gz",
    "inventory_parts": f"{REBRICKABLE_BASE}/inventory_parts.csv.gz",
    "inventory_minifigs": f"{REBRICKABLE_BASE}/inventory_minifigs.csv.gz",
    "inventory_sets": f"{REBRICKABLE_BASE}/inventory_sets.csv.gz",
}

BATCH_SIZE = 5000


def download_csv(name: str, url: str) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    dest = DATA_DIR / f"{name}.csv.gz"
    if dest.exists():
        print(f"  [skip] {name}.csv.gz already downloaded")
        return dest
    print(f"  [download] {name}.csv.gz ...")
    urllib.request.urlretrieve(url, dest)
    return dest


def read_csv(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_bool(value: str) -> bool:
    return value.strip().lower() in ("t", "true", "1", "yes")


def parse_int_or_none(value: str) -> int | None:
    value = value.strip()
    if value == "" or value.lower() == "none":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def parse_str_or_none(value: str) -> str | None:
    value = value.strip()
    return value if value else None


def batch_upsert(conn, table_name: str, rows: list[dict], conflict_cols: list[str]) -> None:
    if not rows:
        return
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        stmt = insert(Base.metadata.tables[table_name]).values(batch)
        stmt = stmt.on_conflict_do_nothing(index_elements=conflict_cols)
        conn.execute(stmt)
    conn.commit()


def import_colors(conn) -> None:
    print("Importing colors...")
    path = download_csv("colors", CSV_FILES["colors"])
    rows = read_csv(path)
    data = [
        {
            "id": int(r["id"]),
            "name": r["name"],
            "rgb": r["rgb"],
            "is_trans": parse_bool(r["is_trans"]),
        }
        for r in rows
    ]
    batch_upsert(conn, "colors", data, ["id"])
    print(f"  {len(data)} colors imported")


def import_themes(conn) -> None:
    print("Importing themes...")
    path = download_csv("themes", CSV_FILES["themes"])
    rows = read_csv(path)
    # First pass: themes without parent (to satisfy FK constraint)
    no_parent = [r for r in rows if not r["parent_id"].strip()]
    with_parent = [r for r in rows if r["parent_id"].strip()]

    data_no_parent = [{"id": int(r["id"]), "name": r["name"], "parent_id": None} for r in no_parent]
    data_with_parent = [
        {"id": int(r["id"]), "name": r["name"], "parent_id": int(r["parent_id"])} for r in with_parent
    ]
    batch_upsert(conn, "themes", data_no_parent, ["id"])
    batch_upsert(conn, "themes", data_with_parent, ["id"])
    print(f"  {len(rows)} themes imported")


def import_part_categories(conn) -> None:
    print("Importing part categories...")
    path = download_csv("part_categories", CSV_FILES["part_categories"])
    rows = read_csv(path)
    data = [{"id": int(r["id"]), "name": r["name"]} for r in rows]
    batch_upsert(conn, "part_categories", data, ["id"])
    print(f"  {len(data)} part categories imported")


def import_parts(conn) -> None:
    print("Importing parts...")
    path = download_csv("parts", CSV_FILES["parts"])
    rows = read_csv(path)
    data = [
        {
            "part_num": r["part_num"],
            "name": r["name"],
            "part_cat_id": int(r["part_cat_id"]),
            "part_material": parse_str_or_none(r.get("part_material", "")),
        }
        for r in rows
    ]
    batch_upsert(conn, "parts", data, ["part_num"])
    print(f"  {len(data)} parts imported")


def import_part_relationships(conn) -> None:
    print("Importing part relationships...")
    path = download_csv("part_relationships", CSV_FILES["part_relationships"])
    rows = read_csv(path)
    data = [
        {
            "rel_type": r["rel_type"],
            "child_part_num": r["child_part_num"],
            "parent_part_num": r["parent_part_num"],
        }
        for r in rows
    ]
    # Part relationships have no unique key from CSV, skip duplicates via truncate+insert
    conn.execute(text("TRUNCATE TABLE part_relationships RESTART IDENTITY"))
    conn.commit()
    for i in range(0, len(data), BATCH_SIZE):
        batch = data[i : i + BATCH_SIZE]
        conn.execute(Base.metadata.tables["part_relationships"].insert(), batch)
    conn.commit()
    print(f"  {len(data)} part relationships imported")


def import_elements(conn) -> None:
    print("Importing elements...")
    path = download_csv("elements", CSV_FILES["elements"])
    rows = read_csv(path)
    data = [
        {
            "element_id": r["element_id"],
            "part_num": r["part_num"],
            "color_id": int(r["color_id"]),
            "design_id": parse_str_or_none(r.get("design_id", "")),
        }
        for r in rows
        if r["part_num"] and r["color_id"]
    ]
    batch_upsert(conn, "elements", data, ["element_id"])
    print(f"  {len(data)} elements imported")


def import_sets(conn) -> None:
    print("Importing sets...")
    path = download_csv("sets", CSV_FILES["sets"])
    rows = read_csv(path)
    data = [
        {
            "set_num": r["set_num"],
            "name": r["name"],
            "year": int(r["year"]),
            "theme_id": int(r["theme_id"]),
            "num_parts": int(r["num_parts"]),
            "img_url": parse_str_or_none(r.get("img_url", "")),
        }
        for r in rows
    ]
    batch_upsert(conn, "sets", data, ["set_num"])
    print(f"  {len(data)} sets imported")


def import_minifigs(conn) -> None:
    print("Importing minifigs...")
    path = download_csv("minifigs", CSV_FILES["minifigs"])
    rows = read_csv(path)
    data = [
        {
            "fig_num": r["fig_num"],
            "name": r["name"],
            "num_parts": int(r["num_parts"]),
            "img_url": parse_str_or_none(r.get("img_url", "")),
        }
        for r in rows
    ]
    batch_upsert(conn, "minifigs", data, ["fig_num"])
    print(f"  {len(data)} minifigs imported")


def import_inventories(conn) -> None:
    print("Importing inventories...")
    path = download_csv("inventories", CSV_FILES["inventories"])
    rows = read_csv(path)
    data = [
        {
            "id": int(r["id"]),
            "version": int(r["version"]),
            "set_num": r["set_num"],
        }
        for r in rows
    ]
    batch_upsert(conn, "inventories", data, ["id"])
    print(f"  {len(data)} inventories imported")


def import_inventory_parts(conn) -> None:
    print("Importing inventory parts (this may take a while)...")
    path = download_csv("inventory_parts", CSV_FILES["inventory_parts"])
    rows = read_csv(path)
    conn.execute(text("TRUNCATE TABLE inventory_parts RESTART IDENTITY"))
    conn.commit()
    data = [
        {
            "inventory_id": int(r["inventory_id"]),
            "part_num": r["part_num"],
            "color_id": int(r["color_id"]),
            "quantity": int(r["quantity"]),
            "is_spare": parse_bool(r["is_spare"]),
            "img_url": parse_str_or_none(r.get("img_url", "")),
        }
        for r in rows
    ]
    for i in range(0, len(data), BATCH_SIZE):
        batch = data[i : i + BATCH_SIZE]
        conn.execute(Base.metadata.tables["inventory_parts"].insert(), batch)
        if i % 50000 == 0 and i > 0:
            print(f"  ... {i}/{len(data)}")
    conn.commit()
    print(f"  {len(data)} inventory parts imported")


def import_inventory_minifigs(conn) -> None:
    print("Importing inventory minifigs...")
    path = download_csv("inventory_minifigs", CSV_FILES["inventory_minifigs"])
    rows = read_csv(path)
    conn.execute(text("TRUNCATE TABLE inventory_minifigs RESTART IDENTITY"))
    conn.commit()
    data = [
        {
            "inventory_id": int(r["inventory_id"]),
            "fig_num": r["fig_num"],
            "quantity": int(r["quantity"]),
        }
        for r in rows
    ]
    for i in range(0, len(data), BATCH_SIZE):
        conn.execute(Base.metadata.tables["inventory_minifigs"].insert(), data[i : i + BATCH_SIZE])
    conn.commit()
    print(f"  {len(data)} inventory minifigs imported")


def import_inventory_sets(conn) -> None:
    print("Importing inventory sets...")
    path = download_csv("inventory_sets", CSV_FILES["inventory_sets"])
    rows = read_csv(path)
    conn.execute(text("TRUNCATE TABLE inventory_sets RESTART IDENTITY"))
    conn.commit()
    data = [
        {
            "inventory_id": int(r["inventory_id"]),
            "set_num": r["set_num"],
            "quantity": int(r["quantity"]),
        }
        for r in rows
    ]
    for i in range(0, len(data), BATCH_SIZE):
        conn.execute(Base.metadata.tables["inventory_sets"].insert(), data[i : i + BATCH_SIZE])
    conn.commit()
    print(f"  {len(data)} inventory sets imported")


def main() -> None:
    print("=== BrickViewer CSV Import ===\n")
    print("Creating tables if not exists...")
    Base.metadata.create_all(engine)

    with engine.begin() as conn:
        # Order matters — respect FK dependencies
        import_colors(conn)
        import_themes(conn)
        import_part_categories(conn)
        import_parts(conn)
        import_part_relationships(conn)
        import_elements(conn)
        import_sets(conn)
        import_minifigs(conn)
        import_inventories(conn)
        import_inventory_parts(conn)
        import_inventory_minifigs(conn)
        import_inventory_sets(conn)

    print("\n=== Import complete! ===")


if __name__ == "__main__":
    main()
