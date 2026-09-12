from pathlib import Path

from nlcspp_generator.discovery import discover_workbooks, inventory_directory


FIXTURE_INPUT = Path(__file__).parents[2] / "training" / "input"


def test_discovers_and_reads_training_workbooks() -> None:
    paths = discover_workbooks(FIXTURE_INPUT)

    assert len(paths) == 4
    assert all(not path.name.startswith("~$") for path in paths)
    assert {path.suffix.casefold() for path in paths} == {".xls", ".xlsx"}

    inventories = inventory_directory(FIXTURE_INPUT)
    assert len(inventories) == 4
    assert all(inventory.sheets for inventory in inventories)
    assert all(
        sheet.row_count > 0 and sheet.column_count > 0
        for inventory in inventories
        for sheet in inventory.sheets
    )