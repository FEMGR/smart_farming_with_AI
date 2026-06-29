# scripts/pdf_to_prolog.py

import re
import fitz  # PyMuPDF
from collections import defaultdict

# =========================
# CONFIG
# =========================
PDF_PATH = "/home/graubo/Documents/Plant/companion-planting.pdf"  # <--- IMPORTANT: Verify this path
OUTPUT_FILE = "../CompanionPlanting_Prolog/data/pest_fact.pl"  # Adjust if CompanionPlanting_Prolog is not a sibling of 'scripts'


# =========================
# NORMALIZATION
# =========================
def normalize(name):
    name = str(name).lower()
    name = re.sub(r"[^a-z0-9 ]", "", name)
    return name.replace(" ", "_").strip()


def is_valid_plant(name):
    """
    Checks if a normalized plant name is a valid entity and not noise.
    """
    noise_words = {"most", "some", "many", "all", "none", "unknown", "etc", "others", "everything"}
    if not name or len(name) < 2:
        return False
    if name in noise_words:
        return False
    return True


def split_items(text):
    # Split by comma, 'and', or newline, then normalize
    return [normalize(x) for x in re.split(r",|\band\b|\n", text) if x.strip()]


# =========================
# STEP 1: EXTRACT TEXT
# =========================
def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = []

    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks")

        # Group blocks by their y-coordinate (visual line)
        lines = defaultdict(list)
        for b in blocks:
            x0, y0, x1, y1, text, block_no, block_type = b
            # Use y0 as the key for the line, allowing for slight variations
            # Rounding to nearest integer or a small epsilon can help group close lines
            lines[round(y0)].append((x0, text.strip()))

        # Sort lines by y-coordinate
        sorted_y_coords = sorted(lines.keys())

        page_lines = []
        for y_coord in sorted_y_coords:
            # Sort blocks within each line by x-coordinate
            sorted_blocks_on_line = sorted(lines[y_coord], key=lambda item: item[0])

            # Join text blocks on the same line, adding spaces
            current_line_text = ""
            last_x_end = 0
            for x0, text_content in sorted_blocks_on_line:
                # Add spacing based on x-coordinate difference
                # This is a heuristic and might need tuning
                if x0 > last_x_end + 50:  # If there's a significant gap, add more space
                    current_line_text += "    "  # Simulate a tab or column break
                elif x0 > last_x_end + 5:  # Small gap, just a space
                    current_line_text += " "

                current_line_text += text_content
                last_x_end = x0 + len(text_content) * 6  # Estimate x_end based on text length (avg char width)

            if current_line_text.strip():
                page_lines.append(current_line_text.strip())

        full_text.extend(page_lines)
        full_text.append(f"---PAGE BREAK {page_num + 1}---")  # Add a clear separator

    return "\n".join(full_text)


# =========================
# STEP 2: CLEAN TEXT
# =========================
def clean_text(text):
    # Replace multiple newlines with a single newline
    text = re.sub(r"\n\s*\n+", "\n", text)
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split("\n")]
    # Remove empty lines
    lines = [line for line in lines if line]
    return "\n".join(lines).strip()


def extract_table_section(text):
    # The table starts with "Table 1. COMPANION PLANTING CHART"
    # and the first crop is Amaranth.
    # We need to be more robust in finding the start of the actual data.

    # Look for the header line or the first crop
    start_match = re.search(r"(CROP:COMPANIONS:INCOMPATIBLE:|Amaranth|Artichokes|Asparagus|Basil|Beans)", text, re.IGNORECASE)

    if not start_match:
        raise ValueError("❌ Could not locate the start of the table data (header or first crop).")

    start_idx = start_match.start()

    # Try to stop before notes/sources or another table/section
    end_match = re.search(
        r"---PAGE BREAK|\bSources\b|\bNotes\b|\bScientific Foundations\b",
        text[start_idx:],  # Search from the start of the table section
        re.IGNORECASE,
    )

    end_idx = start_idx + end_match.start() if end_match else len(text)

    table_text = text[start_idx:end_idx]

    print("\n📊 TABLE TEXT SAMPLE:\n")
    print(table_text[:1000])  # debug preview

    return table_text


