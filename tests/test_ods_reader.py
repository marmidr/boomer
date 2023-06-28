import pytest
import sys
import os

# adding src path to search list
tests_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(os.path.dirname(tests_path), "src"))

# tested module
import ods_reader

# -----------------------------------------------------------------------------

def test_no_file():
    with pytest.raises(AssertionError):
        ods_reader.read_ods_sheet(None)

def test_bom():
    grid = ods_reader.read_ods_sheet(f"{tests_path}/assets/bom.ods")
    assert grid.nrows == 24-1
    assert grid.ncols == 15
    assert grid.rows[-3][2] == "100n"
    # check if empty cells were appended
    assert grid.rows[0][14] == ""
