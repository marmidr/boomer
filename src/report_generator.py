import logging
# import itertools

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
        pnp_parts = ReportGenerator.__extract_pnp_parts(self.pnp)
        return ReportGenerator.__compare(bom_parts, pnp_parts)

    @staticmethod
    def __extract_bom_parts(bom: ConfiguredTextGrid) -> dict[str, str]:
        output = ReportGenerator.__extract_grid(bom, "BOM")
        return output

    @staticmethod
    def __extract_pnp_parts(pnp: ConfiguredTextGrid) -> dict[str, str]:
        output = ReportGenerator.__extract_grid(pnp, "PnP")
        return output

    @staticmethod
    def __extract_grid(grid: ConfiguredTextGrid, grid_name: str) -> dict[str, str]:
        # TODO: case when the file does not contains a column titles, thus column indexes are used instead
        if not isinstance(grid.designator_col, str):
            raise Exception(f"{grid_name} designator column id must be a string")
        if not isinstance(grid.comment_col, str):
            raise Exception(f"{grid_name} comment column id must be a string")

        # find part designator column index
        designator_col_idx = -1
        for i in range(0, grid.text_grid.ncols):
            if grid.text_grid.rows[grid.first_row][i] == grid.designator_col:
                designator_col_idx = i
                break

        # find part comment column index
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

        output = {}
        last_row = grid.text_grid.nrows if grid.last_row == -1 else grid.last_row
        if last_row > grid.text_grid.nrows:
            raise Exception(f"{grid_name} last row > number of rows")

        for row in range(grid.first_row+1, last_row):
            dsgn = grid.text_grid.rows[row][designator_col_idx]
            cmnt = grid.text_grid.rows[row][comment_col_idx]
            dsgn = dsgn.split(',')
            # logging.debug(f"designators: '{dsgn}'")
            for d in dsgn:
                d = d.strip()
                output[d] = cmnt

        return output

    @staticmethod
    def __compare(bom_parts: dict[str, str], pnp_parts: dict[str, str]) -> str:
        missing_pnp_parts = []
        missing_bom_parts = []
        comment_mismatch_parts = []

        # check for items present in BOM, but missing in the PnP
        for bom_part in bom_parts:
            if not bom_part in pnp_parts:
                missing_pnp_parts.append((bom_part, bom_parts[bom_part]))
        missing_pnp_parts.sort()

        # check for items present in PnP, but missing in the BOM
        for pnp_part in pnp_parts:
            if not pnp_part in bom_parts:
                missing_bom_parts.append((pnp_part, pnp_parts[pnp_part]))
        missing_bom_parts.sort()

        # check for comments mismatch
        for bom_part in bom_parts:
            if bom_part in pnp_parts:
                if bom_parts[bom_part] != pnp_parts[bom_part]:
                    comment_mismatch_parts.append((bom_part, bom_parts[bom_part], pnp_parts[bom_part]))
        comment_mismatch_parts.sort()

        # prepare analysis report
        longest_part_name = 0
        for bom_part in bom_parts:
            l = len(bom_part)
            if l > longest_part_name:
                longest_part_name = l

        for pnp_part in pnp_parts:
            l = len(pnp_part)
            if l > longest_part_name:
                longest_part_name = l


        longest_bom_comment = 0
        for bom_part in bom_parts:
            l = len(bom_parts[bom_part])
            if l > longest_bom_comment:
                longest_bom_comment = l

        output = ""

        output += f"ＭＩＳＳＩＮＧ ＰＡＲＴＳ ＩＮ ＰＮＰ: {len(missing_pnp_parts)}\n"
        output += "====================================\n"
        for item in missing_pnp_parts:
            output += "{name:{w}}: {cmnt}\n".format(
                name=item[0], w=longest_part_name, cmnt=item[1])
        output += "\n"

        output += f"ＭＩＳＳＩＮＧ ＰＡＲＴＳ ＩＮ ＢＯＭ: {len(missing_bom_parts)}\n"
        output += "====================================\n"
        for item in missing_bom_parts:
            output += "{name:{w}}: {cmnt}\n".format(
                name=item[0], w=longest_part_name, cmnt=item[1])
        output += "\n"

        output += f"ＢＯＭ ＡＮＤ ＰＮＰ ＣＯＭＭＥＮＴ ＭＩＳＭＡＴＣＨ: {len(comment_mismatch_parts)}\n"
        output += "=================================================\n"
        for item in comment_mismatch_parts:
            output += "{name:{w}}: BOM={bom_cmnt:{bw}}, PnP={pnp_cmnt}\n".format(
                name=item[0], w=longest_part_name, bom_cmnt=item[1], bw=longest_bom_comment, pnp_cmnt=item[2])
        output += "\n"

        return output
