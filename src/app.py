# BOM vs PnP Application
# (c) 2023 Mariusz Midor
# https://github.com/marmidr/boomer

import customtkinter
import tkinter
import logging
import os
import configparser
import textwrap

import xls_reader
import xlsx_reader
import csv_reader

# -----------------------------------------------------------------------------

class Profile:
    name: str
    bom_first_row: int # 0-based
    bom_separator: str
    pnp_first_row: int # 0-based
    pnp_separator: str
    __config: configparser.ConfigParser

    def __init__(self, config: configparser.ConfigParser):
        self.name = "noname"
        self.bom_first_row = 0
        self.bom_separator = "COMMA"
        self.pnp_first_row = 0
        self.pnp_separator = "COMMA"
        self.__config = config

    def load(self, name: str):
        if os.path.isfile("boomer.ini"):
            logging.debug(f"Load profile {name}")
            self.name = name
            section = self.__config['profile.' + self.name]
            self.bom_first_row = section["bom_first_row"]
            self.bom_separator = section["bom_separator"]
            self.pnp_first_row = section["pnp_first_row"]
            self.pnp_separator = section["pnp_separator"]
        else:
            logging.warning("Config file not found")

    def save(self):
        logging.debug(f"Save profile: {self.name}")
        self.__config["profile." + self.name] = {
            "bom_first_row": self.bom_first_row,
            "bom_separator": self.bom_separator,
            "pnp_first_row": self.pnp_first_row,
            "pnp_separator": self.pnp_separator
        }
        with open('boomer.ini', 'w') as f:
            self.__config.write(f)

    @staticmethod
    def get_sepatators() -> list[str]:
        return ["COMMA", "SEMICOLON", "TAB", "FIXED-WIDTH", "REGEX"]

    @staticmethod
    def translate_sepatator(sep: str) -> str:
        # Python 3.10+
        match sep:
            case "COMMA":
                return ","
            case "SEMICOLON":
                return ";"
            case "TAB":
                return "\t"
            case "FIXED-WIDTH":
                return "*fw"
            case "REGEX":
                return "*re"
            case _:
                assert not "Unknown BOM separator"

    def get_bom_delimiter(self) -> str:
        return Profile.translate_sepatator(self.bom_separator)

    def get_pnp_delimiter(self) -> str:
        return Profile.translate_sepatator(self.pnp_separator)

# -----------------------------------------------------------------------------

class Project:
    bom_path: str
    pnp_fname: str
    __config: configparser.ConfigParser
    profile: Profile

    def __init__(self):
        self.bom_path = "bom_path"
        self.pnp_fname = "pnp_fname"

        # https://docs.python.org/3/library/configparser.html
        self.__config = configparser.ConfigParser()
        if os.path.isfile("boomer.ini"):
            self.__config.read('boomer.ini')
        else:
            self.__config['common'] = {
                "initial_dir": "",
            }

        self.profile = Profile(config=self.__config)

    def cfg_get_section(self, sect_name: str) -> configparser.SectionProxy:
        try:
            self.__config[sect_name]
        except:
            self.__config[sect_name] = {}

        return self.__config[sect_name]

    def get_projects(self) -> list[str]:
        projects = []
        for sect in self.__config.sections():
            if sect.startswith("project."):
                projects.append(sect.removeprefix("project."))

        return projects

    def cfg_get_profiles(self) -> list[str]:
        profiles = []
        for sect in self.__config.sections():
            if sect.startswith("profile."):
                profiles.append(sect.removeprefix("profile."))

        return profiles

    def cfg_save_project(self):
        section = self.cfg_get_section("project." + self.bom_path)
        section["pnp"] = self.pnp_fname
        section["profile"] = self.profile.name
        with open('boomer.ini', 'w') as f:
            self.__config.write(f)


# global instance
proj = Project()

# -----------------------------------------------------------------------------

class ProjectProfileFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        lbl_config = customtkinter.CTkLabel(self, text="BOM+PnP profile:")
        lbl_config.grid(row=0, column=0, pady=5, padx=5, sticky="")

        self.opt_profile_var = customtkinter.StringVar(value="")
        self.opt_profile = customtkinter.CTkOptionMenu(self, values=proj.cfg_get_profiles(),
                                                       command=self.opt_profile_event,
                                                       variable=self.opt_profile_var)
        self.opt_profile.grid(row=0, column=1, pady=5, padx=5, sticky="we")
        self.grid_columnconfigure(1, weight=1)

        btn_save_as = customtkinter.CTkButton(self, text="Save as...", command=self.button_save_event)
        btn_save_as.grid(row=0, column=3, pady=5, padx=5)

        btn_delete = customtkinter.CTkButton(self, text="Delete profile", command=self.button_del_event)
        btn_delete.grid(row=0, column=4, pady=5, padx=5)
        btn_delete.configure(state="disabled")

    def button_save_event(self):
        logging.debug("Save as...")
        dialog = customtkinter.CTkInputDialog(text="Save profile as:", title="BOM & PnP profile", )
        new_profile_name = dialog.get_input().strip()
        if len(new_profile_name) >= 3:
            proj.profile.name = new_profile_name
            proj.profile.save()
            proj.cfg_save_project()
            self.opt_profile.configure(values=proj.cfg_get_profiles())
            self.opt_profile_var = proj.profile.name
        else:
            logging.error("Profile name length must be 3 or more")

    def button_del_event(self):
        logging.debug("Del")
        # TODO:

    def opt_profile_event(self, new_profile: str):
        logging.debug(f"Select profile: {new_profile}")
        proj.profile.load(new_profile)
        proj.cfg_save_project()

# -----------------------------------------------------------------------------

class ProjectFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(1, weight=1)
        # self.grid_rowconfigure(0, weight=1)

        lbl_proj_path = customtkinter.CTkLabel(self, text="Project (BOM) path:")
        lbl_proj_path.grid(row=0, column=0, pady=5, padx=5, sticky="w")

        self.bom_paths = proj.get_projects()
        self.opt_bom_var = customtkinter.StringVar(value="")
        self.opt_bom_path = customtkinter.CTkOptionMenu(self, values=self.bom_paths,
                                                        command=self.opt_bom_event,
                                                        variable=self.opt_bom_var)
        self.opt_bom_path.grid(row=0, column=1, pady=5, padx=5, sticky="we")

        btn_browse = customtkinter.CTkButton(self, text="Browse...", command=self.button_browse_event)
        btn_browse.grid(row=0, column=2, pady=5, padx=5, sticky="e")

        # ---

        lbl_pnp_path = customtkinter.CTkLabel(self, text="Pick'n'Place file:")
        lbl_pnp_path.grid(row=1, column=0, pady=5, padx=5, sticky="w")

        self.pnp_names = []
        self.opt_pnp_var = customtkinter.StringVar(value="")
        self.opt_pnp_fname = customtkinter.CTkOptionMenu(self, values=self.pnp_names,
                                                        command=self.opt_pnp_event,
                                                        variable=self.opt_pnp_var)
        self.opt_pnp_fname.grid(row=1, column=1, pady=5, padx=5, sticky="we")
        self.opt_pnp_fname.configure(state="disabled")

        self.config_frame = ProjectProfileFrame(self)
        self.config_frame.grid(row=2, column=0, padx=5, pady=5, columnspan=3, sticky="we")
        # self.config_frame.configure(state="disabled")

    def find_pnp_files(self, bom_path: str):
        if os.path.isfile(bom_path):
            # load all files from the BOM directory to the PnP list
            bom_dir = os.path.dirname(bom_path)
            logging.debug("Search PnP in: {}".format(bom_dir))
            self.opt_pnp_var.set("")
            self.pnp_names = []
            for de in os.scandir(bom_dir):
                if de.path != bom_path:
                    # take only the file name
                    pnp_path = os.path.basename(de.path)
                    self.pnp_names.append(pnp_path)
            self.opt_pnp_fname.configure(values=self.pnp_names, state="enabled")
            # self.config_frame.configure(state="enabled")

    def opt_bom_event(self, bom_path: str):
        logging.debug(f"Open BOM: {bom_path}")
        self.opt_pnp_var.set("")
        if os.path.isfile(bom_path):
            proj.bom_path = bom_path
            self.opt_bom_var.set(bom_path)
            # set pnp
            self.find_pnp_files(bom_path)
            section = proj.cfg_get_section("project." + proj.bom_path)
            pnp_fname = section["pnp"] or "???"
            proj.pnp_fname = pnp_fname
            self.opt_pnp_var.set(pnp_fname)
            # set profile
            profile = section["profile"] or "???"
            self.config_frame.opt_profile_var.set(profile)

    def opt_pnp_event(self, pnp_fname: str):
        logging.debug(f"Select PnP: {pnp_fname}")
        # update config
        proj.pnp_fname = pnp_fname
        proj.cfg_save_project()

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
            if not bom_path in self.bom_paths:
                self.bom_paths.append(bom_path)
            self.opt_bom_path.configure(values=self.bom_paths)
            self.opt_bom_var.set(bom_path)

        self.find_pnp_files(bom_path)
        # update config
        proj.bom_path = bom_path
        proj.cfg_save_project()

