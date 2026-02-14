#!/usr/bin/env python3
"""
Validate titles in pizzini.xml using heuristics discussed:
- Prefer ALL-CAPS heading at start, optionally followed by parenthetical part markers.
- If a numbered parenthetical exists (e.g., (UNO), (III), (2)), include it and stop at the closing ')'.
- Fallback to the first meaningful sentence/snippet.
- Normalize NBSP/thin spaces; trim punctuation artifacts.
Reports items where the existing <Title> is missing or differs from the derived title.
"""
import re
import xml.etree.ElementTree as ET
from typing import List, Dict

INPUT_XML = "pizzini.xml"


def _normalize_spaces(text: str) -> str:
    if not text:
        return ""
    # Replace non-breaking and thin spaces with regular space
    s = text.replace("\u00A0", " ").replace("\u2009", " ")
    # Collapse multiples
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _clean_title(text: str) -> str:
    s = _normalize_spaces(text or "")
    # Trim trailing punctuation and dashes
    s = re.sub(r"\s*[-–—]\s*$", "", s)
    s = re.sub(r"\s*[:;.,!?]+\s*$", "", s)
    return s


_ROMAN = {"I":1,"II":2,"III":3,"IV":4,"V":5,"VI":6,"VII":7,"VIII":8,"IX":9,"X":10}
_ITALIAN_PARTS = {"UNO","DUE","TRE","QUATTRO","CINQUE","SEI","SETTE","OTTO","NOVE","DIECI"}


def derive_title_from_content(content: str) -> str:
    """Derive a title from content using heuristics."""
    s = _normalize_spaces(content or "")
    if not s:
        return ""

    # 1) ALL-CAPS heading possibly with parenthetical part marker
    # Examples: NOVISSIMI (CINQUE) | LA MOLLA (UNO)
    m = re.match(r"^([A-ZÀ-ÖØ-ß][A-ZÀ-ÖØ-ß\s'\.]+?)(\s*\(([^)]+)\))?\s*(?=\b|:)", s)
    if m:
        main = m.group(1).strip()
        paren = m.group(3).strip() if m.group(3) else ""
        title = main
        if paren:
            up = paren.upper()
            if up in _ITALIAN_PARTS or up in _ROMAN or re.fullmatch(r"\d+", paren):
                title = f"{main} ({paren})"  # stop at ')' as required
        return _clean_title(title)

    # 2) Colon-first: take text before first colon as title if short
    colon_idx = s.find(":")
    if 0 < colon_idx <= 60:
        cand = _clean_title(s[:colon_idx])
        if 5 <= len(cand) <= 60:
            return cand

    # 3) Fallback: first sentence up to period/exclamation/question or 60 chars
    m2 = re.search(r"([^.?!]{5,60})[.?!]", s)
    if m2:
        return _clean_title(m2.group(1))
    return _clean_title(s[:60])


def _title_issues(title: str) -> List[str]:
    t = title or ""
    issues = []
    if not t.strip():
        issues.append("missing")
        return issues
    if len(t.strip()) < 3:
        issues.append("too-short")
    if len(t.strip()) > 80:
        issues.append("too-long")
    # Parentheses checks
    open_count = t.count("(")
    close_count = t.count(")")
    if open_count != close_count:
        issues.append("unbalanced-parens")
    if t.endswith("("):
        issues.append("dangling-open-paren")
    if re.search(r"\)\w", t):
        issues.append("no-space-after-paren")
    # Glued uppercase to lowercase like "LIBERTA’Se"
    if re.search(r"[A-ZÀ-ÖØ-ß'’]{2,}[A-ZÀ-ÖØ-ß'’]{2,}[a-zà-öø-ÿ]", t):
        issues.append("glued-uppercase-to-lowercase")
    return issues


def validate(input_path: str = INPUT_XML) -> List[Dict[str, str]]:
    tree = ET.parse(input_path)
    root = tree.getroot()
    # Find all pizzini entries (skip schema node)
    items = root.findall('.//pizzini/pizzini') or [e for e in root.findall('.//pizzini') if e.find('Id') is not None]
    # Deduplicate by Id if both patterns matched
    seen = set()
    mismatches = []

    for item in items:
        id_text = (item.findtext("Id") or "?").strip()
        if id_text in seen:
            continue
        seen.add(id_text)
        title_el = item.find("Title")
        content = item.findtext("Content") or ""
        current = (title_el.text if title_el is not None and title_el.text else "").strip()
        issues = _title_issues(current)
        if issues:
            mismatches.append({
                "id": id_text,
                "current": current,
                "issues": ",".join(issues),
            })
    return mismatches


if __name__ == "__main__":
    mismatches = validate(INPUT_XML)
    print(f"Problematic titles: {len(mismatches)} found")
    for m in mismatches[:30]:  # Show first 30 for brevity
        print(f"Id {m['id']}\n  title : {m['current']}\n  issues: {m['issues']}\n")
    if len(mismatches) > 30:
        print(f"... and {len(mismatches) - 30} more")
