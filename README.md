

# NLCS++ Generator

Generates the NLCS Netbeheer base XSD and a netbeheerder-specific choice-list
XSD from the source Excel workbooks.

## Install

```powershell
py -m pip install -e ".[test]"
```

## Generate

From this directory:

```powershell
py -m nlcspp_generator.cli ..\training\input generated
```

Stedin is selected by default. Other accepted values are `Enexis`, `Liander`,
and `Alliander`; `Alliander` is treated as an alias for `Liander`.

```powershell
py -m nlcspp_generator.cli ..\training\input generated --netbeheerder Stedin
```

The program identifies the information-model and domain workbooks by their
sheet structure, ignores Excel `~$` lock files, and infers the schema version
from the information-model workbook name.

## Verify

```powershell
py -m pytest -q
```

The integration tests compare both generated Stedin files byte-for-byte with
the training outputs, including the UTF-8 BOM, CRLF line endings, tabs, XML
escaping, and absence of a trailing newline.


