# BOM vs PnP Application
# (c) 2023 Mariusz Midor
# https://github.com/marmidr/boomer

import customtkinter
import tkinter
import logging
import os
import configparser

import xls_reader
import xlsx_reader
import csv_reader

# -----------------------------------------------------------------------------

class Proj:
    project_path: str
    pnp_path: str
    profile: str
    __config: configparser.ConfigParser

    def __init__(self):
        self.project_path = ""
        self.pnp_path = ""
        self.profile = "---"

        # https://docs.python.org/3/library/configparser.html
        self.__config = configparser.ConfigParser()
        if os.path.isfile("boomer.ini"):
            self.__config.read('boomer.ini')
        else:
            self.__config['common'] = {
                "initial_dir": "",
            }
            self.__config['profile.altium'] = {
                "bom_first_row": 0,
                "pnp_first_row": 0,
                "pnp_separator": ";",
            }
            self.__config['profile.pads'] = {
                "bom_first_row": 0,
                "pnp_first_row": 0,
                "pnp_separator": ";",
            }

    def cfg_get_section(self, sect_name: str) -> configparser.SectionProxy:
        try:
            self.__config[sect_name]
        except:
            self.__config[sect_name] = {}

        return self.__config[sect_name]

    def cfg_get_profiles(self) -> list[str]:
        profiles = [""]
        for sect in self.__config.sections():
            if sect.startswith("profile."):
                profiles.append(sect.removeprefix("profile."))

        return profiles

    def cfg_save(self):
        section = self.cfg_get_section("project." + self.project_path)
        section["pnp"] = os.path.basename(self.pnp_path)
        section["profile"] = self.profile

        with open('boomer.ini', 'w') as configfile:
            self.__config.write(configfile)


proj = Proj()

# -----------------------------------------------------------------------------

class ProjectProfileFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        lbl_config = customtkinter.CTkLabel(self, text="BOM+PnP profile:")
        lbl_config.grid(row=0, column=0, pady=5, padx=5, sticky="")

        opt_profile = customtkinter.CTkOptionMenu(self, values=proj.cfg_get_profiles(), command=self.opt_profile_event)
        opt_profile.grid(row=0, column=1, pady=5, padx=5, sticky="we")
        self.grid_columnconfigure(1, weight=1)

        btn_load = customtkinter.CTkButton(self, text="Load", command=self.button_load_event)
        btn_load.grid(row=0, column=2, pady=5, padx=5)

        btn_save_as = customtkinter.CTkButton(self, text="Save as...", command=self.button_save_event)
        btn_save_as.grid(row=0, column=3, pady=5, padx=5)
        btn_save_as.configure(state="disabled")

        btn_delete = customtkinter.CTkButton(self, text="Delete profile", command=self.button_del_event)
        btn_delete.grid(row=0, column=4, pady=5, padx=5)

    def button_load_event(self):
        logging.debug("Load")

    def button_save_event(self):
        logging.debug("Save")

    def button_del_event(self):
        logging.debug("Del")

    def opt_profile_event(self, new_profile: str):
        logging.debug(f"Load profile: {new_profile}")
        proj.profile = new_profile
        proj.cfg_save()

# -----------------------------------------------------------------------------

class ProjectFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(1, weight=1)
        # self.grid_rowconfigure(0, weight=1)

        lbl_proj_path = customtkinter.CTkLabel(self, text="Project (BOM) path:")
        lbl_proj_path.grid(row=0, column=0, pady=5, padx=5, sticky="w")

        self.bom_paths = []
        self.cbx_bom_var = customtkinter.StringVar(value="")
        self.cbx_bom_path = customtkinter.CTkComboBox(self, values=self.bom_paths, command=self.cbx_bom_event,
                                                      variable=self.cbx_bom_var)
        self.cbx_bom_path.grid(row=0, column=1, pady=5, padx=5, sticky="we")

        btn_browse = customtkinter.CTkButton(self, text="Browse...", command=self.button_browse_event)
        btn_browse.grid(row=0, column=2, pady=5, padx=5, sticky="e")

        # ---

        lbl_pnp_path = customtkinter.CTkLabel(self, text="Pick'n'Place path:")
        lbl_pnp_path.grid(row=1, column=0, pady=5, padx=5, sticky="w")

        self.pnp_paths = []
        self.cbx_pnp_var = customtkinter.StringVar(value="")
        self.cbx_pnp_path = customtkinter.CTkComboBox(self, values=self.pnp_paths, command=self.cbx_pnp_event,
                                                      variable=self.cbx_pnp_var)
        self.cbx_pnp_path.grid(row=1, column=1, pady=5, padx=5, sticky="we")

        self.config_frame = ProjectProfileFrame(self)
        self.config_frame.grid(row=2, column=0, padx=5, pady=5, columnspan=3, sticky="we")

    def cbx_bom_event(self, new_path: str):
        logging.debug(f"Open BOM: '{new_path}")
        # TODO: if known project, set the PnP file path

    def cbx_pnp_event(self, pnp_path: str):
        logging.debug(f"Change PnP: '{pnp_path}")
        # update config
        proj.pnp_path = pnp_path
        section = proj.cfg_get_section("project." + proj.project_path)
        proj.cfg_save()

    def button_browse_event(self):
        logging.debug("Browse BOM")
        # https://docs.python.org/3/library/dialog.html

        # TODO: get the initial dir from the proj settings
        bom_path = tkinter.filedialog.askopenfilename(
            title="Select BOM file",
            initialdir=None,
            filetypes=(
            ("Supported (*.xls; *.xlsx; *.csv)", "*.xls; *.xlsx; *.csv"),
            ("All (*.*)", "*.*")),
        )
        logging.debug(f"Selected path: {bom_path}")

        if os.path.isfile(bom_path):
            self.bom_paths.append(bom_path)
            self.cbx_bom_path.configure(values=self.bom_paths)
            self.cbx_bom_var.set(bom_path)

            # load all files from the BOM directory to the PnP list
            self.cbx_pnp_var.set("")
            bom_dir = os.path.dirname(bom_path)
            self.pnp_paths = []
            for de in os.scandir(bom_dir):
                self.pnp_paths.append(de.path)
            self.cbx_pnp_path.configure(values=self.pnp_paths)

            # update config
            proj.project_path = bom_path
            proj.cfg_save()

