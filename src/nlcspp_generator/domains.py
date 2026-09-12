from __future__ import annotations

from dataclasses import dataclass
import locale
from pathlib import Path
from typing import Any

import xlrd

from .model import Domain, DomainDefinition, DomainValue


COMPANY_COLUMNS = {
    "Liander": "Alliander",
    "Stedin": "Stedin",
    "Enexis": "Enexis",
}
COMPANY_ALIASES = {"Alliander": "Liander"}


@dataclass(frozen=True)
class DomainCatalog:
    definitions: tuple[DomainDefinition, ...]
    values: tuple[DomainValue, ...]

    def select_open_domains(
        self,
        company: str,
        base_domain_order: tuple[str, ...],
    ) -> tuple[Domain, ...]:
        canonical_company = COMPANY_ALIASES.get(company, company)
        if canonical_company not in COMPANY_COLUMNS:
            supported = ", ".join(COMPANY_COLUMNS)
            raise ValueError(f"Unknown netbeheerder {company!r}; choose one of {supported}")

        definitions = {definition.name: definition for definition in self.definitions}
        selected_values: dict[str, set[str]] = {}
        for domain_value in self.values:
            if domain_value.deleted or canonical_company not in domain_value.companies:
                continue
            selected_values.setdefault(domain_value.domain_name, set()).add(domain_value.value)

        domains = []
        for domain_name in base_domain_order:
            definition = definitions.get(domain_name)
            if definition is None or definition.is_closed_in_base_schema:
                continue
            values = selected_values.get(domain_name)
            if values:
                domains.append(Domain(domain_name, _sort_like_excel(values)))
        return tuple(domains)

    def select_base_domains(self, domain_order: tuple[str, ...]) -> tuple[Domain, ...]:
        definitions = {definition.name: definition for definition in self.definitions}
        shared_values: dict[str, set[str]] = {}
        for domain_value in self.values:
            if (
                not domain_value.deleted
                and {"Stedin", "Enexis"}.issubset(domain_value.companies)
            ):
                shared_values.setdefault(domain_value.domain_name, set()).add(
                    domain_value.value
                )

        domains = []
        for domain_name in domain_order:
            definition = definitions.get(domain_name)
            if definition is None:
                raise ValueError(f"Domain {domain_name!r} is not defined in the domain catalog")
            values = (
                _sort_like_excel(shared_values.get(domain_name, set()))
                if definition.is_closed_in_base_schema
                else ()
            )
            domains.append(Domain(domain_name, values))
        return tuple(domains)


def load_domain_catalog(path: Path) -> DomainCatalog:
    workbook = xlrd.open_workbook(path, on_demand=True)
    try:
        definitions = _read_definitions(workbook.sheet_by_name("domains"))
        values = _read_values(workbook.sheet_by_name("domain_values"))
    finally:
        workbook.release_resources()
    return DomainCatalog(definitions=definitions, values=values)


def _read_definitions(sheet: xlrd.sheet.Sheet) -> tuple[DomainDefinition, ...]:
    headers = _headers(sheet)
    required = {"DOMAIN_NAME", "DOMAIN_DESCRIPTION", "Datatype_Code", "Structuur_XSD"}
    _require_headers(sheet.name, headers, required)

    definitions = []
    for row_index in range(1, sheet.nrows):
        name = _cell_text(sheet.cell_value(row_index, headers["DOMAIN_NAME"]))
        if not name:
            continue
        structure = _cell_text(sheet.cell_value(row_index, headers["Structuur_XSD"]))
        if structure not in {"Ja", "Nee"}:
            raise ValueError(
                f"Invalid Structuur_XSD value {structure!r} in {sheet.name}!A{row_index + 1}"
            )
        definitions.append(
            DomainDefinition(
                name=name,
                description=_cell_text(
                    sheet.cell_value(row_index, headers["DOMAIN_DESCRIPTION"])
                ),
                data_type=_cell_text(sheet.cell_value(row_index, headers["Datatype_Code"])),
                is_closed_in_base_schema=structure == "Ja",
            )
        )
    return tuple(definitions)


def _read_values(sheet: xlrd.sheet.Sheet) -> tuple[DomainValue, ...]:
    headers = _headers(sheet)
    required = {"DOMAIN_NAME", "DOMAIN_VALUE", "Verwijderd?", *COMPANY_COLUMNS.values()}
    _require_headers(sheet.name, headers, required)

    values = []
    for row_index in range(1, sheet.nrows):
        domain_name = _cell_text(sheet.cell_value(row_index, headers["DOMAIN_NAME"]))
        if not domain_name:
            continue
        companies = frozenset(
            canonical_name
            for canonical_name, column_name in COMPANY_COLUMNS.items()
            if _cell_text(sheet.cell_value(row_index, headers[column_name])).casefold() == "x"
        )
        values.append(
            DomainValue(
                domain_name=domain_name,
                value=_cell_text(sheet.cell_value(row_index, headers["DOMAIN_VALUE"])),
                deleted=(
                    _cell_text(sheet.cell_value(row_index, headers["Verwijderd?"])).casefold()
                    == "ja"
                ),
                companies=companies,
                source_row=row_index + 1,
            )
        )
    return tuple(values)


def _headers(sheet: xlrd.sheet.Sheet) -> dict[str, int]:
    return {
        _cell_text(sheet.cell_value(0, column_index)): column_index
        for column_index in range(sheet.ncols)
        if _cell_text(sheet.cell_value(0, column_index))
    }


def _require_headers(sheet_name: str, headers: dict[str, int], required: set[str]) -> None:
    missing = sorted(required - headers.keys())
    if missing:
        raise ValueError(f"Missing columns in sheet {sheet_name!r}: {', '.join(missing)}")


def _cell_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _sort_like_excel(values: set[str]) -> tuple[str, ...]:
    original_locale = locale.setlocale(locale.LC_COLLATE)
    for locale_name in ("Dutch_Netherlands.1252", "nl_NL.UTF-8", "nl_NL"):
        try:
            locale.setlocale(locale.LC_COLLATE, locale_name)
            transformed = {value: locale.strxfrm(value) for value in values}
            return tuple(sorted(values, key=transformed.__getitem__))
        except locale.Error:
            continue
        finally:
            locale.setlocale(locale.LC_COLLATE, original_locale)
    raise RuntimeError("A Dutch locale is required to reproduce Excel enumeration ordering")