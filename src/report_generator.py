# import logging

from text_grid import *
import cross_check

# -----------------------------------------------------------------------------

def __html_title(content: str) -> str:
    return f'<h3 style="color: DarkSlateGray;">{content}</h3>'

def __html_header(content: str) -> str:
    return f'<h5 style="color: DimGray;">{content}</h5>'

def __html_section_begin() -> str:
    return '<code style="font-family: Consolas; font-size: 80%">'

def __html_section_end() -> str:
    return '</code>'

# -----------------------------------------------------------------------------

def prepare_html_report(proj_name: str, ccresult: cross_check.CrossCheckResult) -> str:
    output = '<html>'
    # https://en.wikipedia.org/wiki/Web_colors
    output += __html_title(f'Cross-check report for: <em>{proj_name}</em>')


    section = __html_header(f'BOM parts missing in the PnP: {len(ccresult.bom_parst_missing_in_pnp)}')
    section += __html_section_begin()
    # determine columns width
    longest_designator = 0
    for item in ccresult.bom_parst_missing_in_pnp:
        longest_designator = max(len(item[0]), longest_designator)
    # format the output
    for item in ccresult.bom_parst_missing_in_pnp:
        section += '{name:{w}}: {cmnt}<br/>'.format(
            name=item[0], w=longest_designator, cmnt=item[1]
        )
    section += __html_section_end()
    output += section


    section = __html_header(f'PnP parts missing in the BOM: {len(ccresult.pnp_parst_missing_in_bom)}')
    section += __html_section_begin()
    # determine columns width
    longest_designator = 0
    for pnp_part in ccresult.pnp_parst_missing_in_bom:
        longest_designator = max(len(pnp_part[0]), longest_designator)
    # format the output
    for pnp_part in ccresult.pnp_parst_missing_in_bom:
        section += '{name:{w}}: {cmnt}<br/>'.format(
            name=pnp_part[0], w=longest_designator, cmnt=pnp_part[1]
        )
    section += __html_section_end()
    output += section


    section = __html_header(f'BOM and PnP comment mismatch: {len(ccresult.parts_comment_mismatch)}')
    section += __html_section_begin()
    # determine columns width
    longest_designator = 0
    longest_bom_comment = 0
    for item in ccresult.parts_comment_mismatch:
        longest_designator = max(len(pnp_part[0]), longest_designator)
        longest_bom_comment = max(len(item[1]) + 2, longest_bom_comment)
    # format the output
    for item in ccresult.parts_comment_mismatch:
        # TODO: find BOM comment in PnP and vice-versa, color the differences
        section += '{name:{w}}: BOM={bom_cmnt:{bw}}, PnP={pnp_cmnt}<br/>'.format(
            name=item[0], w=longest_designator,
            bom_cmnt=f"'{item[1]}'", bw=longest_bom_comment,
            pnp_cmnt=f"'{item[2]}'"
        )
    section += __html_section_end()
    output += section


    output += '<br/></html>'
    return output
