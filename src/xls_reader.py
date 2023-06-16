# https://linuxhint.com/read-excel-file-python/
# https://xlrd.readthedocs.io/en/latest/

import xlrd
import logging

from text_grid import TextGrid

# -----------------------------------------------------------------------------

def read_xls_sheet(path: str) -> TextGrid:
    """
    Reads entire sheet 0
    """

    logging.info(f"Reading file '{path}'")
    book = xlrd.open_workbook(filename=path)
    sheet = book.sheet_by_index(0)
    tg = TextGrid()

    # Iterate the loop to read the cell values
    for r in range(sheet.nrows):
        row_cells = []
        for c in range(sheet.ncols):
            cell = sheet.cell_value(r, c)
            if cell is None:
                cell = ""
            elif type(cell) is float or type(cell) is int:
                cell = repr(cell)
            row_cells.append(cell.strip())

        # ignore rows with empty cell 'A'
        if row_cells and row_cells[0] != "":
            tg.rows.append(row_cells)

    tg.nrows = len(tg.rows)
    tg.ncols = sheet.ncols
    return tg
