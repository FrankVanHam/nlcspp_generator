from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Domain:
    name: str
    values: tuple[str, ...]


@dataclass(frozen=True)
class DomainDefinition:
    name: str
    description: str
    data_type: str
    is_closed_in_base_schema: bool


@dataclass(frozen=True)
class DomainValue:
    domain_name: str
    value: str
    deleted: bool
    companies: frozenset[str]
    source_row: int


@dataclass(frozen=True)
class Property:
    name: str
    type_name: str
    required: bool
    max_length: int | None = None
    source_row: int | None = None


@dataclass(frozen=True)
class Feature:
    name: str
    properties: tuple[Property, ...]