import pytest
import sys
import os

# adding src path to search list
tests_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(os.path.dirname(tests_path), "src"))

# tested module
from text_grid import *

# -----------------------------------------------------------------------------

def test_default():
    tg = TextGrid()
    assert tg.nrows == 0
    assert tg.ncols == 0
    assert type(tg.rows) is list
    assert len(tg.rows) == 0

def test_full_features():
    expected_lines = (
        "002 | ID     | Val            | Comment  | ",
        "003 | #      |                |          | ",
        "004 | R1     | 15k            | resistor | ",
        "005 | R3     | 1.2            |          | ",
        "006 | Jumper |                |          | ",
        "007 | U1     | STM32F12345678 | 4321     | "
    )

    tg = TextGrid()
    tg.rows.append(["List of materials"])
    tg.rows.append(["ID", "Val", "Comment"])
    tg.rows.append(["#", None, ""])
    tg.rows.append(["R1", "15k", "resistor"])
    tg.rows.append(["R3", 1.2, None])
    tg.rows.append(["Jumper", ""])
    tg.rows.append(["U1", "STM32F12345678", 4321])
    tg.nrows = len(tg.rows)
    tg.ncols = 3
    tg.align_number_of_columns()
    assert tg.rows[0][1] == ""
    assert tg.rows[0][2] == ""
    formatted = tg.format_grid(1)
    # print()
    # print(txt)
    actual_lines = formatted.splitlines()
    for (act, exp) in zip(actual_lines, expected_lines):
        assert act == exp

