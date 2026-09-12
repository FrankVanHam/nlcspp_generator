

# NLCS++ Generator

Generates the NLCS Netbeheer base XSD and a netbeheerder-specific choice-list
XSD from the source Excel workbooks.

## Input
Create a directory with 2 input files:
domains_InformatiemodelNetbeheerV12.1.xls
InformatiemodelNetbeheerv12.1.xlsx
In this example the value "12.1" is the version. This value can be changed by replacing it with another number like 13.0


## Generate

From this directory:

```powershell
py -m nlcspp_generator.cli ..\training\input generated
```

Stedin is selected by default. Other accepted values are `Enexis` and `Liander`.

```powershell
py -m nlcspp_generator.cli ..\training\input generated --netbeheerder Stedin
```

The program identifies the information-model and domain workbooks by their
sheet structure, ignores Excel `~$` lock files, and infers the schema version
from the information-model workbook name.

## Output
The output will be:
NLCS_Netbeheer.xsd
NLCS_NetbeheerStedinV12.1Import_Keuzelijst.xsd

Note that the version number is included in the keuzelijst XSD, but not in the main XSD.

## Verify

```powershell
py -m pytest -q
```

The integration tests compare both generated Stedin files byte-for-byte with
the training outputs, including the UTF-8 BOM, CRLF line endings, tabs, XML
escaping, and absence of a trailing newline.


