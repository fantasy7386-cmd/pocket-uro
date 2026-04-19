#!/usr/bin/env python3
"""Convert URO_Resident_Tips_and_Guide.md → tips-guide.json"""

import json
import re
import sys
from pathlib import Path

MD_PATH = Path.home() / "Downloads" / "URO_Resident_Tips_and_Guide.md"
OUT_PATH = Path(__file__).parent / "tips-guide.json"

ROMAN = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6,
    "VII": 7, "VIII": 8, "IX": 9, "X": 10, "XI": 11, "XII": 12, "XIII": 13
}

def parse_markdown(text: str) -> dict:
    lines = text.split("\n")
    sections = []
    current_section = None
    current_sub = None
    content_lines = []

    def flush_subsection():
        nonlocal content_lines
        if current_sub is not None:
            md = "\n".join(content_lines).strip()
            current_sub["markdown"] = md
        content_lines = []

    for line in lines:
        # Section header: ## I. Title or ## XIII. Title
        m = re.match(r"^## ([IVXLC]+)\.\s+(.+)$", line)
        if m:
            flush_subsection()
            roman, title = m.group(1), m.group(2)
            num = ROMAN.get(roman, len(sections) + 1)
            current_section = {
                "id": f"tg_{num:02d}",
                "number": roman,
                "title": title,
                "full_title": f"{roman}. {title}",
                "subsections": []
            }
            sections.append(current_section)
            current_sub = None
            continue

        # Subsection header: ### Title
        if line.startswith("### ") and current_section is not None:
            flush_subsection()
            sub_title = line[4:].strip()
            sub_idx = len(current_section["subsections"]) + 1
            current_sub = {
                "id": f"{current_section['id']}_{sub_idx:02d}",
                "title": sub_title,
                "markdown": ""
            }
            current_section["subsections"].append(current_sub)
            continue

        # Skip document-level dividers and preamble
        if current_section is None:
            continue
        if line.strip() == "---":
            continue

        # Everything else → content for current subsection
        if current_sub is not None:
            content_lines.append(line)
        elif current_section is not None and line.strip():
            # Content directly under section header with no subsection
            # (e.g., a table or text before first ###)
            # Create an implicit subsection
            sub_idx = len(current_section["subsections"]) + 1
            current_sub = {
                "id": f"{current_section['id']}_{sub_idx:02d}",
                "title": "(General)",
                "markdown": ""
            }
            current_section["subsections"].append(current_sub)
            content_lines.append(line)

    flush_subsection()
    return sections


def main():
    text = MD_PATH.read_text(encoding="utf-8")
    sections = parse_markdown(text)

    total_subs = sum(len(s["subsections"]) for s in sections)

    output = {
        "version": "1.0.0",
        "updated": "2026-04-06",
        "total_sections": len(sections),
        "total_subsections": total_subs,
        "sections": sections
    }

    OUT_PATH.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    # Summary
    print(f"Converted: {len(sections)} sections, {total_subs} subsections")
    for s in sections:
        print(f"  {s['number']:>5}. {s['title']} — {len(s['subsections'])} subsections")


if __name__ == "__main__":
    main()
