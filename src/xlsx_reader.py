# https://linuxhint.com/read-excel-file-python/
# https://openpyxl.readthedocs.io/en/stable/tutorial.html

import openpyxl
from text_grid import TextGrid
import logging

def read_xlsx_sheet(path: str) -> TextGrid:
    """Reads entire sheet 0"""

    logging.info(f"Reading file '{path}'")
    # Define variable to load the wookbook
    wookbook = openpyxl.load_workbook(path)
    sheet = wookbook.active

    tg = TextGrid()

    # Iterate the loop to read the cell values
    for row in sheet.iter_rows(min_row=1, max_col=sheet.max_column, max_row=sheet.max_row, values_only=True):
        row_cells = []
        for cell in row:
            list.append(row_cells, cell)

        # ignore rows with empty cell 'A'
        if len(row_cells) > 0 and not row_cells[0] is None and row_cells[0] != "":
            list.append(tg.rows, row_cells)

    tg.nrows = len(tg.rows)
    tg.ncols = sheet.max_column
    return tg
