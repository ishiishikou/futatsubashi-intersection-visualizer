#!/usr/bin/env python3
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

MIN_FONT_SIZE = 18.0


def inspect(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return [f"XML parse error: {exc}"]

    if "viewBox" not in root.attrib:
        errors.append("missing viewBox")

    for elem in root.iter():
        tag = elem.tag.rsplit("}", 1)[-1]
        if tag == "image":
            href = elem.attrib.get("href") or elem.attrib.get("{http://www.w3.org/1999/xlink}href")
            if href and (href.startswith("http://") or href.startswith("https://")):
                errors.append(f"external image reference is not allowed: {href}")
        if tag in {"text", "tspan"}:
            size = elem.attrib.get("font-size")
            if size:
                try:
                    if float(size) < MIN_FONT_SIZE:
                        errors.append(f"font-size below {MIN_FONT_SIZE}: {size}")
                except ValueError:
                    errors.append(f"non-numeric font-size: {size}")

    return errors


def main() -> int:
    paths = [Path(p) for p in sys.argv[1:]]
    if not paths:
        print("usage: inspect_svg.py <svg> [<svg> ...]", file=sys.stderr)
        return 2

    failed = False
    for path in paths:
        errors = inspect(path)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {path}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
