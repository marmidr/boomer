import logging
import natsort
import math

from text_grid import *

# -----------------------------------------------------------------------------

class CrossCheckResult:
    def __init__(self):
        self.bom_parst_missing_in_pnp: list[(str, str)] = []
        """Pairs (part_designator : part_comment)"""

        self.pnp_parst_missing_in_bom: list[(str, str)] = []
        """Pairs (part_designator : part_comment)"""

        self.parts_comment_mismatch: list[(str, str, str)] = []
        """Triplets (part_designator : bom_comment : pnp_comment)"""

        self.parts_coord_conflicts: list[(str, str, float)] = []
        """Triplets (part1_designator : part2_designator : distance_mm)"""

# -----------------------------------------------------------------------------

def __extract_grid(grid: ConfiguredTextGrid, grid_name: str) -> dict[str, (str, str, str)]:
    """Returns dictionary: {Designator : (Comment, Coord-X, Coord-Y)}"""
    if grid.has_column_headers:
        if type(grid.designator_col) is not str:
            raise ValueError(f"{grid_name} designator column id must be a string")
        if type(grid.comment_col) is not str:
            raise ValueError(f"{grid_name} comment column id must be a string")
        if type(grid.coord_x_col) is not str:
            raise ValueError(f"{grid_name} x column id must be a string")
        if type(grid.coord_y_col) is not str:
            raise ValueError(f"{grid_name} y column id must be a string")
    else:
        if type(grid.designator_col) is not int:
            raise ValueError(f"{grid_name} designator column id must be an int")
        if type(grid.comment_col) is not int:
            raise ValueError(f"{grid_name} comment column id must be an int")
        if type(grid.coord_x_col) is not int:
            raise ValueError(f"{grid_name} x column id must be an int")
        if type(grid.coord_y_col) is not int:
            raise ValueError(f"{grid_name} y column id must be an int")

    if grid.has_column_headers:
        # find the designator column index basing on a column title
        designator_col_idx = next(
            (
                i
                for i in range(grid.text_grid.ncols)
                if grid.text_grid.rows_raw()[grid.first_row][i] == grid.designator_col
            ),
            -1,
        )
        # find the comment column index basing on a column title
        comment_col_idx = next(
            (
                i
                for i in range(grid.text_grid.ncols)
                if grid.text_grid.rows_raw()[grid.first_row][i] == grid.comment_col
            ),
            -1,
        )

        coord_x_col_idx = coord_y_col_idx = -1

        if grid_name == "PnP":
            # find the x column index basing on a column title
            coord_x_col_idx = next(
                (
                    i
                    for i in range(grid.text_grid.ncols)
                    if grid.text_grid.rows_raw()[grid.first_row][i] == grid.coord_x_col
                ),
                -1,
            )
            # find the y column index basing on a column title
            coord_y_col_idx = next(
                (
                    i
                    for i in range(grid.text_grid.ncols)
                    if grid.text_grid.rows_raw()[grid.first_row][i] == grid.coord_y_col
                ),
                -1,
            )

        if designator_col_idx == -1:
            raise ValueError(f"{grid_name} designator column not found")
        if comment_col_idx == -1:
            raise ValueError(f"{grid_name} comment column not found")

        logging.debug(f"{grid_name} designator '{grid.designator_col}' found at column {designator_col_idx}")
        logging.debug(f"{grid_name} comment '{grid.comment_col}' found at column {comment_col_idx}")
    else:
        designator_col_idx = grid.designator_col
        comment_col_idx = grid.comment_col
        coord_x_col_idx = grid.coord_x_col
        coord_y_col_idx = grid.coord_y_col

    output: dict[str, (str, str, str)] = {}
    first_row = grid.first_row + (1 if grid.has_column_headers else 0)
    last_row = grid.text_grid.nrows if grid.last_row == -1 else grid.last_row

    if last_row > grid.text_grid.nrows:
        raise ValueError(f"{grid_name} last row > number of rows")

    for row in range(first_row, last_row):
        dsgn = grid.text_grid.rows_raw()[row][designator_col_idx]
        cmnt = grid.text_grid.rows_raw()[row][comment_col_idx]
        if coord_x_col_idx > -1 and coord_y_col_idx > -1:
            cx = grid.text_grid.rows_raw()[row][coord_x_col_idx]
            cy = grid.text_grid.rows_raw()[row][coord_y_col_idx]
        else:
            cx = cy = ""

        # in BOM, designator column used to have a number of items
        dsgn = dsgn.split(',')
        # logging.debug(f"designators: '{dsgn}'")
        for d in dsgn:
            d = d.strip()
            output[d] = (cmnt, cx, cy)

    return output

