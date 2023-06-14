# BOM and PnP verifier

The purpose of this project is to help an electronic manufacturer in preparation of the new <abbr title="Printed Circuit Board">PCB</abbr> elements.

It reads the <abbr title="Bill Of Materials">BOM</abbr> and the accompanying <abbr title="Pick And Place">PnP</abbr> files, performing cross-checking to ensure if those files contents matches.

Project selection:
![sshot1](doc/sshot1.png)

BOM preview:
![sshot2](doc/sshot2.png)

PnP preview:
![sshot3](doc/sshot3.png)

Report:
![sshot4](doc/sshot4.png)

The following checks are performed:

* BOM contains element that is missing in the PnP file
* PnP contains reference to element that is not present in the BOM
* Part comment (value) differs between BOM and PnP files

## Supported formats

* [BOM](. "Bill Of Materials")
  * .xls
  * .xlsx
  * .ods
  * .csv
* [PnP](. "Pick And Place")
  * .xls
  * .xlsx
  * .ods
  * any other extension - considered as a CSV file

> NOTE
>
> If xls/xlsx/ods file contains several sheets, only the first one will be used.

## Prerequisites

### Python

[Python for Windows with addons](https://www.python.org/).
Remember to check these options:

* pip
* tcl\tk
* Add Python to environment variables

Minimum required version is **Python 3.9**.

### Libraries

To install required libraries, open the PowerShell and:

```ps1
# .xls reader, .xlsx reader, .ods reader, UI lib, natural sorting, HTML widgets,
pip install xlrd openpyxl odfpy customtkinter natsort tkhtmlview
```

## How to run

From PowerShell:

```ps1
python.exe src/app.py
```

## Trouble shooting

* *ModuleNotFoundError: No module named 'tkinter'*

  `tkinter` was not installed together with the Python -
  follow the instructions [here](https://bobbyhadz.com/blog/python-no-module-named-tkinter).
* *ERROR: Cannot load BOM: 'utf-8' codec can't decode byte*

  Only UTF-8 files are accepted; if the BOM or PnP file uses ANSI or WINDOWS encoding, use `Notepad++` or other editor to change the encoding to UTF-8
*
