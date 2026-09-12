from __future__ import annotations

import argparse
from pathlib import Path

from .generator import generate


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate NLCS Netbeheer XSD files from Excel workbooks"
    )
    parser.add_argument("input_directory", type=Path)
    parser.add_argument("output_directory", type=Path)
    parser.add_argument(
        "--netbeheerder",
        default="Stedin",
        choices=("Stedin", "Enexis", "Liander", "Alliander"),
    )
    arguments = parser.parse_args()
    generated = generate(
        arguments.input_directory,
        arguments.output_directory,
        arguments.netbeheerder,
    )
    print(generated.base_schema)
    print(generated.selection_schema)


if __name__ == "__main__":
    main()