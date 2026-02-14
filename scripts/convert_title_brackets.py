import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

WORKDIR = Path(__file__).resolve().parents[1]
XML_PATH = WORKDIR / "pizzini.xml"
BACKUP_PATH = WORKDIR / "pizzini_parentheses_backup.xml"


def normalize_spaces(s: str) -> str:
    # Collapse multiple spaces and trim
    return re.sub(r"\s+", " ", s).strip()


def convert_parentheses_to_dash(title: str) -> str:
    # Find all parenthetical groups
    groups = re.findall(r"\(([^)]+)\)", title)
    if not groups:
        return title

    # Remove all parenthetical segments from the base
    base = re.sub(r"\s*\([^)]*\)\s*", " ", title)
    base = normalize_spaces(base)

    # Join groups with em dashes
    suffix = " — ".join(normalize_spaces(g) for g in groups if normalize_spaces(g))
    if suffix:
        return f"{base} — {suffix}"
    else:
        return base


def main():
    if not XML_PATH.exists():
        raise FileNotFoundError(f"XML not found: {XML_PATH}")

    # Backup first
    shutil.copy2(XML_PATH, BACKUP_PATH)

    tree = ET.parse(XML_PATH)
    root = tree.getroot()

    changed = 0
    total = 0

    for item in root.findall("pizzini"):
        title_el = item.find("Title")
        if title_el is None or title_el.text is None:
            continue
        total += 1
        old = title_el.text
        new = convert_parentheses_to_dash(old)
        if new != old:
            title_el.text = new
            changed += 1

    tree.write(XML_PATH, encoding="utf-8", xml_declaration=False)

    print(f"Processed titles: {total}")
    print(f"Changed titles: {changed}")
    print(f"Backup saved to: {BACKUP_PATH}")


if __name__ == "__main__":
    main()
