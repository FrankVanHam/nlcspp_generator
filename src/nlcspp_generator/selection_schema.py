from __future__ import annotations

from .model import Domain
from .serializer import encode_document, escape_attribute


def render_selection_schema(
    domains: tuple[Domain, ...],
    base_schema_name: str = "NLCS_Netbeheer.xsd",
    version: str = "12.1",
) -> bytes:
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<xs:schema xmlns="NS_NLCSnetbeheer" attributeFormDefault="unqualified" '
        'elementFormDefault="qualified" targetNamespace="NS_NLCSnetbeheer" '
        f'version="{escape_attribute(version)}" '
        'xmlns:xs="http://www.w3.org/2001/XMLSchema">',
        f'\t<xs:redefine schemaLocation="{escape_attribute(base_schema_name)}">',
    ]
    for domain in domains:
        name = escape_attribute(domain.name)
        lines.extend(
            (
                f'\t\t<xs:simpleType name="{name}">',
                f'\t\t\t<xs:restriction base="{name}">',
            )
        )
        lines.extend(
            f'\t\t\t\t<xs:enumeration value="{escape_attribute(value)}" />'
            for value in domain.values
        )
        lines.extend(("\t\t\t</xs:restriction>", "\t\t</xs:simpleType>"))
    lines.extend(("\t</xs:redefine>", "</xs:schema>"))
    return encode_document(lines)