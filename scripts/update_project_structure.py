"""
Script for automatically detecting the structure of
the whole project and updating the README.md file 
"""

# script/update_project_structure.py
import re
from pathlib import Path

# Set root to the parent of the folder containing this script
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Maximum folder depth to display (1 = root only, 2 = root + subdirectories, etc.)
MAX_DEPTH = 3

# Toggle this: Set to True to display ONLY directories, False for both files and directories
DIRECTORIES_ONLY = True

# Exact folder and file names to ignore
IGNORE_NAMES = {
    ".git",
    ".github",
    ".agents",
    ".codex",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    "node_modules",
    ".idea",
    ".vscode",
    ".DS_Store",
}


def generate_tree(dir_path: Path, prefix: str = "", current_depth: int = 1) -> list[str]:
    """Recursively generates ASCII tree structure lines up to MAX_DEPTH."""
    lines = []

    # Stop traversing if we exceed MAX_DEPTH
    if current_depth > MAX_DEPTH:
        return lines

    try:
        # Filter entries based on ignore list and DIRECTORIES_ONLY setting
        entries = [e for e in dir_path.iterdir() if e.name not in IGNORE_NAMES and (not DIRECTORIES_ONLY or e.is_dir())]
        # Sort directories first, then files alphabetically
        entries = sorted(entries, key=lambda e: (not e.is_dir(), e.name.lower()))
    except PermissionError:
        return []

    count = len(entries)
    for index, entry in enumerate(entries):
        is_last = index == count - 1
        connector = "└── " if is_last else "├── "

        if entry.is_dir():
            lines.append(f"{prefix}{connector}{entry.name}/")
            new_prefix = prefix + ("    " if is_last else "│   ")
            # Recurse with current_depth + 1
            lines.extend(generate_tree(entry, new_prefix, current_depth + 1))
        else:
            lines.append(f"{prefix}{connector}{entry.name}")

    return lines


def update_readme():
    readme_path = PROJECT_ROOT / "README.md"
    project_name = PROJECT_ROOT.name

    # 1. Build the tree text block starting at depth level 1
    tree_lines = [f"{project_name}/"] + generate_tree(PROJECT_ROOT, current_depth=1)
    tree_block = "\n".join(tree_lines)
    new_structure_section = f"## Project Structure\n\n```text\n{tree_block}\n```"

    # 2. Display preview in terminal
    print(f"PROJECT_ROOT: {PROJECT_ROOT.resolve()}")
    print(f"MAX DEPTH: {MAX_DEPTH}")
    print("=" * 50)
    print(" GENERATED PROJECT STRUCTURE PREVIEW")
    print("=" * 50)
    print(tree_block)
    print("=" * 50 + "\n")

    # 3. Prompt user for confirmation
    confirm = input("Would you like to update README.md with this structure? (y/N): ").strip().lower()

    if confirm not in ("y", "yes"):
        print("Operation cancelled. README.md was not modified.")
        return

    # 4. Perform README update upon confirmation
    if not readme_path.exists():
        print(f"Creating new README.md at {readme_path.resolve()}...")
        readme_path.write_text(f"# {project_name}\n\n{new_structure_section}\n", encoding="utf-8")
        print("README.md created successfully.")
        return

    content = readme_path.read_text(encoding="utf-8")

    # Regex matches "## Project Structure" down to the end of the code block
    pattern = r"## Project Structure\s*\n\n```(?:text)?\n[\s\S]*?\n```"

    if re.search(pattern, content):
        updated_content = re.sub(pattern, new_structure_section, content)
        print("Updated existing '## Project Structure' section in README.md.")
    elif "## Project Structure" in content:
        # Fallback if section header exists without standard code block
        pattern_fallback = r"## Project Structure.*?(?=\n\n## |\Z)"
        updated_content = re.sub(pattern_fallback, new_structure_section, content, flags=re.DOTALL)
        print("Replaced '## Project Structure' section in README.md.")
    else:
        # Append to the end if header does not exist
        updated_content = content.rstrip() + f"\n\n{new_structure_section}\n"
        print("Appended '## Project Structure' section to README.md.")

    readme_path.write_text(updated_content, encoding="utf-8")


if __name__ == "__main__":
    update_readme()
