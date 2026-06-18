from common import ensure_dirs, read_json, slugify, write_json
from project_paths import PATHS


def main():
    PATHS.ensure_dirs()
    ensure_dirs()
    name_idx = {}
    sci_idx = {}
    genus_idx = {}
    edible_idx = {}
    for path in sorted(PATHS.normalized_plants.glob("*.json")):
        p = read_json(path, {})
        atom = p.get("plant_atom")
        ident = p.get("identity") or {}
        cls = p.get("classification") or {}
        for n in [ident.get("common_name"), ident.get("scientific_name"), *(ident.get("common_names") or []), *(ident.get("synonyms") or [])]:
            if n:
                name_idx[slugify(n)] = atom
        if ident.get("scientific_name"):
            sci_idx[slugify(ident["scientific_name"])] = atom
        if ident.get("genus"):
            genus_idx.setdefault(slugify(ident["genus"]), []).append(atom)
        if cls.get("edible") is True or cls.get("edible_parts"):
            edible_idx[atom] = {"edible_parts": cls.get("edible_parts") or [], "use_categories": cls.get("use_categories") or []}
    write_json(PATHS.data_bank_indexes / "plant_name_index.json", name_idx)
    write_json(PATHS.data_bank_indexes / "scientific_name_index.json", sci_idx)
    write_json(PATHS.data_bank_indexes / "genus_index.json", genus_idx)
    write_json(PATHS.data_bank_indexes / "edible_crop_index.json", edible_idx)
    print("[INDEX] wrote", PATHS.data_bank_indexes)


if __name__ == "__main__":
    main()
