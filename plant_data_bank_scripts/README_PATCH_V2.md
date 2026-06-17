# Plant Data Bank Patch v2

This patch fixes the main problems visible in the Basil output:

1. FPI search pages were being treated as plant detail pages.
2. PFAF page-wide text was being used to guess too many edible parts and categories.
3. Wildlife text such as "Food (Fruit, Seeds, Leaf litter...)" polluted human edible parts.
4. Search result pages were merged with the same confidence as exact plant pages.
5. `life_cycle` from PFAF can be misleading for cultivated annual herbs, so the script now stores it only when strongly detected.
6. Long extracted text is now stored as notes only when it comes from a relevant section.

How to apply:

Copy these files into your existing `plant_data_bank_scripts/scripts/` folder:

- extract_pfaf_v2.py
- extract_fpi_v2.py
- merge_profiles_v2.py

Then run:

```bash
python3 scripts/extract_pfaf_v2.py --plants config/plants_seed.json
python3 scripts/extract_fpi_v2.py --plants config/plants_seed.json
python3 scripts/merge_profiles_v2.py --plants config/plants_seed.json
```

Recommended:
Keep the old scripts as backup until you compare outputs.

Expected improvement for basil:

```json
"classification": {
  "edible": true,
  "use_categories": ["culinary_herb", "medicinal_plant"],
  "edible_parts": ["leaf", "flower", "seed"],
  "life_cycle": null
}
```

The exact result depends on the source text, but it should no longer produce:
- root
- pod
- fruit_crop
- root_tuber_crop
- grain_seed_crop
unless those are explicitly found in a relevant edible-use section.
