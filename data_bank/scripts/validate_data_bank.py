from common import ensure_dirs, read_json
from project_paths import PATHS


def main():
    PATHS.ensure_dirs()
    ensure_dirs()
    files = sorted(PATHS.normalized_plants.glob("*.json"))
    if not files:
        print("No normalized plant profiles found.")
        return
    total = 0
    for path in files:
        p = read_json(path, {})
        errs = []
        if not p.get("plant_atom"):
            errs.append("missing plant_atom")
        if not (p.get("identity") or {}).get("scientific_name"):
            errs.append("missing identity.scientific_name")
        if not (p.get("identity") or {}).get("common_name"):
            errs.append("missing identity.common_name")
        if "source_metadata" not in p:
            errs.append("missing source_metadata")
        if errs:
            total += len(errs)
            print("[INVALID]", path.name, errs)
        else:
            print("[OK]", path.name)
    print(f"Validated {len(files)} files. Errors: {total}")


if __name__ == "__main__":
    main()
