from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import tempfile

from .base_schema import render_base_schema
from .discovery import locate_input_sources
from .domains import COMPANY_ALIASES, load_domain_catalog
from .information_model import (
    base_schema_domain_order,
    load_features,
    order_features,
    selection_schema_domain_order,
)
from .selection_schema import render_selection_schema


BASE_SCHEMA_NAME = "NLCS_Netbeheer.xsd"


@dataclass(frozen=True)
class GeneratedFiles:
    base_schema: Path
    selection_schema: Path


def generate(
    input_directory: Path,
    output_directory: Path,
    netbeheerder: str = "Stedin",
) -> GeneratedFiles:
    canonical_company = COMPANY_ALIASES.get(netbeheerder, netbeheerder)
    sources = locate_input_sources(input_directory)
    source_features = load_features(sources.information_model)
    try:
        project_feature = next(
            feature for feature in source_features if feature.name == "AprojectReferentie"
        )
    except StopIteration as error:
        raise ValueError("Information model has no AprojectReferentie object") from error
    features = order_features(
        tuple(feature for feature in source_features if feature.name != project_feature.name)
    )
    catalog = load_domain_catalog(sources.domain_catalog)
    base_domains = catalog.select_base_domains(
        base_schema_domain_order(project_feature, features)
    )
    selection_domains = catalog.select_open_domains(
        canonical_company, selection_schema_domain_order(source_features)
    )

    base_bytes = render_base_schema(
        project_feature, features, base_domains, sources.version
    )
    selection_bytes = render_selection_schema(
        selection_domains, BASE_SCHEMA_NAME, sources.version
    )
    selection_name = (
        f"NLCS_Netbeheer{canonical_company}V{sources.version}Import_Keuzelijst.xsd"
    )
    output_directory.mkdir(parents=True, exist_ok=True)
    base_path = output_directory / BASE_SCHEMA_NAME
    selection_path = output_directory / selection_name
    _write_atomically(base_path, base_bytes)
    _write_atomically(selection_path, selection_bytes)
    return GeneratedFiles(base_path, selection_path)


def _write_atomically(path: Path, content: bytes) -> None:
    file_descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(file_descriptor, "wb") as temporary_file:
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise