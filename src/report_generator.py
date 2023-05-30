import logging

from text_grid import *

# -----------------------------------------------------------------------------

class ReportGenerator:
    bom: ConfiguredTextGrid = None
    pnp: ConfiguredTextGrid = None

    def __init__(self, bom: ConfiguredTextGrid, pnp: ConfiguredTextGrid):
        self.bom = bom
        self.pnp = pnp

    def analyze(self) -> str:
        bom_parts = ReportGenerator.__extract_bom_parts(self.bom)
        bom_parts.sort()
        pnp_parts = ReportGenerator.__extract_pnp_parts(self.pnp)
        pnp_parts.sort()
        return ReportGenerator.__compare(bom_parts, pnp_parts)

    @staticmethod
    def __extract_bom_parts(bom: ConfiguredTextGrid) -> list[(str, str)]:
        output = ReportGenerator.__extract_grid(bom, "BOM")
        return output

    @staticmethod
    def __extract_pnp_parts(pnp: ConfiguredTextGrid) -> list[(str, str)]:
        output = ReportGenerator.__extract_grid(pnp, "PnP")
        return output

    @staticmethod
    def __extract_grid(grid: ConfiguredTextGrid, grid_name: str) -> list[(str, str)]:
        # TODO: case when the file does not contains a column titles, thus column indexes are used instead
        if not isinstance(grid.designator_col, str):
            raise Exception(f"{grid_name} designator column id must be a string")
        if not isinstance(grid.comment_col, str):
            raise Exception(f"{grid_name} comment column id must be a string")

        designator_col_idx = -1
        for i in range(0, grid.text_grid.ncols):
            if grid.text_grid.rows[grid.first_row][i] == grid.designator_col:
                designator_col_idx = i
                break

        comment_col_idx = -1
        for i in range(0, grid.text_grid.ncols):
            if grid.text_grid.rows[grid.first_row][i] == grid.comment_col:
                comment_col_idx = i
                break

        if designator_col_idx == -1:
            raise Exception(f"{grid_name} designator column not found")
        if comment_col_idx == -1:
            raise Exception(f"{grid_name} comment column not found")

        logging.debug(f"{grid_name} designator '{grid.designator_col}' found at column {designator_col_idx}")
        logging.debug(f"{grid_name} comment '{grid.comment_col}' found at column {comment_col_idx}")

        output = []
        for row in range(grid.first_row+1, grid.text_grid.nrows):
            dsgn = grid.text_grid.rows[row][designator_col_idx]
            cmnt = grid.text_grid.rows[row][comment_col_idx]
            dsgn = dsgn.split(',')
            # logging.debug(f"designators: '{dsgn}'")
            for d in dsgn:
                d = d.strip()
                output.append((d, cmnt))

        return output

    @staticmethod
    def __compare(bom_parts: list[(str, str)], pnp_parts: list[(str, str)]) -> str:
        bom_out = "=== BOM ===\n"
        for item in bom_parts:
            bom_out += "Part {}: {}\n".format(item[0], item[1])

        pnp_out = "=== PnP ===\n"
        for item in pnp_parts:
            pnp_out += "Part {}: {}\n".format(item[0], item[1])

        return bom_out + pnp_out
