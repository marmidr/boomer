# import logging

from text_grid import *
import cross_check

# -----------------------------------------------------------------------------

def prepare_html_report(proj_name: str, ccresult: cross_check.CrossCheckResult) -> str:
    output = '<html>'
    # https://en.wikipedia.org/wiki/Web_colors
    output += f'<h3 style="color: DarkSlateGray;">Cross-check report for: <em>{proj_name}</em></h3>'


    section = f'<h5 style="color: DimGray;">BOM parts missing in the PnP: {len(ccresult.bom_parst_missing_in_pnp)}</h5>'
    longest_designator = 0
    for item in ccresult.bom_parst_missing_in_pnp:
        longest_designator = max(len(item[0]), longest_designator)
    section += '<code style="font-family: Consolas; font-size: 80%">'
    for item in ccresult.bom_parst_missing_in_pnp:
        section += '{name:{w}}: {cmnt}<br/>'.format(
            name=item[0], w=longest_designator, cmnt=item[1]
        )
    section += '</code>'
    output += section


    section = f'<h5 style="color: DimGray;">PnP parts missing in the BOM: {len(ccresult.pnp_parst_missing_in_bom)}</h5>'
    section += '<code style="font-family: Consolas; font-size: 80%">'
    longest_designator = 0
    for pnp_part in ccresult.pnp_parst_missing_in_bom:
        longest_designator = max(len(pnp_part[0]), longest_designator)
    for pnp_part in ccresult.pnp_parst_missing_in_bom:
        section += '{name:{w}}: {cmnt}<br/>'.format(
            name=pnp_part[0], w=longest_designator, cmnt=pnp_part[1]
        )
    section += '</code>'
    output += section


    section = f'<h5 style="color: DimGray;">BOM and PnP comment mismatch: {len(ccresult.parts_comment_mismatch)}</h5>'
    section += '<code style="font-family: Consolas; font-size: 80%">'
    longest_designator = 0
    longest_bom_comment = 0
    for item in ccresult.parts_comment_mismatch:
        longest_designator = max(len(pnp_part[0]), longest_designator)
        longest_bom_comment = max(len(item[1]) + 2, longest_bom_comment)
    for item in ccresult.parts_comment_mismatch:
        # TODO: find BOM comment in PnP and vice-versa, color the differences
        section += '{name:{w}}: BOM={bom_cmnt:{bw}}, PnP={pnp_cmnt}<br/>'.format(
            name=item[0], w=longest_designator,
            bom_cmnt=f"'{item[1]}'", bw=longest_bom_comment,
            pnp_cmnt=f"'{item[2]}'"
        )
    output += section
    section += '</code>'


    output += '</html>'
    return output