# -----------------------------------------------------------------------------

class BOMView(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def load_bom(self, path: str, **kwargs):
        if path.endswith("xls"):
            logging.debug(f"Read BOM: {path}")
            text_grid = xls_reader.read_xls_sheet(path, **kwargs)
        elif path.endswith("xlsx"):
            logging.debug(f"Read BOM: {path}")
            text_grid = xlsx_reader.read_xlsx_sheet(path, **kwargs)
        elif path.endswith("csv"):
            delim = proj.profile.get_bom_delimiter()
            logging.debug(f"Read BOM: {path}, delim={delim}")
            text_grid = csv_reader.read_csv(path, delim)
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
    bom_view: BOMView

    def __init__(self, master, **kwargs):
        assert "bom_view" in kwargs
        self.bom_view = kwargs.pop("bom_view")
        assert isinstance(self.bom_view, BOMView)

        super().__init__(master, **kwargs)

        lbl_separator = customtkinter.CTkLabel(self, text="CSV Separator:")
        lbl_separator.grid(row=0, column=0, pady=5, padx=5, sticky="")

        opt_separator = customtkinter.CTkOptionMenu(self, values=["COMMA", "SEMICOLON", "TAB", "FIXED-WIDTH"], command=self.opt_separator_event)
        opt_separator.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        self.btn_save = customtkinter.CTkButton(self, text="Save", command=self.button_save_event)
        self.btn_save.grid(row=0, column=2, pady=5, padx=5, sticky="")
        self.btn_save.configure(state="disabled")

        self.btn_load = customtkinter.CTkButton(self, text="Load BOM", command=self.button_load_event)
        self.btn_load.grid(row=0, column=3, pady=5, padx=5, columnspan=2, sticky="e")
        self.grid_columnconfigure(3, weight=1)

    def opt_separator_event(self, new_sep: str):
        logging.debug(f"BOM separator: {new_sep}")
        proj.profile.bom_separator = new_sep
        self.btn_save.configure(state="enabled")

    def button_save_event(self):
        self.btn_save.configure(state="disabled")
        proj.profile.save()
        logging.debug("Profile saved")

    def button_load_event(self):
        logging.debug("Load BOM...")
        self.bom_view.load_bom(proj.bom_path)

# -----------------------------------------------------------------------------

class PnPView(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.textbox = customtkinter.CTkTextbox(self,
                                                font=customtkinter.CTkFont(size=12, family="Consolas"),
                                                activate_scrollbars=True,
                                                wrap='none')
        self.textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        # self.textbox.insert("0.0", "𝐓𝐞𝐱𝐭 𝐄𝐝𝐢𝐭𝐨𝐫, 𝕋𝕖𝕩𝕥 𝔼𝕕𝕚𝕥𝕠𝕣")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def load_pnp(self, path: str):
        if not os.path.isfile(path):
            logging.error(f"File '{path}' does not exists")
            return

        delim = proj.profile.get_pnp_delimiter()
        logging.debug(f"Read PnP: {path}, delim={delim}")
        text_grid = csv_reader.read_csv(path, delim)
        logging.info("Read PnP: {} rows x {} cols".format(text_grid.nrows, text_grid.ncols))

        col_max_w = [0 for _ in range(text_grid.ncols)]
        for r, row in enumerate(text_grid.rows):
            if r >= proj.profile.pnp_first_row:
                for c, cell in enumerate(row):
                    max_w = col_max_w[c]
                    cell_w = len(cell)
                    if cell_w > max_w:
                        col_max_w[c] = cell_w

        # logging.debug("Max col width: {}".format(col_max_w))

        pnp_text_grid = ""
        for r, row in enumerate(text_grid.rows):
            if r >= proj.profile.pnp_first_row:
                pnp_row = "{:0>3} | ".format(r+1)
                for c, cell in enumerate(row):
                    to_fill = col_max_w[c] - len(cell)
                    fill = " " * to_fill if to_fill > 0 else ""
                    cell = cell + fill + " | "
                    pnp_row = pnp_row + cell
                pnp_text_grid = pnp_text_grid + pnp_row + "\n"

        self.textbox.delete("0.0", tkinter.END)
        self.textbox.insert("0.0", pnp_text_grid)
        logging.info("PnP ready")

# -----------------------------------------------------------------------------

class PnPConfig(customtkinter.CTkFrame):
    pnp_view: PnPView

    def __init__(self, master, **kwargs):
        assert "pnp_view" in kwargs
        self.pnp_view = kwargs.pop("pnp_view")
        assert isinstance(self.pnp_view, PnPView)

        super().__init__(master, **kwargs)

        lbl_separator = customtkinter.CTkLabel(self, text="CSV Separator:")
        lbl_separator.grid(row=0, column=0, pady=5, padx=5, sticky="")

        opt_separator = customtkinter.CTkOptionMenu(self, values=Profile.get_sepatators(), command=self.opt_separator_event)
        opt_separator.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        # self.grid_columnconfigure(1, weight=1)

        self.btn_save = customtkinter.CTkButton(self, text="Save", command=self.button_save_event)
        self.btn_save.grid(row=0, column=2, pady=5, padx=5, sticky="")
        self.btn_save.configure(state="disabled")

        lbl_first_row = customtkinter.CTkLabel(self, text="1st row:")
        lbl_first_row.grid(row=0, column=3, padx=5, pady=5, sticky="")

        opt_first_row = customtkinter.CTkOptionMenu(self, values=[str(i) for i in range(1, 20)], command=self.opt_first_row_event)
        opt_first_row.grid(row=0, column=4, padx=5, pady=5, sticky="we")

        self.btn_load = customtkinter.CTkButton(self, text="Load PnP", command=self.button_load_event)
        self.btn_load.grid(row=0, column=5, pady=5, padx=5, columnspan=2, sticky="e")
        self.grid_columnconfigure(5, weight=1)

    def opt_separator_event(self, new_sep: str):
        logging.debug(f"PnP separator: {new_sep}")
        proj.profile.pnp_separator = new_sep
        self.btn_save.configure(state="enabled")

    def opt_first_row_event(self, new_first_row: str):
        logging.debug(f"PnP 1st row: {new_first_row}")
        proj.profile.pnp_first_row = int(new_first_row.strip()) - 1

    def button_save_event(self):
        self.btn_save.configure(state="disabled")
        proj.profile.save()
        logging.debug("Profile saved")

    def button_load_event(self):
        logging.debug("Load PnP...")
        pnp_path = os.path.dirname(proj.bom_path) + "/" + proj.pnp_fname
        self.pnp_view.load_pnp(pnp_path)

# -----------------------------------------------------------------------------

class CtkApp(customtkinter.CTk):
    def __init__(self):
        logging.info('Ctk app is starting')
        super().__init__()

        self.title("BOM + PnP verifier")
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
        self.bom_view = BOMView(tab_bom)
        self.bom_view.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        self.bom_config = BOMConfig(tab_bom, bom_view=self.bom_view)
        self.bom_config.grid(row=1, column=0, pady=5, padx=5, sticky="we")

        tab_bom.grid_columnconfigure(0, weight=1)
        tab_bom.grid_rowconfigure(0, weight=1)

        # panel with the PnP
        self.pnp_view = PnPView(tab_pnp)
        self.pnp_view.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        self.pnp_config = PnPConfig(tab_pnp, pnp_view=self.pnp_view)
        self.pnp_config.grid(row=1, column=0, padx=5, pady=5, sticky="we")

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

    ctkapp = CtkApp()
    ctkapp.mainloop()
