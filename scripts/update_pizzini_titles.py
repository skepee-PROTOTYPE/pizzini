import argparse
import re
import sys
from typing import List, Optional, Tuple
import xml.etree.ElementTree as ET


def normalize_text(s: str) -> str:
    s = s.strip()
    # Replace newlines/tabs with spaces and collapse spaces
    # Normalize non-breaking and thin spaces to regular spaces first
    s = s.replace("\u00A0", " ").replace("\u202F", " ")
    s = re.sub(r"[\r\n\t]+", " ", s)
    s = re.sub(r"\s{2,}", " ", s)
    # Trim leading/ending quotes and guillemets
    s = s.strip(" \u00AB\u00BB\"'“”‘’»«")
    return s.strip()


GENERIC_PREFIXES = [
    "Pizzino della settimana",
    "PIZZINO DELLA SETTIMANA",
    "PIZZINO DI PROVA",
]


ROMAN_NUM = r"I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII"
ITALIAN_NUM = r"UNO|DUE|TRE|QUATTRO|CINQUE|SEI|SETTE|OTTO|NOVE|DIECI"


def clean_title(t: str) -> str:
    t = t.strip()
    # Trim dangling punctuation/quotes
    t = t.strip(" .,:;\u00AB\u00BB\"'“”‘’»«")
    # Compress inner spaces
    t = re.sub(r"\s{2,}", " ", t)
    return t


def is_all_caps_block(s: str) -> bool:
    # Treat accented uppercase letters and allowed symbols as caps block
    return bool(re.fullmatch(r"[A-ZÀ-ÖØ-Ý'’\s().0-9°ª-]+", s))


_TRIVIAL_WORDS = {
    "IL",
    "LA",
    "LO",
    "L",
    "L’",
    "L'",
    "I",
    "GLI",
    "LE",
    "UN",
    "UNO",
    "UNA",
}


def polish_candidate(title: str) -> str:
    """Post-process derived title to fix glued words and drop trivial tokens."""
    s = clean_title(title)
    # If starts with glued ALL-CAPS immediately followed by a lowercase sequence (e.g., TUTTOTutto), keep the ALL-CAPS token only
    # NOTE: Require the next character sequence to include at least one lowercase letter to avoid truncating
    # valid ALL-CAPS words followed by a space (e.g., 'ANCORA SUL ...').
    m = re.match(r"^([A-ZÀ-ÖØ-Ý]{3,})([A-ZÀ-ÖØ-Ý]?[a-zà-öø-ÿ].*)$", s)
    if m:
        caps = m.group(1)
        if 3 <= len(caps) <= 60:
            s = caps
    # Remove solitary trivial words
    if s.upper() in _TRIVIAL_WORDS:
        return ""
    return s


def _finalize_title(original_text: str, cand: str) -> str:
    """Trim a stray single capital glued from the next word.
    If the original text continues with a lowercase letter immediately after
    the candidate (optionally with whitespace), drop a trailing single
    uppercase letter from the candidate (e.g., 'IL SILENZIOI' → 'IL SILENZIO').
    """
    if not cand:
        return cand
    pattern = rf"^\s*{re.escape(cand)}[\s\u00A0\u202F]*[a-zà-öø-ÿ]"
    if re.match(pattern, original_text, flags=re.UNICODE):
        if re.search(r"[A-ZÀ-ÖØ-Þ]$", cand):
            return cand[:-1].rstrip()
    return cand


