# Plant Data Bank Extractor Scripts

This package creates a local JSON plant knowledge bank for the Smart Urban Farming System.

Sources included:
- Food Plants International (FPI) web extractor
- Plants For A Future (PFAF) web extractor
- Perenual API enrichment
- GBIF taxonomy enrichment
- manual fact importer
- profile merger
- validator
- index builder
- Prolog exporter

The goal is:

```text
raw source data
    ↓
source-specific extracted JSON
    ↓
normalized plant profile
    ↓
merged centralized data bank
    ↓
optional Prolog export
```

## Install

```bash
pip install -r requirements.txt
```

## Configure

Create `.env` if you want Perenual enrichment:

```env
PERENUAL_API_KEY=your_key_here
```

## Edit plant seed list

Edit:

```text
config/plants_seed.json
```

## Run source extraction

```bash
python3 scripts/extract_fpi.py --plants config/plants_seed.json
python3 scripts/extract_pfaf.py --plants config/plants_seed.json
python3 scripts/enrich_gbif.py --plants config/plants_seed.json
```

Perenual is optional because of cooldown/API quota:

```bash
python3 scripts/enrich_perenual.py --plants config/plants_seed.json --delay 6
```

## Merge profiles

```bash
python3 scripts/merge_profiles.py --plants config/plants_seed.json
python3 scripts/build_indexes.py
python3 scripts/validate_data_bank.py
python3 scripts/export_to_prolog.py
```

## Or run all except Perenual

```bash
python3 scripts/run_pipeline.py --plants config/plants_seed.json
```

With Perenual:

```bash
python3 scripts/run_pipeline.py --plants config/plants_seed.json --include-perenual
```

## Output

```text
data_bank/
  raw_sources/
    food_plants_international/
    pfaf/
    perenual/
    gbif/
    manual/
  normalized/plants/
  indexes/
  exports/prolog/
```

Important: FPI and PFAF are not clean APIs. These scripts are conservative extractors. Always review raw and normalized JSON before using the facts for decision support.
