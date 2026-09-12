# NLCS++ Generator

Generate a deterministic NLCS++ XSD from the Netbeheer information-model workbooks.

## Inputs

The generator uses two source workbooks:

- `InformatiemodelNetbeheer*.xlsx` supplies objects and attributes from columns `AV:BF` of the `Informatiemodel` worksheet.
- `domains_*.xls` supplies domain definitions and values from the `domains` and `domain_values` worksheets.

When exactly one `domains_*.xls` file is beside the model workbook, it is discovered automatically. Otherwise, pass it explicitly with `--domains`.

## Installation

```powershell
python -m pip install -e ".[test]"
```

## Usage

```powershell
nlcspp-generate path\to\InformatiemodelNetbeheerv12.1.xlsx output\NLCS_Netbeheer.xsd
```

Explicit domain workbook and version:

```powershell
nlcspp-generate model.xlsx output.xsd --domains domains.xls --version 12.1
```

The output format is intentionally fixed: UTF-8 with BOM, CRLF line endings, tabs for indentation, stable attribute ordering, and no final newline.

## Verification

```powershell
python -m pytest
```

The golden test generates the v12.1 schema and compares it byte-for-byte with the reference file in `training/output`.