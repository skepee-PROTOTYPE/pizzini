import argparse
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET


UPPER_CHARS = "A-ZÀ-ÖØ-Þ"
LOWER_CHARS = "a-zà-öø-ÿ"


def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def extract_title_from_content(content: str) -> str:
    if not content:
        return ""
    t = content.strip()

    # Remove leading quotes or weird markers
    t = re.sub(r"^[\"'«»“”‘’>\s]+", "", t)

    # 1) Heading in ALL CAPS (possibly with digits/parentheses) at start until first lowercase
    m = re.match(rf"^([ {UPPER_CHARS}0-9'’\-()/:]+)", t)
    if m:
        candidate = normalize_space(m.group(1))
        # Ensure it's not trivially short and has some uppercase letters
        if len(re.sub(rf"[^ {UPPER_CHARS}]", "", candidate)) >= 3:
            return candidate.strip(" -–—:;,.()")

    # 2) Title-like phrase up to a colon/period/dash/parenthesis (proper case)
    m = re.match(rf"^([{UPPER_CHARS}][ {UPPER_CHARS}{LOWER_CHARS}0-9'’\-]+?)(?::|—|–|-|\(|\.|!|\?)", t)
    if m:
        return normalize_space(m.group(1)).strip(" -–—:;,")

    # 3) Known pattern 'Pizzino della settimana' (case-insensitive)
    m = re.match(r"^(Pizzino della settimana)", t, re.IGNORECASE)
    if m:
        return "Pizzino della settimana"

    # 4) Fallback: first sentence (limited length)
    first = re.split(r"[\.\!\?]\s", t, maxsplit=1)[0]
    first = normalize_space(first)
    if len(first) > 120:
        first = first[:120].rsplit(" ", 1)[0]
    return first


def ensure_title_element(item_el: ET.Element) -> bool:
    """Ensure each <pizzini> item has a <Title>. Returns True if modified."""
    children = list(item_el)
    id_el = item_el.find("Id")
    date_el = item_el.find("Date")
    title_el = item_el.find("Title")
    content_el = item_el.find("Content")

    if title_el is not None and (title_el.text and title_el.text.strip()):
        return False  # already has a title

    content_text = content_el.text if content_el is not None else ""
    derived = extract_title_from_content(content_text)
    if not derived:
        derived = "Senza titolo"

    if title_el is None:
        title_el = ET.Element("Title")
        # Insert respecting sequence: Id, Date, Title, Content
        # Compute insert index
        insert_idx = 0
        if id_el is not None:
            insert_idx = children.index(id_el) + 1
        if date_el is not None:
            insert_idx = children.index(date_el) + 1
        item_el.insert(insert_idx, title_el)

    title_el.text = derived
    return True


def process_file(input_path: str, output_path: str, in_place: bool) -> int:
    parser = ET.XMLParser()
    tree = ET.parse(input_path, parser=parser)
    root = tree.getroot()

    # Iterate only over child items named 'pizzini' directly under root
    modified_count = 0
    for item in root.findall("./pizzini"):
        if ensure_title_element(item):
            modified_count += 1

    # Write
    if in_place:
        # Create backup
        backup_path = input_path + ".bak"
        if not os.path.exists(backup_path):
            shutil.copyfile(input_path, backup_path)
        tree.write(input_path, encoding="utf-8", xml_declaration=True)
        return modified_count
    else:
        out_dir = os.path.dirname(output_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        return modified_count


def main():
    ap = argparse.ArgumentParser(description="Add/derive Title for each <pizzini> item from Content")
    ap.add_argument("--in", dest="inp", required=True, help="Input XML file path (pizzini_original.xml)")
    ap.add_argument("--out", dest="outp", help="Output XML file path (if omitted and --inplace is false, appends .titled.xml)")
    ap.add_argument("--inplace", action="store_true", help="Modify the input file in place (creates .bak backup)")
    args = ap.parse_args()

    inp = args.inp
    outp = args.outp
    in_place = args.inplace

    if not os.path.exists(inp):
        print(f"Input file not found: {inp}", file=sys.stderr)
        sys.exit(1)

    if not in_place and not outp:
        base, ext = os.path.splitext(inp)
        outp = base + ".titled" + ext

    count = process_file(inp, outp, in_place)
    target = inp if in_place else outp
    print(f"Titles added/updated: {count}\nWritten: {target}")


if __name__ == "__main__":
    main()
