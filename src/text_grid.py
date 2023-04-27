
class TextGrid:
    """Represents data read from the XLS/XLSX/CSV"""

    nrows: int
    ncols: int
    rows: list[list[str]]

    def __init__(self):
        self.nrows = 0
        self.ncols = 0
        self.rows = []

class TextGridConfig:
    """Determines data range to be imported"""
    columns: list[str]
    first_row: int
