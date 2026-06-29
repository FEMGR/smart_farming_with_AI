# Plant Seed Builder

This package creates `plants_seed.json` from multiple edible/crop plant source lists.

Supported input formats:

- CSV
- JSON list
- JSON object with list fields
- raw text lines

Recommended sources:

- PFAF exports or manually prepared CSV
- Food Plants International / FPI exports or manually prepared CSV
- EdiblePlantDB exports or manually prepared CSV
- USDA GRIN exports or manually prepared CSV

The output file is meant to feed your plant data bank pipeline:

```text
source lists
    ↓
normalize names
    ↓
deduplicate by scientific name / genus / common name
    ↓
classify crop/herb/edible categories
    ↓
config/plants_seed.json
```

## Install

```bash
pip install rapidfuzz
```

## Input folder

Put source files here:

```text
input_sources/
  pfaf.csv
  fpi.csv
  edibleplantdb.csv
  usda_grin.csv
```

The script accepts flexible column names.

Useful columns:

```text
scientific_name
latin_name
botanical_name
common_name
name
family
genus
synonyms
edible_parts
uses
category
life_cycle
source_url
```

## Run

```bash
python3 scripts/build_plants_seed.py \
  --input-dir input_sources \
  --output config/plants_seed.json
```

## Output format

```json
[
  {
    "plant_atom": "sage",
    "common_name": "Sage",
    "scientific_name": "Salvia officinalis",
    "genus": "Salvia",
    "family": "Lamiaceae",
    "synonyms": [],
    "source_names": ["pfaf", "fpi"],
    "use_categories": ["culinary_herb"],
    "edible_parts": ["leaf"],
    "confidence": 0.9,
    "duplicate_group_id": "salvia_officinalis"
  }
]
```

## Why this exists

You do not want to manually write thousands of crops/herbs into `plants_seed.json`.

This script gives you a clean starting list and prevents duplicate plants such as:

```text
Tomato
tomatoes
Solanum lycopersicum
Lycopersicon esculentum
```

from becoming separate records.
