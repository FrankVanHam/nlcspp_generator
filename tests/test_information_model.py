from pathlib import Path

from nlcspp_generator.information_model import load_features


INFORMATION_MODEL = (
    Path(__file__).parents[2]
    / "training"
    / "input"
    / "InformatiemodelNetbeheerv12.1.xlsx"
)


def test_loads_canonical_features_and_properties() -> None:
    features = load_features(INFORMATION_MODEL)
    by_name = {feature.name: feature for feature in features}

    assert len(features) == 57
    assert len(by_name) == 57

    lskast = by_name["LSkast"]
    assert lskast.properties[0].name == "Handle"
    assert lskast.properties[1].name == "ID"
    assert lskast.properties[1].type_name == "xs:ID"
    assert lskast.properties[1].required
    assert lskast.properties[-1].name == "Geometry"
    assert lskast.properties[-1].type_name == "gml:SurfacePropertyType"

    project = by_name["AprojectReferentie"]
    assert [property_.name for property_ in project.properties[-3:]] == [
        "DatumTijdMutatie",
        "Tekeningtype",
        "Geometry",
    ]
    assert project.properties[-2].type_name == "Tekeningtype"
    assert project.properties[-1].type_name == "gml:SurfacePropertyType"


def test_maps_inline_text_and_scalar_types() -> None:
    features = {feature.name: feature for feature in load_features(INFORMATION_MODEL)}
    project = {property_.name: property_ for property_ in features["AprojectReferentie"].properties}

    assert project["Projectnummer"].type_name == "xs:string"
    assert project["Projectnummer"].max_length == 50
    assert project["Volgnummer"].type_name == "xs:integer"
    assert project["DatumTijdMutatie"].type_name == "xs:dateTime"