
class TextGrid:
    """Represents data read from the XLS/SLSX"""
    nrows: int
    ncols: int
    rows: list[list[str]]

class TextGridConfig:
    """Determines which data to be imported"""
    columns: list[str]
    first_row: int
