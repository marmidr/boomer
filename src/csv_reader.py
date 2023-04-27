from text_grid import TextGrid
import csv
import logging

# class Delim:
#     SPACE=1
#     TAB=2
#     CONSTWIDTH=3
#     COLON=4
#     SEMICOLON=5

def read_csv(path: str, delim: str) -> TextGrid:
    """Reads entire CSV file"""

    logging.info(f"Reading file '{path}'")

    tg = TextGrid()
    max_cols = 0

    with open(path, 'r', encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=delim)
        for row in reader:
            # ignore rows with empty cell 'A'
            if len(row) > 0 and row[0] != "":
                row_cells = []
                for cell in row:
                    list.append(row_cells, cell.strip())

                if len(row_cells) > max_cols: max_cols = len(row_cells)
                list.append(tg.rows, row_cells)

    tg.nrows = len(tg.rows)
    tg.ncols = max_cols

    # ensure every row has the same number of columns
    for row in tg.rows:
        cols_to_add = tg.ncols - len(row)
        while cols_to_add > 0:
            list.append(row, "")
            cols_to_add -= 1

    return tg
