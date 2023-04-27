# BOM vs PnP Application
# (c) 2023 Mariusz Midor
# https://github.com/marmidr/boomer

import customtkinter
import xls_reader
import xlsx_reader
import csv_reader
import logging

# -----------------------------------------------------------------------------

class ConfigFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        lbl_config = customtkinter.CTkLabel(self, text="BOM+PnP configurations:")
        lbl_config.grid(row=0, column=0, pady=5, padx=5, sticky="")

        # TODO: load configs from file
        opt_config = customtkinter.CTkOptionMenu(self, values=["---", "Altium", "Pads", "Eagle"], command=self.opt_config_event)
        opt_config.grid(row=0, column=1, pady=5, padx=5, sticky="we")
        self.grid_columnconfigure(1, weight=1)

        btn_load = customtkinter.CTkButton(self, text="Load", command=self.button_load_event)
        btn_load.grid(row=0, column=2, pady=5, padx=5)

        btn_save_as = customtkinter.CTkButton(self, text="Save as...", command=self.button_save_event)
        btn_save_as.grid(row=0, column=3, pady=5, padx=5)

        btn_delete = customtkinter.CTkButton(self, text="Delete config", command=self.button_del_event)
        btn_delete.grid(row=0, column=4, pady=5, padx=5)

    def button_load_event(self):
        logging.debug("Load")

    def button_save_event(self):
        logging.debug("Save")

    def button_del_event(self):
        logging.debug("Del")

    def opt_config_event(self, new_config: str):
        logging.debug(f"Load config: '{new_config}")

# -----------------------------------------------------------------------------

class BOMConfig(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        lbl_separator = customtkinter.CTkLabel(self, text="CSV Separator:")
        lbl_separator.grid(row=0, column=0, pady=5, padx=5, sticky="")

        opt_separator = customtkinter.CTkOptionMenu(self, values=["COMMA", "SEMICOLON", "TAB", "SPACE"], command=self.opt_separator_event)
        opt_separator.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        self.grid_columnconfigure(1, weight=1)

    def opt_separator_event(self, new_sep: str):
        logging.debug(f"Separator: '{new_sep}")

class BOMView(customtkinter.CTkScrollableFrame):
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

# -----------------------------------------------------------------------------

class App(customtkinter.CTk):
    def __init__(self):
        logging.info('Ctk app is starting')
        super().__init__()

        self.title("BOM vs PnP -> Fight!")
        self.geometry("900x600")
        self.grid_columnconfigure(0, weight=1)

        # panel with predefined configs
        config_frame = ConfigFrame(self)
        config_frame.grid(row=0, column=0, padx=5, pady=5, sticky="we")

        # panel with BOM/PnP/Result
        tabview = customtkinter.CTkTabview(self)
        tabview.grid(row=1, column=0, padx=5, pady=5, sticky="wens")
        self.grid_rowconfigure(1, weight=1) # set row 1 height to all remaining space

        tab_bom = tabview.add("BOM")
        tab_pnp = tabview.add("PnP")
        tab_summary = tabview.add("Comparison Summary")

        tabview.set("BOM")  # set currently visible tab

        # panel with the BOM
        bom_view = BOMView(tab_bom)
        bom_view.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        bom_view.load_bom("example1/Kaseta_2v1 BOM.xls")
        # bom_view.load_bom("example1/Kaseta_2v1 BOM.xlsx")
        # bom_view.load_bom("example1/Kaseta_2v1 BOM.csv", delim="\t")
        # bom_view.load_bom("example3/Pick Place for TCC-FLOOR2-V3.csv", delim=",")

        bom_config = BOMConfig(tab_bom)
        bom_config.grid(row=1, column=0, pady=5, padx=5, sticky="we")

        tab_bom.grid_columnconfigure(0, weight=1)
        tab_bom.grid_rowconfigure(0, weight=1)

        # UI ready
        logging.info('Ready')

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # logger config with dimmed time
    # https://docs.python.org/3/howto/logging.html
    logging.basicConfig(format='\033[30m%(asctime)s\033[39m %(levelname)s: %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    # https://customtkinter.tomschimansky.com/documentation/appearancemode
    customtkinter.set_appearance_mode("light")
    customtkinter.set_default_color_theme("green")

    app = App()
    app.mainloop()
