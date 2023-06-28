import time
import logging

from text_grid import *
import cross_check

# -----------------------------------------------------------------------------

EOL = '\n'
PRE_EOL = '\n' # when \r\n, PRE block inserts empty lines when .html file is opened

def __html_title(content: str) -> str:
    # https://en.wikipedia.org/wiki/Web_colors
    # add the newlines so if copied to the clipboard, it will be somewhat readable
    return f'<h3 style="color: DarkSlateGray;">{content}</h3>{EOL}'

def __html_header(content: str) -> str:
    return f'<h5 style="color: DimGray;">{content}</h5>{EOL}'

def __html_section_begin() -> str:
    # https://www.w3schools.com/tags/tag_pre.asp
    return f'<pre style="font-family: Consolas; font-size: 80%">{EOL}'

def __html_section_end() -> str:
    return f'</pre>{EOL}'

def __html_p(content: str) -> str:
    return f'<p style="font-size: 80%">{content}</p>{EOL}'

def __html_span_red(content: str) -> str:
    return f'<span style="color: IndianRed">{content}</span>'

def __html_span_green(content: str) -> str:
    return f'<span style="color: ForestGreen">{content}</span>'

def __html_span_gray(content: str) -> str:
    return f'<span style="color: Gray">{content}</span>'

def __format_comment(designator: str, designator_w: int, bom_cmnt: str, bom_w: int, pnp_cmnt: str) -> str:
    # sourcery skip: inline-immediately-returned-variable
    ### format BOM comment:
    pnp_in_bom_idx = bom_cmnt.lower().find(pnp_cmnt.lower())
    if pnp_in_bom_idx > -1:
        before = bom_cmnt[:pnp_in_bom_idx]
        after = bom_cmnt[pnp_in_bom_idx + len(pnp_cmnt):]
        bom_comment = __html_span_red(before) + pnp_cmnt + __html_span_red(after)
        bom_comment += ' ' * max(0, bom_w - len(bom_cmnt))
    else:
        bom_comment = bom_cmnt + ' ' * max(0, bom_w - len(bom_cmnt))

    ### format PnP comment:
    pnp_comment = pnp_cmnt
    bom_in_pnp_idx = pnp_comment.lower().find(bom_cmnt.lower())
    if bom_in_pnp_idx > -1:
        before = pnp_comment[:bom_in_pnp_idx]
        after = pnp_comment[bom_in_pnp_idx + len(bom_cmnt):]
        pnp_comment = __html_span_green(before) + bom_cmnt + __html_span_green(after)

    ### output:
    out = '{desgn:{w}}: {bom}{bom_comment} {pnp}{pnp_comment}{eol}'.format(
                desgn=designator, w=designator_w,
                bom=__html_span_gray('BOM='),
                bom_comment=bom_comment,
                pnp=__html_span_gray('PnP='),
                pnp_comment=pnp_comment,
                eol=PRE_EOL
            )
    # logging.debug(f"'{out}'")
    return out

# -----------------------------------------------------------------------------

def prepare_html_report(proj_name: str, ccresult: cross_check.CrossCheckResult) -> str:
    # html/body tags not necessary, moreover disadviced when used with the `klembord`
    output = __html_title(f'Cross-check report for: <em>{proj_name}</em>')
    # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    output += __html_p(f"Generated: <b>{time.strftime('%Y-%m-%d %H:%M:%S')}</b>")

    ### 1st section:
    section = __html_header(f'BOM parts missing in the PnP: {len(ccresult.bom_parst_missing_in_pnp)}')
    section += __html_section_begin()
    # determine columns width
    dsgn_w = 0
    for item in ccresult.bom_parst_missing_in_pnp:
        dsgn_w = max(len(item[0]), dsgn_w)
    # format the output
    for item in ccresult.bom_parst_missing_in_pnp:
        section += '{desgn:{w}}: {cmnt}{eol}'.format(
            desgn=item[0], w=dsgn_w, cmnt=item[1], eol=PRE_EOL
        )
    section += __html_section_end()
    output += section

    ### 2nd section:
    section = __html_header(f'PnP parts missing in the BOM: {len(ccresult.pnp_parst_missing_in_bom)}')
    section += __html_section_begin()
    # determine columns width
    dsgn_w = 0
    for pnp_part in ccresult.pnp_parst_missing_in_bom:
        dsgn_w = max(len(pnp_part[0]), dsgn_w)
    # format the output
    for pnp_part in ccresult.pnp_parst_missing_in_bom:
        section += '{desgn:{w}}: {cmnt}{eol}'.format(
            desgn=pnp_part[0], w=dsgn_w, cmnt=pnp_part[1], eol=PRE_EOL
        )
    section += __html_section_end()
    output += section

    ### 3rd section:
    section = __html_header(f'BOM and PnP comment mismatch: {len(ccresult.parts_comment_mismatch)}')
    section += __html_section_begin()
    # determine columns width
    dsgn_w = 0
    bom_w = 0
    for item in ccresult.parts_comment_mismatch:
        dsgn_w = max(len(item[0]), dsgn_w)
        bom_w = max(len(item[1]) + 2, bom_w)
    # format the output
    for item in ccresult.parts_comment_mismatch:
        section += __format_comment(item[0], dsgn_w,
                                    item[1], bom_w,
                                    item[2])
    section += __html_section_end()
    output += section

    # html block is ready
    return output
