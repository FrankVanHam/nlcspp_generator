from pathlib import Path

from nlcspp_generator.domains import load_domain_catalog
from nlcspp_generator.information_model import (
    load_features,
    selection_schema_domain_order,
)
from nlcspp_generator.selection_schema import render_selection_schema


WORKSPACE = Path(__file__).parents[2]
DOMAIN_WORKBOOK = WORKSPACE / "training" / "input" / "domains_InformatiemodelNetbeheerV12.1.xls"
SELECTION_GOLDEN = (
    WORKSPACE
    / "training"
    / "output"
    / "NLCS_NetbeheerStedinV12.1Import_Keuzelijst.xsd"
)


def test_renders_stedin_selection_schema_byte_for_byte() -> None:
    features = load_features(
        WORKSPACE / "training" / "input" / "InformatiemodelNetbeheerv12.1.xlsx"
    )
    catalog = load_domain_catalog(DOMAIN_WORKBOOK)

    domains = catalog.select_open_domains(
        "Stedin", selection_schema_domain_order(features)
    )
    generated = render_selection_schema(domains)

    assert len(domains) == 87
    assert sum(len(domain.values) for domain in domains) == 763
    assert generated == SELECTION_GOLDEN.read_bytes()


def test_alliander_is_an_alias_for_liander() -> None:
    catalog = load_domain_catalog(DOMAIN_WORKBOOK)
    order = tuple(definition.name for definition in catalog.definitions)

    assert catalog.select_open_domains("Alliander", order) == catalog.select_open_domains(
        "Liander", order
    )