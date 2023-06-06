# import logging

from text_grid import *
import cross_check

# -----------------------------------------------------------------------------

def prepare_text_report(ccresult: cross_check.CrossCheckResult) -> str:
    output = ""

    output += f"ＢＯＭ ＰＡＲＴＳ ＭＩＳＳＩＮＧ ＩＮ ＰＮＰ: {len(ccresult.bom_parst_missing_in_pnp)}\n"
    output += "==========================================\n"
    longest_designator = 0
    for item in ccresult.bom_parst_missing_in_pnp:
        longest_designator = max(len(item[0]), longest_designator)

    for item in ccresult.bom_parst_missing_in_pnp:
        output += "{name:{w}}: {cmnt}\n".format(
            name=item[0], w=longest_designator, cmnt=item[1]
        )
    output += "\n"


    output += f"ＰＮＰ ＰＡＲＴＳ ＭＩＳＳＩＮＧ ＩＮ ＢＯＭ: {len(ccresult.pnp_parst_missing_in_bom)}\n"
    output += "==========================================\n"
    longest_designator = 0
    for pnp_part in ccresult.pnp_parst_missing_in_bom:
        longest_designator = max(len(pnp_part[0]), longest_designator)

    for pnp_part in ccresult.pnp_parst_missing_in_bom:
        output += "{name:{w}}: {cmnt}\n".format(
            name=pnp_part[0], w=longest_designator, cmnt=pnp_part[1]
        )
    output += "\n"


    output += f"ＢＯＭ ＡＮＤ ＰＮＰ ＣＯＭＭＥＮＴ ＭＩＳＭＡＴＣＨ: {len(ccresult.parts_comment_mismatch)}\n"
    output += "=================================================\n"
    longest_designator = 0
    longest_bom_comment = 0
    for item in ccresult.parts_comment_mismatch:
        longest_designator = max(len(pnp_part[0]), longest_designator)
        longest_bom_comment = max(len(item[1]) + 2, longest_bom_comment)

    for item in ccresult.parts_comment_mismatch:
        output += "{name:{w}}: BOM={bom_cmnt:{bw}}, PnP={pnp_cmnt}\n".format(
            name=item[0], w=longest_designator, bom_cmnt=f"'{item[1]}'", bw=longest_bom_comment, pnp_cmnt=f"'{item[2]}'"
        )
    output += "\n"

    return output
