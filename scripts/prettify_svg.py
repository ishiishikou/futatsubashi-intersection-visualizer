#!/usr/bin/env python3
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def prettify(path: Path) -> None:
    tree = ET.parse(path)
    root = tree.getroot()
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: prettify_svg.py <svg> [<svg> ...]", file=sys.stderr)
        return 2
    for raw in sys.argv[1:]:
        path = Path(raw)
        prettify(path)
        print(f"prettified {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
