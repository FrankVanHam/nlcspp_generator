from pathlib import Path

from nlcspp_generator.cli import main
from nlcspp_generator.workbook import read_information_model
from nlcspp_generator.xsd_writer import render_xsd


TRAINING = Path(__file__).parents[2] / "training"
MODEL = TRAINING / "input" / "InformatiemodelNetbeheerv12.1.xlsx"
DOMAINS = TRAINING / "input" / "domains_InformatiemodelNetbeheerV12.1.xls"
REFERENCE = TRAINING / "output" / "NLCS_Netbeheer.xsd"


def test_training_model_shape() -> None:
    model = read_information_model(MODEL, DOMAINS)
    assert model.version == "12.1"
    assert len(model.features) == 57
    assert len(model.domains) == 122
    assert sum(len(domain.values) for domain in model.domains) == 167


def test_reference_bytes() -> None:
    generated = render_xsd(read_information_model(MODEL, DOMAINS))
    assert generated == REFERENCE.read_bytes()


def test_cli_auto_discovers_domains(tmp_path: Path) -> None:
    output = tmp_path / "generated.xsd"
    assert main([str(MODEL), str(output)]) == 0
    assert output.read_bytes() == REFERENCE.read_bytes()