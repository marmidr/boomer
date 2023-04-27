# https://linuxhint.com/read-excel-file-python/
# https://xlrd.readthedocs.io/en/latest/

import xlrd
from text_grid import TextGrid
import logging

def read_xls_sheet(path: str) -> TextGrid:
    """Reads entire sheet 0"""

    logging.info(f"Reading file '{path}'")
    book = xlrd.open_workbook(filename=path)
    sheet = book.sheet_by_index(0)

    tg = TextGrid()

    # Iterate the loop to read the cell values
    for r in range(sheet.nrows):
        row_cells = []
        for c in range(sheet.ncols):
            list.append(row_cells, sheet.cell_value(r, c))
        # ignore rows with empty cell 'A'
        if len(row_cells) > 0 and not row_cells[0] is None and row_cells[0] != "":
            list.append(tg.rows, row_cells)

    tg.nrows = len(tg.rows)
    tg.ncols = sheet.ncols
    return tg
