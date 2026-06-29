from __future__ import annotations
import argparse
from copy import deepcopy
from common import NORMALIZED_DIR, ensure_dirs, plant_filename, read_json, utc_now, write_json


def deep_merge(base, incoming):
    result = deepcopy(base)
    for k, v in incoming.items():
        if k in ["source", "plant_atom"]:
            continue
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = deep_merge(result[k], v)
        elif v not in (None, "", [], {}):
            result[k] = v
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    args = ap.parse_args()
    ensure_dirs()
    incoming = read_json(args.file, {})
    if not incoming.get("plant_atom"):
        raise ValueError("Manual source file must include plant_atom")
    out = NORMALIZED_DIR / plant_filename(incoming)
    existing = read_json(out, {"plant_atom": incoming["plant_atom"]})
    merged = deep_merge(existing, incoming)
    source = incoming.get("source") or {}
    merged.setdefault("source_metadata", {}).setdefault("sources", []).append(
        {
            "source_name": source.get("source_name", "manual"),
            "source_url": source.get("source_url"),
            "status": "manual_import",
            "fields_provided": list(incoming.keys()),
            "confidence": source.get("confidence", 0.8),
            "last_verified_at": utc_now(),
        }
    )
    write_json(out, merged)
    print("[MANUAL] updated", out)


if __name__ == "__main__":
    main()
