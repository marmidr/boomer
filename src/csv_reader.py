from text_grid import TextGrid
import csv
import logging

def read_csv(path: str, delim: str) -> TextGrid:
    """
    Reads entire CSV/text file.

    Delim may be: ' '  ','  ';'  '\t'  '*fw'  '*re'
    """

    logging.info(f"Reading file '{path}'")

    tg = TextGrid()
    max_cols = 0

    with open(path, 'r', encoding="utf-8") as f:
        if delim == "*fw":
            # TODO: add reader for fixed-width
            raise ValueError("delimiter *fw not yet supported")
        elif delim == "*re":
            # TODO: add reader for reg-ex
            raise ValueError("delimiter *re not yet supported")
        else:
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
