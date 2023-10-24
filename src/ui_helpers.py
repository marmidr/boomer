import customtkinter
import tkinter

# -----------------------------------------------------------------------------

def textbox_find_text(textbox: customtkinter.CTkTextbox, needle: str) -> int:
    """Search and highlight the text in the TextBox"""

    textbox.tag_delete("search")
    textbox.tag_config("search", background="yellow")
    start = 1.0
    pos = textbox.search(pattern=needle, index=start, stopindex=tkinter.END, nocase=True)
    found_cnt = 0
    length = len(needle)

    if length > 0:
        while pos:
            found_cnt += 1
            row, col = pos.split('.')
            end = int(col) + length
            end = f'{row}.{str(end)}'
            textbox.tag_add("search", pos, end)
            start = end
            pos = textbox.search(pattern=needle, index=start, stopindex=tkinter.END, nocase=True)

    return found_cnt

def window_set_centered(app: tkinter.Tk, wnd: tkinter.Toplevel, wnd_w: int, wnd_h: int):
    # set window size
    wnd.geometry(f"{wnd_w}x{wnd_h}")
    # calc position
    wnd_x = app.winfo_rootx()
    wnd_x += app.winfo_width()//2
    wnd_x -= wnd_w//2
    wnd_y = app.winfo_rooty()
    wnd_y += app.winfo_height()//2
    wnd_y -= wnd_h//2
    wnd_y -= 20
    # set screen position
    wnd.geometry(f"+{wnd_x}+{wnd_y}")
