# BOM and PnP verifier

The purpose of this project is to help an electronic manufacturer in preparation of the new <abbr title="Printed Circuit Board">PCB</abbr> elements.

It reads the <abbr title="Bill Of Materials">BOM</abbr> and the accompanying <abbr title="Pick And Place">PnP</abbr> files, performing cross-checking to ensure if those files contents matches.

The following checks are performed:

* BOM contains some element that is missing in the PnP file
* PnP contains reference to element that is not present in the BOM

## Supported formats

* [BOM](. "Bill Of Materials")
  * .xls
  * .xlsx
  * .csv
* [PnP](. "Pick And Place")
  * .csv

## Prerequisites

[Python for Windows with addons (pip, tkinter)](https://www.python.org/)
Remember to check "Add Python to PATH".

Open PowerShell and:

```ps1
# .xls reader, .xlsx reader, UI lib
pip install xlrd openpyxl customtkinter
```

## Examples

TBD
