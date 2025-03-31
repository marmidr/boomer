import customtkinter
import tkinter
from tkhtmlview import HTMLScrolledText
import logger

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


# https://stackoverflow.com/questions/4266566/stardand-context-menu-in-python-tkinter-text-widget-when-mouse-right-button-is-p
def wgt_install_standard_menu(wgt, items: str):
    if items is None:
        items = "cxpl"

    if items == "":
        return

    menu = tkinter.Menu(wgt, tearoff=0)
    wgt.menu = menu
    menu.wgt = wgt

    if "c" in items:
        menu.add_command(label="Copy",
                        command=lambda: menu.wgt.focus_force() or menu.wgt.event_generate("<<Copy>>"))
    if "x" in items:
        menu.add_command(label="Cut",
                        command=lambda: menu.wgt.focus_force() or menu.wgt.event_generate("<<Cut>>"))
    if "p" in items:
        menu.add_command(label="Paste",
                        command=lambda: menu.wgt.focus_force() or menu.wgt.event_generate("<<Paste>>"))
    if "l" in items:
        menu.add_command(label="Clear",
                        command=lambda: menu.wgt.focus_force() or menu.wgt.delete(0, tkinter.END))
    if "a" in items:
        menu.add_separator()
        menu.add_command(label="Select all",
                        command=lambda: menu.wgt.event_select_all())

class HTMLScrolledTextWithPPM(HTMLScrolledText):
    # common menus for all HTMLScrolledText instances
    menus: dict[str, tkinter.Menu] = {}

    def __init__(self, *args, **kwargs):
        menuitems = kwargs.pop("menuitems") if "menuitems" in kwargs else None
        HTMLScrolledText.__init__(self, *args, **kwargs)

        self.add_menu(menuitems)
        # overwrite default class binding so we don't need to return "break"
        self.bind_class("HTMLScrolledText", "<Control-a>", self.event_select_all)
        self.bind("<Button-3><ButtonRelease-3>", self.show_menu)

    def add_menu(self, menuitems: str):
        menuitems_default = menuitems or "*"

        if menuitems_default in HTMLScrolledTextWithPPM.menus.keys():
            self.menu = HTMLScrolledTextWithPPM.menus[menuitems_default]
        else:
            try:
                self.menu = None
                wgt_install_standard_menu(self, menuitems)
                if self.menu:
                    # update menus database
                    HTMLScrolledTextWithPPM.menus[menuitems_default] = self.menu
            except Exception as e:
                logger.error(f"HTMLScrolledTextWithPPM: {e}")

    def show_menu(self, ev):
        if self.menu:
            self.menu.wgt = self # replace reference to the calling widget
            self.menu.post(ev.x_root, ev.y_root)

    def event_select_all(self, *_args):
        self.focus_force()
        # self.selection_range('0', tkinter.END)