# =========================
# STEP 3: PARSE ENTRIES
# =========================
def parse_entries(text):
    entries = []

    # Known crops from your dataset (expand later if needed)
    KNOWN_PLANTS = [
        "Amaranth",
        "Artichokes",
        "Asparagus",
        "Basil",
        "Beans",
        "Beans, Bush",
        "Beans, Pole",
        "Beets",
        "Blackberries",
        "Blueberries",
        "Borage",
        "Cabbage",
        "Carrots",
        "Celery",
        "Corn",
        "Cucumber",
        "Eggplant",
        "Ginger",
        "Gourds",
        "Grapes",
        "Lettuce",
        "Melons",
        "Onion",
        "Okra",
        "Parsley",
        "Pea",
        "Pea, English",
        "Peanut",
        "Peppers",
        "Potato",
        "Pumpkins",
        "Radish",
        "Spinach",
        "Squash",
        "Strawberries",
        "Sunflowers",
        "Sweet Potato",
        "Tomato",
        "Turnip",
        "Watermelon",
    ]

    # Create a regex pattern to find known plants at the beginning of a line
    # Use word boundaries to avoid partial matches
    plant_pattern = r"^(?:" + "|".join(re.escape(p) for p in KNOWN_PLANTS) + r")\b"

    lines = text.split("\n")
    current_entry = None

    for line in lines:
        line = line.strip()
        if not line or line.startswith("---PAGE BREAK"):
            continue

        # Check for the header line and skip it
        if "CROP:COMPANIONS:INCOMPATIBLE:" in line.upper():
            continue

        plant_match = re.match(plant_pattern, line, re.IGNORECASE)

        if plant_match:
            # If we were processing a previous entry, save it
            if current_entry:
                entries.append(current_entry)

            plant_name = plant_match.group(0).strip()
            remaining_line = line[plant_match.end() :].strip()

            # Attempt to split the remaining line into companions and incompatible
            # Assuming a structure like "PLANT    COMPANIONS_TEXT    INCOMPATIBLE_TEXT"
            # We need to be flexible with spacing
            parts = re.split(r"\s{2,}", remaining_line, maxsplit=1)  # Split by 2 or more spaces

            companions_text = parts[0].strip() if len(parts) > 0 else ""
            incompatible_text = parts[1].strip() if len(parts) > 1 else ""

            current_entry = {
                "plant": plant_name,
                "companions": split_items(companions_text),
                "incompatible": split_items(incompatible_text),
            }
        elif current_entry:
            # If no new plant, this line might be a continuation of the previous entry's lists
            # This is a common pattern in PDF tables where long lists wrap
            # We'll append to the last known list (companions or incompatible)
            # This is a heuristic and might need refinement based on actual PDF output

            # Check if the line seems to be a continuation of companions
            if not current_entry["incompatible"] and current_entry["companions"]:
                current_entry["companions"].extend(split_items(line))
            # Check if the line seems to be a continuation of incompatible
            elif current_entry["incompatible"]:
                current_entry["incompatible"].extend(split_items(line))
            # If neither, it's an unclassified continuation, add to companions by default
            else:
                current_entry["companions"].extend(split_items(line))

    # Add the last entry after the loop
    if current_entry:
        entries.append(current_entry)

    return entries


# =========================
# STEP 4: EXPORT PROLOG
# =========================
def export_prolog(entries):
    with open(OUTPUT_FILE, "w") as f:
        for entry in entries:
            plant = normalize(entry["plant"])

            if not plant:
                continue

            for c in entry["companions"]:
                if c and is_valid_plant(c):  # Add validation for companion plants
                    f.write(f"companion({plant}, {c}).\n")

            for i in entry["incompatible"]:
                if i and is_valid_plant(i):  # Add validation for incompatible plants
                    f.write(f"antagonist({plant}, {i}).\n")

    print(f"✅ Prolog file saved to: {OUTPUT_FILE}")


# =========================
# MAIN
# =========================
def main():
    print("📄 Extracting text from PDF...")
    raw_text = extract_text(PDF_PATH)
    print("\n🔍 RAW TEXT SAMPLE (first 1000 chars):\n", raw_text[:1000])

    print("🧹 Cleaning text...")
    clean = clean_text(raw_text)
    print("\n🔍 CLEANED TEXT SAMPLE (first 1000 chars):\n", clean[:1000])

    table_text = extract_table_section(clean)
    print("\n📊 EXTRACTED TABLE SECTION (first 1000 chars):\n", table_text[:1000])

    print("🧠 Parsing entries...")
    entries = parse_entries(table_text)

    print(f"✅ Parsed {len(entries)} entries")

    print("\n🔍 Sample output:")
    for e in entries[:5]:
        print(e)

    print("\n💾 Exporting Prolog...")
    export_prolog(entries)


if __name__ == "__main__":
    main()
