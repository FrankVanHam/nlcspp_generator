from pathlib import Path

from nlcspp_generator.generator import generate


WORKSPACE = Path(__file__).parents[2]
INPUT = WORKSPACE / "training" / "input"
GOLDEN = WORKSPACE / "training" / "output"


def test_generates_both_stedin_files_byte_for_byte(tmp_path: Path) -> None:
    generated = generate(INPUT, tmp_path)

    assert generated.base_schema.read_bytes() == (GOLDEN / "NLCS_Netbeheer.xsd").read_bytes()
    assert generated.selection_schema.read_bytes() == (
        GOLDEN / "NLCS_NetbeheerStedinV12.1Import_Keuzelijst.xsd"
    ).read_bytes()
    assert {path.name for path in tmp_path.iterdir()} == {
        "NLCS_Netbeheer.xsd",
        "NLCS_NetbeheerStedinV12.1Import_Keuzelijst.xsd",
    }