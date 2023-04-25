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

* msys (Windows)\
[Msys2 installer](https://msys2.org/)
* Python and it's modules

```sh
# python3 + pip
pacman -S python3
pacman -S python-pip
# .xls reader
pip install xlrd
# .xlsx  reader
pip install openpyxl
```

## Examples

TBD
