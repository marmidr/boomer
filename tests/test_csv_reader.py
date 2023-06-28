import pytest
import sys
import os

# adding src path to search list
tests_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(os.path.dirname(tests_path), "src"))

# tested module
import csv_reader

# -----------------------------------------------------------------------------

def test_no_file():
    with pytest.raises(AssertionError):
        csv_reader.read_csv(None, " ")

def test_no_separator():
    with pytest.raises(AssertionError):
        csv_reader.read_csv(".", None)

def test_csv_comma():
    # using a full asset path makes possible to run the tests from the VSCode
    grid = csv_reader.read_csv(f"{tests_path}/assets/comma.csv", ",")
    assert grid.nrows == 12-3 # empty rows skipped
    assert grid.ncols == 13
    assert grid.rows[-3][0] == "Designator"
    # check if empty cells were appended
    assert grid.rows[0][12] == ""

def test_csv_spaces():
    grid = csv_reader.read_csv(f"{tests_path}/assets/spaces.csv", "*sp")
    assert grid.nrows == 11-1
    assert grid.ncols == 8
    assert grid.rows[-6][0] == "Fid6"

def test_csv_tabs():
    grid = csv_reader.read_csv(f"{tests_path}/assets/tabs.csv", "\t")
    assert grid.nrows == 21-2 # skip empty and lines that begins with '___'
    assert grid.ncols == 10
    assert grid.rows[-2][2] == "SOT23_S4C"