def __extract_bom_parts(bom: ConfiguredTextGrid) -> dict[str, (str, str, str)]:
    return __extract_grid(bom, "BOM")

def __extract_pnp_parts(pnp: ConfiguredTextGrid) -> dict[str, (str, str, str)]:
    return __extract_grid(pnp, "PnP")

def __txt_to_mm(coord: (str, str)) -> (float, float):
    MIL_PER_MM = 1000/25.4

    try:
        if coord[0].endswith("mm") and coord[1].endswith("mm"):
            return (float(coord[0][:-2]), float(coord[1][:-2]))
        elif coord[0].endswith("mil") and coord[1].endswith("mil"):
            return (float(coord[0][:-3]) / MIL_PER_MM, float(coord[1][:-3]) / MIL_PER_MM)
        else:
            # no suffix - assume mm
            # logging.warn(f"Invalid distance unit(s): {coord[0]}:{coord[1]}")
            return (float(coord[0]), float(coord[1]))
    except Exception as e:
        logging.warn(f"Conversion error at: {coord[0]}:{coord[1]}")
        return (0, 0)

def __check_distances(pnp_parts: dict[str, (str, str, str)]) -> list[(str, str, float)]:
    MIN_DISTANCE = 3.0 #mm

    # decoded coords cache
    decoded_coords: dict[str, (float, float)] = {}
    output = []

    for key_a in pnp_parts:
        for key_b in pnp_parts:
            if key_b != key_a:
                # x
                if coord := decoded_coords.get(key_a):
                    coord_a = coord
                else:
                    coord_a = __txt_to_mm((pnp_parts[key_a][1], pnp_parts[key_a][2]))
                    decoded_coords[key_a] = coord_a
                # y
                if coord := decoded_coords.get(key_b):
                    coord_b = coord
                else:
                    coord_b = __txt_to_mm((pnp_parts[key_b][1], pnp_parts[key_b][2]))
                    decoded_coords[key_b] = coord_b

                dist = ((coord_a[0] - coord_b[0])**2.0) + ((coord_a[1] - coord_b[1])**2.0)
                dist = math.sqrt(dist)
                if dist < MIN_DISTANCE:
                    logging.debug(f"{key_a}({coord_a[0]:.1f}, {coord_a[1]:.1f}) <--> {key_b}({coord_b[0]:.1f}, {coord_b[1]:.1f}) = {dist:0.1f}mm")
                    output.append((key_a, key_b, dist))
    return output

def __compare(bom_parts: dict[str, (str, str, str)], pnp_parts: dict[str, (str, str, str)]) -> CrossCheckResult:
    result = CrossCheckResult()

    # check for items present in BOM, but missing in the PnP
    for designator in bom_parts:
        if designator not in pnp_parts:
            result.bom_parst_missing_in_pnp.append((designator, bom_parts[designator][0]))
    # sort naturally: https://pypi.org/project/natsort/
    result.bom_parst_missing_in_pnp = natsort.natsorted(result.bom_parst_missing_in_pnp)

    # check for items present in PnP, but missing in the BOM
    for designator in pnp_parts:
        if designator not in bom_parts:
            result.pnp_parst_missing_in_bom.append((designator, pnp_parts[designator][0]))
    result.pnp_parst_missing_in_bom = natsort.natsorted(result.pnp_parst_missing_in_bom)

    # check for comments mismatch
    for designator in bom_parts:
        if designator in pnp_parts:
            if bom_parts[designator][0] != pnp_parts[designator][0]:
                result.parts_comment_mismatch.append((designator, bom_parts[designator][0], pnp_parts[designator][0]))
    result.parts_comment_mismatch = natsort.natsorted(result.parts_comment_mismatch)

    # check for conflicting PnP coordinates
    logging.info("Calculate parts center distances...")
    result.parts_coord_conflicts = __check_distances(pnp_parts)
    result.parts_coord_conflicts = natsort.natsorted(result.parts_coord_conflicts)

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
