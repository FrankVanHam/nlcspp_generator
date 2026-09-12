from dataclasses import dataclass


@dataclass(frozen=True)
class AttributeDefinition:
    feature_name: str
    name: str
    data_type: str
    length: int | None
    domain_name: str | None
    required: bool
    geometry_type: str | None
    source_row: int


@dataclass(frozen=True)
class FeatureDefinition:
    name: str
    attributes: tuple[AttributeDefinition, ...]


@dataclass(frozen=True)
class DomainDefinition:
    name: str
    structured: bool
    values: tuple[str, ...]


@dataclass(frozen=True)
class InformationModel:
    version: str
    features: tuple[FeatureDefinition, ...]
    domains: tuple[DomainDefinition, ...]