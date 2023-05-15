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
        if delim == "*sp":
            rows = f.read().splitlines()
            for row in rows:
                # split row by any number of following whitespaces
                row_cells = row.split()
                max_cols = max(max_cols, len(row_cells))
                # ignore rows with empty cell 'A'
                if len(row_cells) > 0 and row_cells[0] != "":
                    row_cells_processed = []

                    # merge quoted cells into single one,
                    # like this: "5k1 5% 0603"
                    quoted_cell = ""
                    for cell in row_cells:
                        if cell.startswith('"'):
                            quoted_cell = cell
                        elif len(quoted_cell) > 0:
                            quoted_cell += ' '
                            quoted_cell += cell
                            if cell.endswith('"'):
                                # drop the quotes
                                quoted_cell = quoted_cell[1:-1]
                                row_cells_processed.append(quoted_cell)
                                quoted_cell = ""
                        else:
                            row_cells_processed.append(cell)

                    tg.rows.append(row_cells_processed)

        elif delim == "*fw":
            # TODO: add reader for fixed-width
            raise ValueError("delimiter *fw not yet implemented")
        elif delim == "*re":
            # TODO: add reader for reg-ex
            raise ValueError("delimiter *re not yet implemented")
        else:
            reader = csv.reader(f, delimiter=delim)
            for row in reader:
                # ignore rows with empty cell 'A'
                if len(row) > 0 and row[0] != "":
                    row_cells = []
                    for cell in row:
                        row_cells.append(cell.strip())

                    max_cols = max(max_cols, len(row_cells))
                    tg.rows.append(row_cells)

    tg.nrows = len(tg.rows)
    tg.ncols = max_cols

    # ensure every row has the same number of columns
    for row in tg.rows:
        cols_to_add = tg.ncols - len(row)
        while cols_to_add > 0:
            row.append("")
            cols_to_add -= 1

    return tg