# -----------------------------------------------------------------------------

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

class BOMConfig(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        lbl_separator = customtkinter.CTkLabel(self, text="CSV Separator:")
        lbl_separator.grid(row=0, column=0, pady=5, padx=5, sticky="")

        opt_separator = customtkinter.CTkOptionMenu(self, values=["COMMA", "SEMICOLON", "TAB", "FIXED-WIDTH"], command=self.opt_separator_event)
        opt_separator.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        self.grid_columnconfigure(1, weight=1)

    def opt_separator_event(self, new_sep: str):
        logging.debug(f"Separator: '{new_sep}")

# -----------------------------------------------------------------------------

class PnPView(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.textbox = customtkinter.CTkTextbox(self,
                                                font=customtkinter.CTkFont(size=12, family="Consolas"),
                                                activate_scrollbars=True)
        self.textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.textbox.insert("0.0", "𝐓𝐞𝐱𝐭 𝐄𝐝𝐢𝐭𝐨𝐫, 𝕋𝕖𝕩𝕥 𝔼𝕕𝕚𝕥𝕠𝕣")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def load_pnp(self, path: str, **kwargs):
        text_grid = csv_reader.read_csv(path, **kwargs)
        logging.info("Read PNP: {} rows x {} cols".format(text_grid.nrows, text_grid.ncols))
        # logging.info('Preparing UI...')

# -----------------------------------------------------------------------------

class PnPConfig(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        lbl_separator = customtkinter.CTkLabel(self, text="CSV Separator:")
        lbl_separator.grid(row=0, column=0, pady=5, padx=5, sticky="")

        opt_separator = customtkinter.CTkOptionMenu(self, values=["COMMA", "SEMICOLON", "TAB", "FIXED-WIDTH"], command=self.opt_separator_event)
        opt_separator.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        self.grid_columnconfigure(1, weight=1)

    def opt_separator_event(self, new_sep: str):
        logging.debug(f"Separator: '{new_sep}")

# -----------------------------------------------------------------------------

class App(customtkinter.CTk):
    def __init__(self):
        logging.info('Ctk app is starting')
        super().__init__()

        self.title("BOM vs PnP -> Fight!")
        self.geometry("1200x600")
        self.grid_columnconfigure(0, weight=1)

        # panel with Proj/BOM/PnP/Result
        tabview = customtkinter.CTkTabview(self)
        tabview.grid(row=1, column=0, padx=5, pady=5, sticky="wens")
        self.grid_rowconfigure(1, weight=1) # set row 1 height to all remaining space
        tab_prj = tabview.add("Project")
        tab_bom = tabview.add("Bill Of Materials")
        tab_pnp = tabview.add("Pick And Place")
        tab_summary = tabview.add("Comparison Summary")
        tabview.set("Project")  # set currently visible tab

        # panel with predefined configs
        proj_frame = ProjectFrame(tab_prj)
        proj_frame.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        tab_prj.grid_columnconfigure(0, weight=1)
        tab_prj.grid_rowconfigure(0, weight=1)

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

        # panel with the PnP
        pnp_view = PnPView(tab_pnp)
        pnp_view.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        pnp_view.load_pnp("example1/Pick Place for Kaseta2v1(Standard).csv", delim="cw")

        pnp_config = PnPConfig(tab_pnp)
        pnp_config.grid(row=1, column=0, padx=5, pady=5, sticky="we")

        tab_pnp.grid_columnconfigure(0, weight=1)
        tab_pnp.grid_rowconfigure(0, weight=1)

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
