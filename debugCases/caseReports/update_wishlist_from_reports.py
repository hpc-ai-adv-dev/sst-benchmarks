#!/usr/bin/env python3
"""Generate a wishlist list from case reports and print it to stdout.

This script scans all case report markdown files in this directory, extracts
subheaders under each "Thoughts and wishlist items" section and builds a
summary list with parenthesized source links with anchors.

Example link format:
    - Some wishlist item ([badMerge](badMerge.md#thoughts-and-wishlist-items))
"""

import argparse
import re
from pathlib import Path

SECTION_IN_REPORT_RE = re.compile(r"^(#{1,6})\s+Thoughts and wishlist items\s*$", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")


def extract_headers_by_report(reports_dir):
    """Return ordered mapping: wishlist-header -> list of source report paths."""
    mapping = {}

    for report_path in sorted(reports_dir.glob("*.md")):
        if report_path.name == "WISHLIST.md":
            continue

        lines = report_path.read_text(encoding="utf-8").splitlines()
        in_section = False
        section_level = 0

        for line in lines:
            match = SECTION_IN_REPORT_RE.match(line)
            if match:
                in_section = True
                section_level = len(match.group(1))
                continue

            if not in_section:
                continue

            heading_match = HEADING_RE.match(line)
            if not heading_match:
                continue

            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()

            if level <= section_level:
                in_section = False
                continue

            if heading_text not in mapping:
                mapping[heading_text] = []
            if report_path not in mapping[heading_text]:
                mapping[heading_text].append(report_path)

    return mapping


def build_bullets(mapping):
    bullets = []

    for header, paths in mapping.items():
        links = ", ".join(
            f"[{path.stem}]({path.name}#thoughts-and-wishlist-items)" for path in paths
        )
        bullets.append(f"- {header} ({links})")

    return bullets


def main():
    parser = argparse.ArgumentParser(description="Print case-report wishlist items.")
    parser.parse_args()

    reports_dir = Path(__file__).resolve().parent

    mapping = extract_headers_by_report(reports_dir)
    bullets = build_bullets(mapping)

    for bullet in bullets:
        print(bullet)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())