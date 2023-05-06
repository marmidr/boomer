
class TextGrid:
    """Represents data read from the XLS/XLSX/CSV"""

    nrows: int
    ncols: int
    rows: list[list[str]]

    def __init__(self):
        self.nrows = 0
        self.ncols = 0
        self.rows = []

    @staticmethod
    def format_cell(cell) -> str:
        # https://stackoverflow.com/questions/2184955/test-if-a-variable-is-a-list-or-tuple
        if cell is None:
            cell = "---"
        elif type(cell) is str:
            pass
        else:
            cell = repr(cell)
        return cell

    def get_columns_width(self, first_row: int) -> list[int]:
        col_max_w = [0 for _ in range(self.ncols)]
        for r, row in enumerate(self.rows):
            if r >= first_row:
                for c, cell in enumerate(row):
                    cell = self.format_cell(cell)
                    max_w = col_max_w[c]
                    cell_w = len(cell)
                    if cell_w > max_w:
                        col_max_w[c] = cell_w
        return col_max_w

    def format_grid(self, first_row: int) -> str:
        columns_width = self.get_columns_width(first_row)
        grid_formatted = ""
        for r, row in enumerate(self.rows):
            if r >= first_row:
                row_formatted = "{:0>3} | ".format(r+1)
                for c, cell in enumerate(row):
                    cell = self.format_cell(cell)
                    to_fill = columns_width[c] - len(cell)
                    fill = " " * to_fill if to_fill > 0 else ""
                    cell = cell + fill + " | "
                    row_formatted = row_formatted + cell
                grid_formatted = grid_formatted + row_formatted + "\n"
        return grid_formatted

class TextGridConfig:
    """Determines data range to be imported"""
    columns: list[str]
    first_row: int