def derive_title_from_content(content: str) -> Optional[str]:
    """Best-effort heuristic to derive a compact title from the item's content.

    Preference order (revised):
    1) Colon-based title when a meaningful ':' appears early
    2) Numbered pattern at start (e.g., WORDS (UNO|III|1°)) — keep parentheses
    3) Leading ALL-CAPS header (used primarily when ':' is missing)
    4) First sentence
    5) Short snippet fallback
    """
    if not content:
        return None
    text = normalize_text(content)
    if not text:
        return None

    # 1) Colon-based
    colon_pos = text.find(":")
    if 0 < colon_pos <= 140:
        pre = clean_title(text[:colon_pos])
        post = normalize_text(text[colon_pos + 1 :])
        if any(pre.upper().startswith(pfx.upper()) for pfx in GENERIC_PREFIXES):
            m_q = re.match(r"^([^\.!?]{5,120}?)[\?\.!]", post)
            if m_q:
                cand = polish_candidate(m_q.group(1))
                cand = _finalize_title(text, cand)
                if 8 <= len(cand) <= 120:
                    return cand
        if 6 <= len(pre) <= 80 and not pre.endswith("…"):
            cand = polish_candidate(pre)
            cand = _finalize_title(text, cand)
            if cand and len(cand) >= 6:
                return cand

    # 2) Numbered pattern (keep parentheses in title) — prioritize capturing the full "TITLE (PART)"
    m_num = re.match(
        r"^([A-ZÀ-ÖØ-Ý][A-ZÀ-ÖØ-Ý'’\s-]{2,})\s*\((" + ITALIAN_NUM + r"|" + ROMAN_NUM + r"|[0-9]+[°ª]?)\)",
        text,
    )
    if m_num:
        main = clean_title(m_num.group(1)).upper()
        part = m_num.group(2)
        cand = f"{main} ({part})"
        cand = _finalize_title(text, cand)
        # Validate caps block including parentheses
        if 5 <= len(cand) <= 80 and is_all_caps_block(main):
            cand2 = polish_candidate(cand)
            if cand2:
                return cand2

    # 3) Leading ALL-CAPS header
    ws = r"[\s\u00A0\u202F]+"
    CAPS_WORD = r"[A-ZÀ-ÖØ-Þ0-9][A-ZÀ-ÖØ-Þ0-9'’.\/-]*"
    caps_run_re = re.compile(rf"^({CAPS_WORD}(?:{ws}{CAPS_WORD})*){ws}(?=[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ])")
    m_caps = caps_run_re.match(text)
    caps_block = None
    if m_caps:
        caps_block = clean_title(m_caps.group(1)).upper()
    else:
        caps_start_re = re.compile(rf"^({CAPS_WORD}(?:{ws}{CAPS_WORD})+)(?=[\s\u00A0\u202F]*[\.:;–—\-]|$)")
        m2 = caps_start_re.match(text)
        if m2:
            caps_block = clean_title(m2.group(1)).upper()
        else:
            mlow = re.search(r"[a-zà-öø-ÿ]", text)
            if mlow:
                idx = mlow.start()
                head = text[:idx]
                head = re.sub(r"[\s\u00A0\u202F]+[A-ZÀ-ÖØ-Þ]$", "", head)
                head = clean_title(head).upper()
                if head and is_all_caps_block(head) and len(head) >= 3:
                    # If the original text has exactly one capital letter glued before the first lowercase (e.g., '... SILENZIOIn'), drop it
                    if re.match(rf"^{re.escape(head)}[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ]", text):
                        head = head[:-1]
                        head = head.rstrip()
                    caps_block = head
    if caps_block:
        cand = polish_candidate(caps_block)
        cand = _finalize_title(text, cand)
        if cand:
            return cand

    # (removed: numbered pattern handled earlier)

    # 4) First sentence fallback
    m_sent = re.match(r"^([^\.!?]{8,90}?)\.?[!\?]", text)
    if m_sent:
        cand = polish_candidate(m_sent.group(1))
        cand = _finalize_title(text, cand)
        if len(cand) >= 6:
            return cand

    # 5) Snippet fallback
    snippet = text[:60]
    if " " in snippet:
        snippet = snippet[: snippet.rfind(" ")]
    cand = polish_candidate(snippet)
    cand = _finalize_title(text, cand)
    return cand if cand else None


def _build_title_regex(title: str) -> re.Pattern:
    """Build a robust regex to match the title at the very start of content.
    - Escapes regex chars in title
    - Makes spaces flexible (\s+)
    - Allows trailing separators like colon/dashes and whitespace
    - Case-insensitive, unicode-aware
    """
    # Normalize title spacing/punctuation for pattern
    t = clean_title(title)
    # Escape regex meta, then replace escaped spaces with \s+
    t_esc = re.escape(t)
    t_esc = re.sub(r"\\\s+", r"\\s+", t_esc)
    # Also permit straight/curly quotes variations around apostrophes
    t_esc = t_esc.replace("\\'", "[\u2019']")
    # Build pattern: optional leading whitespace, exact title, require a word-boundary or separator/end
    # This avoids matching partial words (e.g., 'ANCOR' inside 'ANCORA').
    pat = rf"^\s*{t_esc}(?:\b|[\s\.:;–—-]|$)[\s\.:;–—-]*\s*"
    return re.compile(pat, flags=re.IGNORECASE | re.UNICODE | re.MULTILINE)


def strip_leading_heading_from_content(content: str, title: str) -> str:
    """If content begins with the given title (or superficial variants), strip it.
    Returns possibly-updated content (original if no change)."""
    if not content or not title:
        return content
    pattern = _build_title_regex(title)
    new = pattern.sub("", content, count=1)
    if new == content:
        # Try extended match: Title followed by optional parenthetical note or subtitle after dash/colon
        base = clean_title(title)
        t_esc = re.escape(base)
        t_esc = re.sub(r"\\\s+", r"\\s+", t_esc)
        t_esc = t_esc.replace("\\'", "[\u2019']")
        # Accept NBSP/thin spaces as whitespace; capture up to first sentence boundary
        ws = r"[\s\u00A0\u202F]+"
        extended_pat = rf"^\s*{t_esc}(?:{ws}\([^\)\n\r]{{1,80}}\))?(?:{ws}?[\-–—:]{1}\s*[^\.!?\n\r]{{1,80}})?[\s\.:;–—-]*\s*"
        new2 = re.sub(extended_pat, "", content, count=1, flags=re.IGNORECASE|re.UNICODE|re.MULTILINE)
        if new2 != content:
            new = new2
    # Also trim a single leading blank line left behind
    if new.startswith("\n\n"):
        new = new.lstrip()
    return new


