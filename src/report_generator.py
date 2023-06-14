import logging

from text_grid import *
import cross_check

# -----------------------------------------------------------------------------

def __html_title(content: str) -> str:
    return f'<h3 style="color: DarkSlateGray;">{content}</h3>'

def __html_header(content: str) -> str:
    return f'<h5 style="color: DimGray;">{content}</h5>'

def __html_section_begin() -> str:
    # https://www.w3schools.com/tags/tag_pre.asp
    return '<pre style="font-family: Consolas; font-size: 80%">'

def __html_section_end() -> str:
    return '</pre>'

def __html_span_red(content: str) -> str:
    return f'<span style="color: IndianRed">{content}</span>'

def __html_span_green(content: str) -> str:
    return f'<span style="color: SeaGreen">{content}</span>'

def __html_span_gray(content: str) -> str:
    return f'<span style="color: Gray">{content}</span>'

def __format_comment(designator: str, designator_w: int, bom_cmnt: str, bom_w: int, pnp_cmnt: str) -> str:
    # format BOM comment:
    bom_comment = "{c:{w}}".format(c=bom_cmnt, w=bom_w) # set width
    # TODO: html view does not preserve spaces  when PRE combined with SPAN
    # pnp_in_bom_idx = bom_comment.lower().find(pnp_cmnt.lower())
    # if pnp_in_bom_idx > -1:
    #     before = bom_comment[:pnp_in_bom_idx]
    #     after = bom_comment[pnp_in_bom_idx + len(pnp_cmnt):]
    #     bom_comment = __html_span_red(before) + pnp_cmnt + __html_span_red(after)

    # format PnP comment:
    pnp_comment = pnp_cmnt
    bom_in_pnp_idx = pnp_comment.lower().find(bom_cmnt.lower())
    if bom_in_pnp_idx > -1:
        before = pnp_comment[:bom_in_pnp_idx]
        after = pnp_comment[bom_in_pnp_idx + len(bom_cmnt):]
        pnp_comment = __html_span_green(before) + bom_cmnt + __html_span_green(after)

    # output:
    out = '{desgn:{w}}: <span style="color: Gray">BOM =</span>{bom_comment}, <span style="color: Gray">PnP =</span>{pnp_comment}<br/>'.format(
                desgn=designator, w=designator_w,
                bom_comment=bom_comment,
                pnp_comment=pnp_comment
            )
    # logging.debug(f"'{out}'")
    return out

# -----------------------------------------------------------------------------

def prepare_html_report(proj_name: str, ccresult: cross_check.CrossCheckResult) -> str:
    output = '<html>'
    # https://en.wikipedia.org/wiki/Web_colors
    output += __html_title(f'Cross-check report for: <em>{proj_name}</em>')


    section = __html_header(f'BOM parts missing in the PnP: {len(ccresult.bom_parst_missing_in_pnp)}')
    section += __html_section_begin()
    # determine columns width
    dsgn_w = 0
    for item in ccresult.bom_parst_missing_in_pnp:
        dsgn_w = max(len(item[0]), dsgn_w)
    # format the output
    for item in ccresult.bom_parst_missing_in_pnp:
        section += '{desgn:{w}}: {cmnt}<br/>'.format(
            desgn=item[0], w=dsgn_w, cmnt=item[1]
        )
    section += __html_section_end()
    output += section


    section = __html_header(f'PnP parts missing in the BOM: {len(ccresult.pnp_parst_missing_in_bom)}')
    section += __html_section_begin()
    # determine columns width
    dsgn_w = 0
    for pnp_part in ccresult.pnp_parst_missing_in_bom:
        dsgn_w = max(len(pnp_part[0]), dsgn_w)
    # format the output
    for pnp_part in ccresult.pnp_parst_missing_in_bom:
        section += '{desgn:{w}}: {cmnt}<br/>'.format(
            desgn=pnp_part[0], w=dsgn_w, cmnt=pnp_part[1]
        )
    section += __html_section_end()
    output += section


    section = __html_header(f'BOM and PnP comment mismatch: {len(ccresult.parts_comment_mismatch)}')
    section += __html_section_begin()
    # determine columns width
    dsgn_w = 0
    bom_w = 0
    for item in ccresult.parts_comment_mismatch:
        dsgn_w = max(len(pnp_part[0]), dsgn_w)
        bom_w = max(len(item[1]) + 2, bom_w)
    # format the output
    for item in ccresult.parts_comment_mismatch:
        section += __format_comment(item[0], dsgn_w,
                                    item[1], bom_w,
                                    item[2])
    section += __html_section_end()
    output += section


    output += '<br/></html>'
    return output
