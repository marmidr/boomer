# Changelog

See the description: https://keepachangelog.com/en/1.0.0/

## 0.3.0 - 2023-06-14

* Added
  * .ods reader for BOM and PnP
  * coloring differences in the report
  * support for separated TOP/BOTTON layer PnP files (PnP2)
* Changed
  * Separator option active only for .csv files
* Deprecated
* Removed
* Fixed
  * block the unintended BOM and PnP loading upon the project selection
  * file extension case ignored (recognizes both .xls and .XLS)

## 0.2.0 - 2023-05-30

* Added
  * BOM and PnP content cross checking and report generator
  * PnP can be imported also from the .xls(x) files
  * text searching for BOM and PnP
  * spaces-separated .csv reader
* Changed
  * comparison report: natural sorting of the parts: C2, C3, C10, C11
  * compatibility with the Python 3.9
* Deprecated
* Removed
* Fixed
  * clears all previews before opening project

## 0.1.0 - 2023-04-26

* Added
  * .xls and .xlsx reader
  * customtkinter GUI
  * .csv reader
  * project panel
  * BOM panel
  * PnP panel
* Changed
* Deprecated
* Removed
* Fixed