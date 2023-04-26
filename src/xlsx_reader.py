# https://linuxhint.com/read-excel-file-python/
# https://openpyxl.readthedocs.io/en/stable/tutorial.html

import openpyxl
from text_grid import TextGrid

def read_xlsx_sheet(path: str) -> TextGrid:
    """Reads entire sheet 0"""

    # Define variable to load the wookbook
    wookbook = openpyxl.load_workbook(path)
    sheet = wookbook.active

    tg = TextGrid()
    tg.nrows = sheet.max_row
    tg.ncols = sheet.max_column
    tg.rows = []

    # Iterate the loop to read the cell values
    for row in sheet.iter_rows(min_row=1, max_col=sheet.max_column, max_row=sheet.max_row, values_only=True):
        row_cells = []
        for cell in row:
            list.append(row_cells, cell)
        list.append(tg.rows, row)

    return tg
