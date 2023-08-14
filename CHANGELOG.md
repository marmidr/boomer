# Changelog

See the [keepachangelog.com description](https://keepachangelog.com/en/1.0.0/).

## 0.7.2 - 2023-08-14

* Added
* Changed
  * UI improvements
* Deprecated
* Removed
* Fixed
  * refactoring: removed static class members

## 0.7.1 - 2023-07-17

* Added
* Changed
  * search string highlight color: aqua -> yellow
* Deprecated
* Removed
* Fixed
  * xls/xlsx - prevent formatting of digits-only cells, like '100', as float numbers '100.0'
  * xls/xlsx - cells containing multiple rows are transformed into single-line with '⏎' character

## 0.7.0 - 2023-07-15

* Added
  * BOM and PnP column can be selected by index, if file has no column headers
* Changed
* Deprecated
* Removed
* Fixed

## 0.6.0 - 2023-07-10

* Added
  * once the BOM and PnP files are loaded successfully, every time you click the `Cross-check the files` will reload these files before comparison
  * item comment comparison: text diff library used to detect differences char-by-char
* Changed
* Deprecated
* Removed
* Fixed

## 0.5.1 - 2023-06-28

* Added
  * report has a date/time information pointing on when it was generated
  * for every type of input file, not just CSV, ensure that each row has the same number of columns
  * unit tests
* Changed
  * examples moved to `examples` folder
  * html files not listed as potential PnP files
* Deprecated
* Removed
* Fixed
  * removing many nonexisting projects on startup
  * changing the profile does not reload the files

## 0.5.0 - 2023-06-27

* Added
  * generated report is automatically saved as .html file in the project directory
  * on startup, automatically deletes nonexisting projects from the configuration file
* Changed
* Deprecated
* Removed
* Fixed
  * `Copy HTML` button - fixed library attached, HTML text recognized by GMail editor

## 0.4.1 - 2023-06-26

* Added
  * if current shared profile was changed and user wants to save it, message box is displayed asking whether to overwrite
* Changed
* Deprecated
* Removed
* Fixed
  * clears all of the previews when adding a new project (Browse...)
  * fix error causing results wrom previous project being added to the current project cross-check results

## 0.4.0 - 2023-06-19

* Added
  * HTML widget for formatted report
  * copy to clipboard as HTML
* Changed
  * Project and PnP lists are now sorted
* Deprecated
* Removed
* Fixed

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