def ensure_title_element(entry: ET.Element) -> Tuple[bool, Optional[str]]:
    """Insert or fill the Title element based on Content.
    Also de-duplicates a leading heading from Content if it matches the Title.
    Returns (changed, title)."""
    # Find child elements by tag name
    children = list(entry)
    tags = [ch.tag for ch in children]

    # Fetch existing elements
    id_el = entry.find("Id")
    date_el = entry.find("Date")
    title_el = entry.find("Title")
    content_el = entry.find("Content")

    if content_el is None or (content_el.text or "").strip() == "":
        return False, None

    current_title = (title_el.text if title_el is not None and title_el.text else "").strip()
    content_text = content_el.text or ""
    # If a title already exists, attempt content de-duplication and repair malformed numbered titles
    if current_title:
        changed = False
        new_content = strip_leading_heading_from_content(content_text, current_title)
        if new_content != content_text:
            content_el.text = new_content.lstrip()
            changed = True

        # Repair titles like 'NOVISSIMI (CINQUE)Filippo ...' → 'NOVISSIMI (CINQUE)'
        # Only trim when the parenthetical part matches a known numbering pattern
        # and is immediately followed by a lowercase-run of sentence text.
        # Generic trim: if there's a closing ')' followed immediately by sentence text, cut at ')'
        m_generic = re.match(r"^(?P<head>.+?\))\s*(?P<rest>[A-ZÀ-ÖØ-Ý]?[a-zà-öø-ÿ].*)$", current_title)
        if m_generic:
            repaired = clean_title(m_generic.group("head"))
            if repaired != current_title:
                current_title = repaired
                title_el.text = current_title
                changed = True

        return changed, current_title

    derived = derive_title_from_content(content_text)
    if not derived:
        return False, None

    # Create Title element if missing
    if title_el is None:
        title_el = ET.Element("Title")
        # Insert after Date (sequence: Id, Date, Title, Content)
        insert_idx = 0
        if id_el is not None and "Id" in tags:
            insert_idx = max(insert_idx, tags.index("Id") + 1)
        if date_el is not None and "Date" in tags:
            insert_idx = max(insert_idx, tags.index("Date") + 1)
        # Bound check
        insert_idx = min(insert_idx, len(children))
        entry.insert(insert_idx, title_el)

    title_el.text = derived

    # After setting Title, remove duplicated heading from Content if present
    new_content = strip_leading_heading_from_content(content_text, derived)
    if new_content != content_text:
        content_el.text = new_content.lstrip()

    return True, derived


def indent(elem: ET.Element, level: int = 0) -> None:
    """Pretty-print indentation (in-place) for ElementTree output."""
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level + 1)
        if not e.tail or not e.tail.strip():  # type: ignore[name-defined]
            e.tail = i  # type: ignore[name-defined]
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i


def process(input_path: str, output_path: str, dry_run: bool = False) -> int:
    tree = ET.parse(input_path)
    root = tree.getroot()

    # Items are nested <pizzini> inside root <pizzini>
    items = root.findall("pizzini")
    updated = 0
    derived_list: List[Tuple[str, Optional[str]]] = []

    for item in items:
        changed, title = ensure_title_element(item)
        if changed:
            updated += 1
        # Collect id for logging
        id_text = (item.findtext("Id") or "?").strip()
        derived_list.append((id_text, title))

    # Post-pass: repair any existing numbered titles that still have appended sentence text
    for item in items:
        title_el = item.find("Title")
        if title_el is None or not title_el.text:
            continue
        t = title_el.text.strip()
        m_generic = re.match(r"^(?P<head>.+?\))\s*(?P<rest>[A-ZÀ-ÖØ-Ý]?[a-zà-öø-ÿ].*)$", t)
        if m_generic:
            repaired = clean_title(m_generic.group("head"))
            if repaired != t:
                title_el.text = repaired
                updated += 1

    if not dry_run:
        indent(root)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)

    # Simple report to stdout
    print(f"Processed {len(items)} items; added/updated titles: {updated}")
    for pid, t in derived_list:
        if t:
            print(f"  Id {pid}: '{t}'")
        else:
            print(f"  Id {pid}: (unchanged or no content)")

    return updated


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Derive and insert Title from Content for pizzini XML entries.")
    p.add_argument("--in", dest="inp", default="pizzini_original.xml", help="Input XML path (default: pizzini_original.xml)")
    p.add_argument(
        "--out",
        dest="out",
        default="pizzini.xml",
        help="Output XML path (default: pizzini.xml)",
    )
    p.add_argument("--dry-run", action="store_true", help="Parse and preview without writing output file")
    args = p.parse_args(argv)

    try:
        return 0 if process(args.inp, args.out, dry_run=args.dry_run) >= 0 else 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())