import pytest
import sys
import os

# adding src path to search list
tests_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(os.path.dirname(tests_path), "src"))

# tested module
import xlsx_reader

# -----------------------------------------------------------------------------

def test_no_file():
    with pytest.raises(AssertionError):
        xlsx_reader.read_xlsx_sheet(None)

def test_bom():
    grid = xlsx_reader.read_xlsx_sheet(f"{tests_path}/assets/bom.xlsx")
    assert grid.nrows == 22-1 # skip lines with empty column A
    assert grid.ncols == 8
    assert grid.rows[-1][3] == "MURA-BLM18PG_KG-CHIP-2_V1"
    # check if empty cell was appended
    assert grid.rows[1][7] == ""
