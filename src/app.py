# BOM vs PnP Application
# (c) 2023 Mariusz Midor
# https://github.com/marmidr/boomer

import customtkinter
import xls_reader
import xlsx_reader

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
        self.radios=[]

        for c in range(text_grid.ncols):
            chbox = customtkinter.CTkCheckBox(self, text=chr(ord('A') + c),
                                              checkbox_width=18, checkbox_height=18,
                                              border_width=2)
            chbox.grid(row=0, column=c+1, sticky="")

        # first row with nonempty column A
        nonempty_row_found = False
        # keeps id of selected radio
        self.var_first_row = customtkinter.IntVar(value=0)

        for r in range(text_grid.nrows):
            if not text_grid.rows[r][0] is None:
                # iterate until the first column is empty
                nonempty_row_found = True

            if nonempty_row_found and text_grid.rows[r][0] is None:
                # column A is empty? ignore remaining rows
                break

            for c in range(text_grid.ncols):
                radiobtn = customtkinter.CTkRadioButton(self, text="{}".format(r+1), width=25,
                                                        radiobutton_width=18, radiobutton_height=18,
                                                        variable=self.var_first_row,
                                                        value=r)
                radiobtn.grid(row=r+1, column=0, pady=5, padx=5, sticky="n")

                entry = customtkinter.CTkEntry(self)
                entry.insert(0, text_grid.rows[r][c] or "")
                entry.grid(row=r+1, column=c+1, padx=1, pady=1, sticky="")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("BOM vs PnP -> Fight!")
        self.geometry("900x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.cellgrid = ScrollableCellGrid(self)
        self.cellgrid.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nswe")
        # self.cellgrid.load_bom("example1/Kaseta_2v1 BOM.xls")
        self.cellgrid.load_bom("example1/Kaseta_2v1 BOM.xlsx")

        # create radiobutton frame
        self.radiobutton_frame = customtkinter.CTkFrame(self)
        self.radiobutton_frame.grid(row=0, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.radio_var = customtkinter.IntVar(value=0)
        self.label_radio_group = customtkinter.CTkLabel(master=self.radiobutton_frame, text="CTkRadioButton Group:")
        self.label_radio_group.grid(row=0, column=2, columnspan=1, padx=10, pady=10, sticky="")
        self.radio_button_1 = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=0)
        self.radio_button_1.grid(row=1, column=2, pady=10, padx=20, sticky="n")
        self.radio_button_2 = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=1)
        self.radio_button_2.grid(row=2, column=2, pady=10, padx=20, sticky="n")
        self.radio_button_3 = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=2)
        self.radio_button_3.grid(row=3, column=2, pady=10, padx=20, sticky="n")


# -----------------------------------------------

if __name__ == "__main__":
    # https://customtkinter.tomschimansky.com/documentation/appearancemode
    customtkinter.set_appearance_mode("light")
    customtkinter.set_default_color_theme("green")
    app = App()
    app.mainloop()
