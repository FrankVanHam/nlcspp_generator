from pathlib import Path

from .workbook import read_information_model
from .xsd_writer import render_xsd


def generate_xsd(
    model_path: str | Path,
    domains_path: str | Path,
    output_path: str | Path,
    version: str | None = None,
) -> None:
    model = read_information_model(model_path, domains_path, version)
    data = render_xsd(model)
    destination = Path(output_path)
    temporary = destination.with_name(destination.name + ".tmp")
    try:
        temporary.write_bytes(data)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)