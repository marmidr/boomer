from odf import opendocument, table
import logging

from text_grid import TextGrid

# -----------------------------------------------------------------------------

def read_ods_sheet(path: str) -> TextGrid:
    """
    Reads ODS/spreadsheet document, returning the first sheet
    """

    logging.info(f"Reading file '{path}'")
    doc = opendocument.load(path)
    tg = TextGrid()

    # with open("odf-dump.xml", "w") as f:
    #     f.write(str(doc.xml()))

    if "opendocument.spreadsheet" in doc.getMediaType():
        for tab in doc.getElementsByType(table.Table):
            name = tab.getAttrNS(table.TABLENS, u"name")
            logging.info(f"Reading sheet: {name}")
            max_cols = 0

            for tablerow in tab.getElementsByType(table.TableRow):
                row_cells = []
                for child in tablerow.childNodes:
                    row_cells.append(str(child).strip())
                max_cols = max(max_cols, len(row_cells))
                tg.rows.append(row_cells)

            tg.nrows = len(tg.rows)
            tg.ncols = max_cols

            # dont read any other sheets
            break
    else:
        logging.error("File does not contain a spreadsheet document")

    return tg