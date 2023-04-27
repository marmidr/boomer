# BOM vs PnP Application
# (c) 2023 Mariusz Midor
# https://github.com/marmidr/boomer

import customtkinter
import xls_reader
import xlsx_reader
import csv_reader
import logging

class ScrollableCellGrid(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def load_bom(self, path: str, **kwargs):
        if path.endswith("xls"):
            text_grid = xls_reader.read_xls_sheet(path, **kwargs)
        elif path.endswith("xlsx"):
            text_grid = xlsx_reader.read_xlsx_sheet(path, **kwargs)
        elif path.endswith("csv"):
            text_grid = csv_reader.read_csv(path, **kwargs)
        else:
            raise RuntimeError("Unknown file type")

        logging.info("Read BOM: {} rows x {} cols".format(text_grid.nrows, text_grid.ncols))
        logging.info('Preparing UI...')

        for c in range(text_grid.ncols):
            chbox = customtkinter.CTkCheckBox(self, text=chr(ord('A') + c),
                                              checkbox_width=18, checkbox_height=18,
                                              border_width=2)
            chbox.grid(row=0, column=c+1, sticky="")

        # keeps id of selected radio
        self.var_first_row = customtkinter.IntVar(value=0)

        for r in range(text_grid.nrows):
            for c in range(text_grid.ncols):
                radiobtn = customtkinter.CTkRadioButton(self, text="{}".format(r+1), width=25,
                                                        radiobutton_width=18, radiobutton_height=18,
                                                        variable=self.var_first_row,
                                                        value=r)
                radiobtn.grid(row=r+1, column=0, pady=5, padx=5, sticky="w")

                entry = customtkinter.CTkEntry(self)
                entry.insert(0, text_grid.rows[r][c] or "")
                entry.grid(row=r+1, column=c+1, padx=1, pady=1, sticky="")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # logger config with dimmed time
        logging.basicConfig(format='\033[30m%(asctime)s\033[39m %(levelname)s: %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG,)
        logging.info('Ctk app is starting')

        self.title("BOM vs PnP -> Fight!")
        self.geometry("900x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.cellgrid = ScrollableCellGrid(self)
        self.cellgrid.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nswe")
        self.cellgrid.load_bom("example1/Kaseta_2v1 BOM.xls")
        # self.cellgrid.load_bom("example1/Kaseta_2v1 BOM.xlsx")
        # self.cellgrid.load_bom("example1/Kaseta_2v1 BOM.csv", delim="\t")
        # self.cellgrid.load_bom("example3/Pick Place for TCC-FLOOR2-V3.csv", delim=",")
        logging.info('Ready')

# -----------------------------------------------

if __name__ == "__main__":
    # https://customtkinter.tomschimansky.com/documentation/appearancemode
    customtkinter.set_appearance_mode("light")
    customtkinter.set_default_color_theme("green")
    app = App()
    app.mainloop()
