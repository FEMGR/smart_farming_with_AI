from __future__ import annotations
import argparse
from common import NORMALIZED_DIR, RAW_DIR, canonical_profile_template, ensure_dirs, load_plants, plant_filename, read_json, utc_now, write_json


def setf(p, path, value, source, overwrite=False):
    if value in (None, "", [], {}):
        return
    cur = p
    parts = path.split(".")
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    if overwrite or cur.get(parts[-1]) in (None, "", [], {}):
        cur[parts[-1]] = value
        p.setdefault("field_sources", {})[path] = source


def extendl(p, path, values, source):
    values = values or []
    if not values:
        return
    cur = p
    parts = path.split(".")
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    old = cur.get(parts[-1]) or []
    out = []
    for v in old + values:
        if v not in out:
            out.append(v)
    cur[parts[-1]] = out
    p.setdefault("field_sources", {})[path] = source


def meta(p, raw, source):
    for s in raw.get("snapshots") or []:
        p["source_metadata"]["sources"].append(
            {
                "source_name": source,
                "source_url": s.get("source_url"),
                "status": s.get("status"),
                "fields_provided": list(((s.get("parsed") or {}).get("guessed_fields") or {}).keys()),
                "confidence": 0.65,
                "last_verified_at": s.get("fetched_at"),
            }
        )


def merge_gbif(p, raw):
    for s in raw.get("snapshots") or []:
        payload = (s.get("parsed") or {}).get("payload") or {}
        if payload and payload.get("matchType") != "NONE":
            setf(p, "identity.scientific_name", payload.get("scientificName"), "GBIF")
            setf(p, "identity.genus", payload.get("genus"), "GBIF")
            setf(p, "identity.family", payload.get("family"), "GBIF")


def aslist(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def merge_perenual(p, raw):
    details = []
    for s in raw.get("snapshots") or []:
        parsed = s.get("parsed") or {}
        if parsed.get("endpoint") == "species-details":
            details += parsed.get("payload") or []
    for d in details:
        if not isinstance(d, dict):
            continue
        setf(p, "identity.common_name", d.get("common_name"), "Perenual")
        sci = d.get("scientific_name")
        setf(p, "identity.scientific_name", sci[0] if isinstance(sci, list) and sci else sci, "Perenual")
        setf(p, "classification.life_cycle", d.get("cycle"), "Perenual")
        extendl(p, "growth.sunlight", aslist(d.get("sunlight")), "Perenual")
        setf(p, "growth.water_need", d.get("watering"), "Perenual")
        setf(p, "care.watering_notes", d.get("watering_general_benchmark"), "Perenual")
        extendl(p, "germination.propagation_methods", aslist(d.get("propagation")), "Perenual")
        setf(p, "growth.growth_speed", d.get("growth_rate"), "Perenual")


def merge_text(p, raw, source):
    for s in raw.get("snapshots") or []:
        g = (s.get("parsed") or {}).get("guessed_fields") or {}
        setf(p, "classification.life_cycle", g.get("life_cycle"), source)
        extendl(p, "classification.edible_parts", g.get("edible_parts") or [], source)
        extendl(p, "classification.use_categories", g.get("use_categories") or [], source)
        extendl(p, "germination.propagation_methods", g.get("propagation_methods") or [], source)
        setf(p, "germination.propagation_notes", g.get("propagation_notes"), source)
        setf(p, "care.cultivation_notes", g.get("cultivation_notes"), source)
        setf(p, "care.nutrition_notes", g.get("nutrition_notes"), source)
        setf(p, "pests_and_diseases.disease_notes", g.get("pest_disease_notes"), source)
        setf(p, "care.cautions", g.get("cautions") or g.get("known_hazards"), source)
    if p["classification"]["edible_parts"]:
        setf(p, "classification.edible", True, source)


def missing(p):
    req = [
        "identity.scientific_name",
        "identity.genus",
        "identity.family",
        "classification.edible_parts",
        "classification.life_cycle",
        "growth.sunlight",
        "growth.water_need",
        "growth.soil_notes",
        "germination.propagation_methods",
        "germination.germination_days_min",
        "germination.sowing_depth_cm",
        "pests_and_diseases.known_diseases",
    ]
    miss = []
    for path in req:
        cur = p
        ok = True
        for part in path.split("."):
            if not isinstance(cur, dict) or part not in cur:
                ok = False
                break
            cur = cur[part]
        if not ok or cur in (None, "", [], {}):
            miss.append(path)
    p["missing_fields"] = miss


def one(plant):
    p = canonical_profile_template(plant)
    if plant.get("scientific_name"):
        setf(p, "identity.scientific_name", plant["scientific_name"], "local_seed", True)
    if plant.get("common_name"):
        setf(p, "identity.common_name", plant["common_name"], "local_seed", True)
    for folder, source, fn in [
        ("gbif", "GBIF", merge_gbif),
        ("perenual", "Perenual", merge_perenual),
        ("food_plants_international", "Food Plants International", lambda p, r: merge_text(p, r, "Food Plants International")),
        ("pfaf", "Plants For A Future", lambda p, r: merge_text(p, r, "Plants For A Future")),
    ]:
        raw = read_json(RAW_DIR / folder / plant_filename(plant), None)
        if raw:
            fn(p, raw)
            meta(p, raw, source)
    p["source_metadata"]["last_merged_at"] = utc_now()
    missing(p)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plants", required=True)
    args = ap.parse_args()
    ensure_dirs()
    for plant in load_plants(args.plants):
        out = NORMALIZED_DIR / plant_filename(plant)
        write_json(out, one(plant))
        print("[MERGE] wrote", out)


if __name__ == "__main__":
    main()
