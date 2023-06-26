import logging
import natsort

from text_grid import *

# -----------------------------------------------------------------------------

class CrossCheckResult:
    bom_parst_missing_in_pnp: list[(str, str)]
    """Pairs part_designator:part_comment"""
    pnp_parst_missing_in_bom: list[(str, str)]
    """Pairs part_designator:part_comment"""
    parts_comment_mismatch: list[(str, str, str)]
    """Triplets part_designator:bom_comment:pnp_comment"""

    def __init__(self):
        self.bom_parst_missing_in_pnp = []
        self.pnp_parst_missing_in_bom = []
        self.parts_comment_mismatch = []

# -----------------------------------------------------------------------------

def __extract_grid(grid: ConfiguredTextGrid, grid_name: str) -> dict[str, str]:
    # TODO: case when the file does not contains a column titles, thus column indexes are used instead
    if type(grid.designator_col) is not str:
        raise ValueError(f"{grid_name} designator column id must be a string")
    if type(grid.comment_col) is not str:
        raise ValueError(f"{grid_name} comment column id must be a string")

    designator_col_idx = next(
        (
            i
            for i in range(grid.text_grid.ncols)
            if grid.text_grid.rows[grid.first_row][i] == grid.designator_col
        ),
        -1,
    )

    comment_col_idx = next(
        (
            i
            for i in range(grid.text_grid.ncols)
            if grid.text_grid.rows[grid.first_row][i] == grid.comment_col
        ),
        -1,
    )

    if designator_col_idx == -1:
        raise ValueError(f"{grid_name} designator column not found")
    if comment_col_idx == -1:
        raise ValueError(f"{grid_name} comment column not found")

    logging.debug(f"{grid_name} designator '{grid.designator_col}' found at column {designator_col_idx}")
    logging.debug(f"{grid_name} comment '{grid.comment_col}' found at column {comment_col_idx}")

    output = {}
    last_row = grid.text_grid.nrows if grid.last_row == -1 else grid.last_row
    if last_row > grid.text_grid.nrows:
        raise ValueError(f"{grid_name} last row > number of rows")

    for row in range(grid.first_row+1, last_row):
        dsgn = grid.text_grid.rows[row][designator_col_idx]
        cmnt = grid.text_grid.rows[row][comment_col_idx]
        dsgn = dsgn.split(',')
        # logging.debug(f"designators: '{dsgn}'")
        for d in dsgn:
            d = d.strip()
            output[d] = cmnt

    return output

def __extract_bom_parts(bom: ConfiguredTextGrid) -> dict[str, str]:
    return __extract_grid(bom, "BOM")

def __extract_pnp_parts(pnp: ConfiguredTextGrid) -> dict[str, str]:
    return __extract_grid(pnp, "PnP")

def __compare(bom_parts: dict[str, str], pnp_parts: dict[str, str]) -> CrossCheckResult:
    # sourcery skip: merge-nested-ifs
    result = CrossCheckResult()

    # check for items present in BOM, but missing in the PnP
    for designator in bom_parts:
        if designator not in pnp_parts:
            result.bom_parst_missing_in_pnp.append((designator, bom_parts[designator]))
    # sort naturally: https://pypi.org/project/natsort/
    result.bom_parst_missing_in_pnp = natsort.natsorted(result.bom_parst_missing_in_pnp)

    # check for items present in PnP, but missing in the BOM
    for designator in pnp_parts:
        if designator not in bom_parts:
            result.pnp_parst_missing_in_bom.append((designator, pnp_parts[designator]))
    result.pnp_parst_missing_in_bom = natsort.natsorted(result.pnp_parst_missing_in_bom)

    # check for comments mismatch
    for designator in bom_parts:
        if designator in pnp_parts:
            if bom_parts[designator] != pnp_parts[designator]:
                result.parts_comment_mismatch.append((designator, bom_parts[designator], pnp_parts[designator]))
    result.parts_comment_mismatch = natsort.natsorted(result.parts_comment_mismatch)

    #
    return result

# -----------------------------------------------------------------------------

def compare(bom: ConfiguredTextGrid, pnp: ConfiguredTextGrid) -> CrossCheckResult:
    """Performs BOM and PnP cross check"""

    if bom is None or bom.text_grid is None:
        raise ValueError("BOM data is missing")
    if pnp is None or pnp.text_grid is None:
        raise ValueError("PnP data is missing")

    bom_parts = __extract_bom_parts(bom)
    pnp_parts = __extract_pnp_parts(pnp)
    return __compare(bom_parts, pnp_parts)
