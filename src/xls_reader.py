# https://linuxhint.com/read-excel-file-python/
# https://xlrd.readthedocs.io/en/latest/

import xlrd
from text_grid import TextGrid

def read_xls_sheet(path: str) -> TextGrid:
    """Reads entire sheet 0"""
    book = xlrd.open_workbook(filename=path)
    sheet = book.sheet_by_index(0)

    tg = TextGrid()
    tg.nrows = sheet.nrows
    tg.ncols = sheet.ncols
    tg.rows = []

    # Iterate the loop to read the cell values
    for r in range(sheet.nrows):
        row_cells = []
        for c in range(tg.ncols):
            list.append(row_cells, sheet.cell_value(r, c))
        list.append(tg.rows, row_cells)

    return tg
