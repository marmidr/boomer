# BOM vs PnP Application
# (c) 2023 Mariusz Midor
# github.com/marmidr

import customtkinter
import xls_reader
import xlsx_reader

# class CellGrid(customtkinter.CTkFrame):
class ScrollableCellGrid(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def load_bom(self, path: str):
        if path.endswith("xls"):
            text_grid = xls_reader.read_xls_sheet(path)
        elif path.endswith("xlsx"):
            text_grid = xlsx_reader.read_xlsx_sheet(path)
        else:
            raise RuntimeError("Unknown file type")

        # list of CTkEntry
        self.entries = []

        for r in range(text_grid.nrows):
            for c in range(text_grid.ncols):
                entry = customtkinter.CTkEntry(self)
                entry.insert(0, text_grid.rows[r][c] or "")
                entry.grid(row=r, column=c, padx=1, pady=1, sticky="")
                list.append(self.entries, entry)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("BOM vs PnP -> Fight!")
        self.geometry("600x280")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.cellgrid = ScrollableCellGrid(self)
        self.cellgrid.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nswe")
        # self.cellgrid.load_bom("example1/Kaseta_2v1 BOM.xls")
        self.cellgrid.load_bom("example1/Kaseta_2v1 BOM.xlsx")

# -----------------------------------------------

if __name__ == "__main__":
    customtkinter.set_appearance_mode("light")
    customtkinter.set_default_color_theme("green")
    app = App()
    app.mainloop()
