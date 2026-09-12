from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .generator import generate_xsd
from .workbook import WorkbookError


def _default_domains(model_path: Path) -> Path | None:
    matches = sorted(model_path.parent.glob("domains_*.xls"))
    return matches[0] if len(matches) == 1 else None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate an NLCS++ XSD from Excel workbooks")
    parser.add_argument("model", type=Path, help="Informatiemodel .xlsx file")
    parser.add_argument("output", type=Path, help="Destination .xsd file")
    parser.add_argument("--domains", type=Path, help="Domain definitions .xls file")
    parser.add_argument("--version", help="Schema version (normally inferred from the model filename)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    domains = args.domains or _default_domains(args.model)
    if domains is None:
        print("error: pass --domains or place exactly one domains_*.xls beside the model", file=sys.stderr)
        return 2
    try:
        generate_xsd(args.model, domains, args.output, args.version)
    except (OSError, WorkbookError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0