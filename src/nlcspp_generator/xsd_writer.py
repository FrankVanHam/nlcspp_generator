from __future__ import annotations

from .model import AttributeDefinition, FeatureDefinition, InformationModel


IDREF_ATTRIBUTES = {
    ("AmantelbuisInhoud", "MantelbuisID"),
    ("AmantelbuisInhoud", "InhoudID"),
    ("AbestandBijlage", "AssetObjectID"),
    ("Averplaatsing", "AssetObjectID"),
}


def _escape(value: object) -> str:
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _xsd_type(attribute: AttributeDefinition) -> str | None:
    key = (attribute.feature_name, attribute.name)
    if attribute.name == "ID" and attribute.feature_name != "GtStuk":
        return "xs:ID"
    if key in IDREF_ATTRIBUTES:
        return "xs:IDREF"
    if attribute.domain_name:
        return attribute.domain_name
    if attribute.data_type == "DATE ONLY":
        return "xs:date"
    if attribute.data_type == "DATE":
        return "xs:dateTime"
    if attribute.data_type == "LONG":
        return "xs:integer"
    if attribute.data_type in {"DOUBLE", "FLOAT"}:
        return "xs:decimal"
    if attribute.data_type == "SHAPE":
        geometry = (attribute.geometry_type or "").casefold()
        if attribute.feature_name == "Averplaatsing" or geometry.startswith("lijn"):
            return "gml:CurvePropertyType"
        if geometry.startswith("punt"):
            return "gml:PointPropertyType"
        if geometry.startswith("vlak"):
            return "gml:SurfacePropertyType"
        raise ValueError(f"Unsupported geometry for {attribute.feature_name}.{attribute.name}")
    if attribute.data_type == "TEXT":
        return None
    raise ValueError(f"Unsupported datatype {attribute.data_type!r} at row {attribute.source_row}")


class XsdWriter:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def line(self, depth: int, text: str) -> None:
        self.lines.append("\t" * depth + text)

    def attribute(self, depth: int, attribute: AttributeDefinition) -> None:
        minimum = "1" if attribute.required else "0"
        xsd_type = _xsd_type(attribute)
        prefix = (f'<xs:element minOccurs="{minimum}" maxOccurs="1" '
                  f'name="{_escape(attribute.name)}"')
        if xsd_type:
            self.line(depth, f'{prefix} type="{_escape(xsd_type)}" />')
            return
        if attribute.length is None:
            raise ValueError(f"Missing text length at row {attribute.source_row}")
        self.line(depth, prefix + ">")
        self.line(depth + 1, "<xs:simpleType>")
        self.line(depth + 2, '<xs:restriction base="xs:string">')
        self.line(depth + 3, f'<xs:maxLength value="{attribute.length}" />')
        self.line(depth + 2, "</xs:restriction>")
        self.line(depth + 1, "</xs:simpleType>")
        self.line(depth, "</xs:element>")

    def feature(self, depth: int, feature: FeatureDefinition, project: bool = False) -> None:
        if project:
            self.line(depth, f'<xs:element minOccurs="1" maxOccurs="1" name="{feature.name}">')
        else:
            self.line(depth, f'<xs:element maxOccurs="unbounded" name="{feature.name}">')
        self.line(depth + 1, "<xs:complexType>")
        self.line(depth + 2, '<xs:complexContent mixed="false">')
        self.line(depth + 3, '<xs:extension base="gml:AbstractFeatureType">')
        self.line(depth + 4, "<xs:sequence>")
        self.line(depth + 5, '<xs:element minOccurs="0" maxOccurs="1" name="Handle" type="xs:string" />')
        for attribute in feature.attributes:
            self.attribute(depth + 5, attribute)
        self.line(depth + 4, "</xs:sequence>")
        self.line(depth + 3, "</xs:extension>")
        self.line(depth + 2, "</xs:complexContent>")
        self.line(depth + 1, "</xs:complexType>")
        self.line(depth, "</xs:element>")

    def render(self, model: InformationModel) -> bytes:
        features = {feature.name: feature for feature in model.features}
        project = features["AprojectReferentie"]
        choices = [feature for feature in model.features if feature.name != project.name]
        self.line(0, '<?xml version="1.0" encoding="utf-8"?>')
        self.line(0, '<xs:schema xmlns="NS_NLCSnetbeheer" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" attributeFormDefault="unqualified" elementFormDefault="qualified" targetNamespace="NS_NLCSnetbeheer" version="' + _escape(model.version) + '" xmlns:xs="http://www.w3.org/2001/XMLSchema">')
        self.line(1, '<xs:import schemaLocation="http://schemas.opengis.net/gml/3.2.1/gml.xsd" namespace="http://www.opengis.net/gml/3.2" />')
        self.line(1, '<xs:element name="NLCSnetbeheer" substitutionGroup="gml:AbstractFeatureCollection">')
        self.line(2, "<xs:complexType>")
        self.line(3, '<xs:complexContent mixed="false">')
        self.line(4, '<xs:extension base="gml:AbstractFeatureCollectionType">')
        self.line(5, "<xs:sequence>")
        self.feature(6, project, project=True)
        self.line(6, '<xs:choice minOccurs="0" maxOccurs="unbounded">')
        for feature in choices:
            self.feature(7, feature)
        self.line(6, "</xs:choice>")
        self.line(5, "</xs:sequence>")
        self.line(5, '<xs:attribute name="VersieNummer" type="xs:string" />')
        self.line(4, "</xs:extension>")
        self.line(3, "</xs:complexContent>")
        self.line(2, "</xs:complexType>")
        self.line(1, "</xs:element>")
        for domain in model.domains:
            self.line(1, f'<xs:simpleType name="{_escape(domain.name)}">')
            self.line(2, '<xs:restriction base="xs:string">')
            if domain.structured:
                for value in domain.values:
                    self.line(3, f'<xs:enumeration value="{_escape(value)}" />')
            else:
                self.line(3, '<xs:maxLength value="255" />')
            self.line(2, "</xs:restriction>")
            self.line(1, "</xs:simpleType>")
        self.line(0, "</xs:schema>")
        return b"\xef\xbb\xbf" + "\r\n".join(self.lines).encode("utf-8")


def render_xsd(model: InformationModel) -> bytes:
    return XsdWriter().render(model)