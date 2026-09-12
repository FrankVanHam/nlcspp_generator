from pathlib import Path

from nlcspp_generator.base_schema import render_base_schema
from nlcspp_generator.domains import load_domain_catalog
from nlcspp_generator.information_model import (
    base_schema_domain_order,
    load_features,
    order_features,
)


WORKSPACE = Path(__file__).parents[2]
INPUT = WORKSPACE / "training" / "input"
BASE_GOLDEN = WORKSPACE / "training" / "output" / "NLCS_Netbeheer.xsd"


def test_renders_base_schema_byte_for_byte() -> None:
    source_features = load_features(INPUT / "InformatiemodelNetbeheerv12.1.xlsx")
    project = next(feature for feature in source_features if feature.name == "AprojectReferentie")
    features = order_features(
        tuple(feature for feature in source_features if feature.name != project.name)
    )
    catalog = load_domain_catalog(INPUT / "domains_InformatiemodelNetbeheerV12.1.xls")
    domains = catalog.select_base_domains(
        base_schema_domain_order(project, features)
    )

    generated = render_base_schema(project, features, domains, version="12.1")

    assert len(features) == 56
    assert len(domains) == 122
    assert generated == BASE_GOLDEN.read_bytes()