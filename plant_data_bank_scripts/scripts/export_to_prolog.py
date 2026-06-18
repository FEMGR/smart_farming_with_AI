import re
from common import ensure_dirs, read_json
from project_paths import PATHS


def atom(v):
    v = str(v or "").strip().lower()
    v = re.sub(r"[^a-z0-9]+", "_", v)
    v = re.sub(r"_+", "_", v)
    return v.strip("_") or "unknown"


def ps(v):
    return "'" + str(v or "").replace("\\", "\\\\").replace("'", "\\'") + "'"


def fact(name, *args):
    return f"{name}({', '.join(args)})."


def facts(p):
    out = []
    pl = atom(p.get("plant_atom"))
    ident = p.get("identity") or {}
    cls = p.get("classification") or {}
    growth = p.get("growth") or {}
    germ = p.get("germination") or {}
    out.append(fact("plant", pl))
    if ident.get("scientific_name"):
        out.append(fact("scientific_name", pl, ps(ident["scientific_name"])))
    if ident.get("genus"):
        out.append(fact("genus", pl, atom(ident["genus"])))
    if ident.get("family"):
        out.append(fact("plant_family", pl, atom(ident["family"])))
    if cls.get("edible") is True:
        out.append(fact("edible", pl))
    for part in cls.get("edible_parts") or []:
        out.append(fact("edible_part", pl, atom(part)))
    for cat in cls.get("use_categories") or []:
        out.append(fact("use_category", pl, atom(cat)))
    if cls.get("life_cycle"):
        out.append(fact("life_cycle", pl, atom(cls["life_cycle"])))
    for sun in growth.get("sunlight") or []:
        out.append(fact("sunlight_need", pl, atom(sun)))
    if growth.get("water_need"):
        out.append(fact("water_need", pl, atom(growth["water_need"])))
    for m in germ.get("propagation_methods") or []:
        out.append(fact("propagation_method", pl, atom(m)))
    if germ.get("germination_days_min") is not None and germ.get("germination_days_max") is not None:
        out.append(fact("germination_days", pl, str(germ["germination_days_min"]), str(germ["germination_days_max"])))
    return out


def main():
    PATHS.ensure_dirs()
    ensure_dirs()
    lines = ["% Auto-generated from centralized JSON plant data bank.", "% Do not edit manually.", ""]
    for path in sorted(PATHS.normalized_plants.glob("*.json")):
        lines.append("% Source profile: " + path.name)
        lines.extend(facts(read_json(path, {})))
        lines.append("")
    out = PATHS.generated_prolog_export
    out.write_text("\n".join(lines), encoding="utf-8")
    print("[PROLOG] wrote", out)


if __name__ == "__main__":
    main()
