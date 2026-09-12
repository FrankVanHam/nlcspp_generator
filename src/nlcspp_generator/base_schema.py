from __future__ import annotations

from .model import Domain, Feature, Property
from .serializer import encode_document, escape_attribute


def render_base_schema(
    project_feature: Feature,
    features: tuple[Feature, ...],
    domains: tuple[Domain, ...],
    version: str,
) -> bytes:
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<xs:schema xmlns="NS_NLCSnetbeheer" xmlns:gml="http://www.opengis.net/gml/3.2" '
        'xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" '
        'xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" attributeFormDefault="unqualified" '
        'elementFormDefault="qualified" targetNamespace="NS_NLCSnetbeheer" '
        f'version="{escape_attribute(version)}" xmlns:xs="http://www.w3.org/2001/XMLSchema">',
        '\t<xs:import schemaLocation="http://schemas.opengis.net/gml/3.2.1/gml.xsd" namespace="http://www.opengis.net/gml/3.2" />',
        '\t<xs:element name="NLCSnetbeheer" substitutionGroup="gml:AbstractFeatureCollection">',
        '\t\t<xs:complexType>',
        '\t\t\t<xs:complexContent mixed="false">',
        '\t\t\t\t<xs:extension base="gml:AbstractFeatureCollectionType">',
        '\t\t\t\t\t<xs:sequence>',
    ]
    _append_feature(lines, project_feature, 6, project=True)
    lines.append('\t\t\t\t\t\t<xs:choice minOccurs="0" maxOccurs="unbounded">')
    for feature in features:
        _append_feature(lines, feature, 7, project=False)
    lines.extend(
        (
            "\t\t\t\t\t\t</xs:choice>",
            "\t\t\t\t\t</xs:sequence>",
            '\t\t\t\t\t<xs:attribute name="VersieNummer" type="xs:string" />',
            "\t\t\t\t</xs:extension>",
            "\t\t\t</xs:complexContent>",
            "\t\t</xs:complexType>",
            "\t</xs:element>",
        )
    )
    for domain in domains:
        _append_domain(lines, domain)
    lines.append("</xs:schema>")
    return encode_document(lines)


def _append_feature(
    lines: list[str], feature: Feature, indent: int, *, project: bool
) -> None:
    tabs = "\t" * indent
    occurrence = 'minOccurs="1" maxOccurs="1" ' if project else 'maxOccurs="unbounded" '
    lines.extend(
        (
            f'{tabs}<xs:element {occurrence}name="{escape_attribute(feature.name)}">',
            f"{tabs}\t<xs:complexType>",
            f'{tabs}\t\t<xs:complexContent mixed="false">',
            f'{tabs}\t\t\t<xs:extension base="gml:AbstractFeatureType">',
            f"{tabs}\t\t\t\t<xs:sequence>",
        )
    )
    for property_ in feature.properties:
        _append_property(lines, property_, indent + 5)
    lines.extend(
        (
            f"{tabs}\t\t\t\t</xs:sequence>",
            f"{tabs}\t\t\t</xs:extension>",
            f"{tabs}\t\t</xs:complexContent>",
            f"{tabs}\t</xs:complexType>",
            f"{tabs}</xs:element>",
        )
    )


def _append_property(lines: list[str], property_: Property, indent: int) -> None:
    tabs = "\t" * indent
    min_occurs = "1" if property_.required else "0"
    name = escape_attribute(property_.name)
    if property_.max_length is None:
        lines.append(
            f'{tabs}<xs:element minOccurs="{min_occurs}" maxOccurs="1" '
            f'name="{name}" type="{escape_attribute(property_.type_name)}" />'
        )
        return
    lines.extend(
        (
            f'{tabs}<xs:element minOccurs="{min_occurs}" maxOccurs="1" name="{name}">',
            f"{tabs}\t<xs:simpleType>",
            f'{tabs}\t\t<xs:restriction base="xs:string">',
            f'{tabs}\t\t\t<xs:maxLength value="{property_.max_length}" />',
            f"{tabs}\t\t</xs:restriction>",
            f"{tabs}\t</xs:simpleType>",
            f"{tabs}</xs:element>",
        )
    )


def _append_domain(lines: list[str], domain: Domain) -> None:
    name = escape_attribute(domain.name)
    lines.extend(
        (
            f'\t<xs:simpleType name="{name}">',
            '\t\t<xs:restriction base="xs:string">',
        )
    )
    if domain.values:
        lines.extend(
            f'\t\t\t<xs:enumeration value="{escape_attribute(value)}" />'
            for value in domain.values
        )
    else:
        lines.append('\t\t\t<xs:maxLength value="255" />')
    lines.extend(("\t\t</xs:restriction>", "\t</xs:simpleType>"))