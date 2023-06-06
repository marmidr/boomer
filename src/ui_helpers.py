import customtkinter
import tkinter
import logging

import cross_check

# -----------------------------------------------------------------------------

def textbox_find_text(textbox: customtkinter.CTkTextbox, needle: str) -> int:
    """Search and highlight the text in the TextBox"""

    textbox.tag_delete("search")
    textbox.tag_config("search", background="aqua")
    start = 1.0
    pos = textbox.search(pattern=needle, index=start, stopindex=tkinter.END, nocase=True)
    found_cnt = 0
    length = len(needle)

    if length > 0:
        while pos:
            found_cnt += 1
            row, col = pos.split('.')
            end = int(col) + length
            end = row + '.' + str(end)
            textbox.tag_add("search", pos, end)
            start = end
            pos = textbox.search(pattern=needle, index=start, stopindex=tkinter.END, nocase=True)

    return found_cnt

def textbox_colorize_comments_mismatch(textbox: customtkinter.CTkTextbox, ccr: cross_check.CrossCheckResult):
    """Search and highlight the BOM/PnP comment differences"""

    textbox.tag_delete("rem")
    textbox.tag_config("rem", background="orange")
    textbox.tag_delete("add")
    textbox.tag_config("add", background="lime")

    # search for the comment mismatch section
    section_pos = textbox.search(pattern="ＣＯＭＭＥＮＴ ＭＩＳＭＡＴＣＨ", index=1.0, stopindex=tkinter.END)
    if not section_pos:
        return
    part_mismatch_row, _col = section_pos.split('.')
    part_mismatch_row = int(part_mismatch_row)
    part_mismatch_row += 1 # skip the ==== line
    logging.debug(f"Comments mismatch section start row: {part_mismatch_row}")

    # iterate part by part: rows are in the same order
    for item in ccr.parts_comment_mismatch:
        part_mismatch_row += 1

        if item[1].lower() in item[2].lower():
            needle = item[1]
            tag = "add"
            # logging.debug(f"des={item[0]}, tag={tag}, needle={needle}")
        elif item[2].lower() in item[1].lower():
            needle = item[2]
            tag = "rem"
            # logging.debug(f"des={item[0]}, tag={tag}, needle={needle}")
        else:
            # logging.debug(f"des={item[0]}, tag=---")
            continue

        needle_len = len(needle)

        if needle_len > 0:
            start = float(part_mismatch_row)
            pos = textbox.search(pattern=needle, index=start, stopindex=tkinter.END, nocase=True)
            while pos:
                row, col = pos.split('.')
                # logging.debug(f"  needle {needle} found at {col}")
                if int(row) > part_mismatch_row:
                    # logging.debug(f"  #")
                    break
                end = row + '.' + str(int(col) + needle_len)
                textbox.tag_add(tag, pos, end)
                start = end
                pos = textbox.search(pattern=needle, index=start, stopindex=tkinter.END, nocase=True)
