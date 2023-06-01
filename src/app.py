# BOM & PnP verifier
#
# The purpose of this application is to read the PCB BillOfMaterial file
# together with the correcponding PickAndPlace file(s), and check the contents against
# differences in an electronic parts listed in both files, plus verify if the
# parts comments (values) matches.
#
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
import text_grid
import report_generator
from column_selector import ColumnsSelectorWindow, ColumnsSelectorResult
from prj_profile import Profile
import ui_helpers

# -----------------------------------------------------------------------------

class Project:
    bom_path: str
    pnp_fname: str
    pnp2_fname: str
    __config: configparser.ConfigParser
    profile: Profile
    bom_grid: text_grid.TextGrid = None
    pnp_grid: text_grid.TextGrid = None

    def __init__(self):
        self.bom_path = "<bom_path>"
        self.pnp_fname = "<pnp_fname>"
        self.pnp2_fname = ""

        # https://docs.python.org/3/library/configparser.html
        self.__config = configparser.ConfigParser()
        if os.path.isfile(Profile.CONFIG_FILE_NAME):
            self.__config.read(Profile.CONFIG_FILE_NAME)
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

    def del_project(self, name: str):
        sect_name = "project." + name
        if sect_name in self.__config.sections():
            self.__config.remove_section(sect_name)
            with open(Profile.CONFIG_FILE_NAME, 'w') as f:
                self.__config.write(f)
        else:
            logging.warning(f"Project '{name}' not found")

    def cfg_get_profiles(self) -> list[str]:
        profiles = []
        for sect in self.__config.sections():
            if sect.startswith("profile."):
                profiles.append(sect.removeprefix("profile."))

        return profiles

    def cfg_save_project(self):
        section = self.cfg_get_section("project." + self.bom_path)
        section["pnp"] = self.pnp_fname
        section["pnp2"] = self.pnp2_fname or ""
        section["profile"] = self.profile.name
        with open(Profile.CONFIG_FILE_NAME, 'w') as f:
            self.__config.write(f)

# global instance
proj = Project()

# -----------------------------------------------------------------------------

class ProjectProfileFrame(customtkinter.CTkFrame):
    # project_frame: ProjectFrame = None

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
        if '[' in new_profile_name or ']' in new_profile_name:
            logging.error("Profile name cannot contain square bracket characters: []")
            return

        if len(new_profile_name) >= 3:
            old_name = proj.profile.name
            proj.profile.name = new_profile_name
            proj.profile.save()
            # restore original profile name, not touching the project configuration
            proj.profile.name = old_name
        else:
            logging.error("Profile name length must be 3 or more")

    def button_del_event(self):
        logging.debug("Del profile")
        # TODO:

    def opt_profile_event(self, new_profile: str):
        logging.debug(f"Select profile: {new_profile}")
        proj.profile.load(new_profile)
        proj.cfg_save_project()
        self.project_frame.config_frames_load_profile()

# -----------------------------------------------------------------------------

class ProjectFrame(customtkinter.CTkFrame):
    # bom_config: BOMConfig = None
    # pnp_config: PnPConfig = None
    # bom_view: BOMView = None
    # pnp_view: PnPView = None
    # report_view: ReportView = None
    bom_config = None
    pnp_config = None
    bom_view = None
    pnp_view = None
    report_view = None

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

        btn_browse = customtkinter.CTkButton(self, text="Remove\nfrom list", command=self.button_remove_event)
        btn_browse.grid(row=0, column=3, pady=5, padx=5, sticky="e")

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


        lbl_pnp2_path = customtkinter.CTkLabel(self, text="PnP2 (optional):")
        lbl_pnp2_path.grid(row=2, column=0, pady=5, padx=5, sticky="w")

        self.opt_pnp2_var = customtkinter.StringVar(value="")
        self.opt_pnp2_fname = customtkinter.CTkOptionMenu(self, values=self.pnp_names,
                                                        command=self.opt_pnp2_event,
                                                        variable=self.opt_pnp2_var)
        self.opt_pnp2_fname.grid(row=2, column=1, pady=5, padx=5, sticky="we")
        self.opt_pnp2_fname.configure(state="disabled")

        self.config_frame = ProjectProfileFrame(self)
        self.config_frame.grid(row=3, column=0, padx=5, pady=5, columnspan=2, sticky="we")
        self.config_frame.project_frame = self
        # self.config_frame.configure(state="disabled")

    def find_pnp_files(self, bom_path: str):
        if os.path.isfile(bom_path):
            # load all files from the BOM directory to the PnP list
            bom_dir = os.path.dirname(bom_path)
            logging.debug("Search PnP in: {}".format(bom_dir))
            self.opt_pnp_var.set("")
            self.pnp_names = [""]
            for de in os.scandir(bom_dir):
                logging.debug("PnP path: " + de.path)
                # take only the file name
                pnp_fname = os.path.basename(de.path)
                if pnp_fname != os.path.basename(bom_path):
                    self.pnp_names.append(pnp_fname)
            self.opt_pnp_fname.configure(values=self.pnp_names, state="enabled")
            self.opt_pnp2_fname.configure(values=self.pnp_names, state="enabled")
            # self.config_frame.configure(state="enabled")

    def opt_bom_event(self, bom_path: str):
        logging.debug(f"Open BOM: {bom_path}")
        self.opt_pnp_var.set("")
        self.opt_pnp2_var.set("")

        if os.path.isfile(bom_path):
            self.bom_view.clear_preview()
            self.pnp_view.clear_preview()
            self.report_view.clear_preview()

            proj.bom_path = bom_path
            self.opt_bom_var.set(bom_path)
            # set pnp
            self.find_pnp_files(bom_path)
            section = proj.cfg_get_section("project." + proj.bom_path)
            proj.pnp_fname = section.get("pnp", "???")
            self.opt_pnp_var.set(proj.pnp_fname)
            proj.pnp2_fname = section.get("pnp2", "")
            self.opt_pnp2_var.set(proj.pnp2_fname)
            # set profile
            profile_name = section["profile"] or "???"
            self.config_frame.opt_profile_var.set(profile_name)
            # load profile
            proj.profile.load(profile_name)
            self.config_frames_load_profile()

    def opt_pnp_event(self, pnp_fname: str):
        logging.debug(f"Select PnP: {pnp_fname}")
        # update config
        proj.pnp_fname = pnp_fname
        proj.cfg_save_project()

    def opt_pnp2_event(self, pnp_fname: str):
        logging.debug(f"Select PnP2: {pnp_fname}")
        # update config
        proj.pnp2_fname = pnp_fname
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
                ("All (*.*)", "*.*")
            ),
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

    def button_remove_event(self):
        logging.debug("Remove project from list")
        proj.del_project(self.opt_bom_var.get())
        self.opt_bom_var.set("")
        self.bom_paths = proj.get_projects()
        self.opt_bom_path.configure(values=self.bom_paths)

    def config_frames_load_profile(self):
        self.bom_config.load_profile()
        self.pnp_config.load_profile()

# -----------------------------------------------------------------------------

class BOMView(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.textbox = customtkinter.CTkTextbox(self,
                                                font=customtkinter.CTkFont(size=12, family="Consolas"),
                                                activate_scrollbars=True,
                                                wrap='none')
        self.textbox.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        # self.textbox.tag_config('highlight', background='white', foreground='red')

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.entry_search = customtkinter.CTkEntry(self, placeholder_text="search...")
        self.entry_search.grid(row=1, column=0, padx=5, pady=5, sticky="wens")

        self.btn_search = customtkinter.CTkButton(self, text="Find", command=self.button_find_event)
        self.btn_search.grid(row=1, column=1, pady=5, padx=5, sticky="we")

        self.lbl_occurences = customtkinter.CTkLabel(self, text="Found: 0")
        self.lbl_occurences.grid(row=1, column=2, pady=5, padx=5, sticky="")

    def load_bom(self, path: str, **kwargs):
        if not os.path.isfile(path):
            logging.error(f"File '{path}' does not exists")
            return

        if path.endswith("xls"):
            logging.debug(f"Read BOM: {path}")
            proj.bom_grid = xls_reader.read_xls_sheet(path, **kwargs)
        elif path.endswith("xlsx"):
            logging.debug(f"Read BOM: {path}")
            proj.bom_grid = xlsx_reader.read_xlsx_sheet(path, **kwargs)
        elif path.endswith("csv"):
            delim = proj.profile.get_bom_delimiter()
            logging.debug(f"Read BOM: {path}, delim='{delim}'")
            proj.bom_grid = csv_reader.read_csv(path, delim)
        else:
            raise RuntimeError("Unknown file type")

        logging.info("Read BOM: {} rows x {} cols".format(proj.bom_grid.nrows, proj.bom_grid.ncols))

        bom_txt_grid = proj.bom_grid.format_grid(proj.profile.bom_first_row, proj.profile.bom_last_row)
        self.clear_preview()
        self.textbox.insert("0.0", bom_txt_grid)
        logging.info("BOM ready")

    def clear_preview(self):
        self.textbox.delete("0.0", tkinter.END)

    def button_find_event(self):
        txt = self.entry_search.get()
        logging.info(f"Find '{txt}'")
        cnt = ui_helpers.textbox_find_text(self.textbox, txt)
        self.lbl_occurences.configure(text=f"Found: {cnt}")
        # logging.debug(f"Found {cnt} occurences")

# -----------------------------------------------------------------------------

class BOMConfig(customtkinter.CTkFrame):
    bom_view: BOMView = None
    column_selector: ColumnsSelectorWindow = None

    def __init__(self, master, **kwargs):
        assert "bom_view" in kwargs
        self.bom_view = kwargs.pop("bom_view")
        assert isinstance(self.bom_view, BOMView)

        super().__init__(master, **kwargs)

        #
        lbl_separator = customtkinter.CTkLabel(self, text="CSV\nSeparator:")
        lbl_separator.grid(row=0, column=0, pady=5, padx=5, sticky="")

        self.opt_separator_var = customtkinter.StringVar(value="")
        opt_separator = customtkinter.CTkOptionMenu(self, values=Profile.get_separator_names(),
                                                    command=self.opt_separator_event,
                                                    variable=self.opt_separator_var)
        opt_separator.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        #
        # https://stackoverflow.com/questions/6548837/how-do-i-get-an-event-callback-when-a-tkinter-entry-widget-is-modified
        self.entry_first_row_var = customtkinter.StringVar(value="1")
        self.entry_first_row_var.trace_add("write", lambda n, i, m, sv=self.entry_first_row_var: self.var_first_row_event(sv))
        self.entry_first_row = customtkinter.CTkEntry(self, placeholder_text="first row", textvariable=self.entry_first_row_var)
        self.entry_first_row.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        #
        self.entry_last_row_var = customtkinter.StringVar(value="")
        self.entry_last_row_var.trace_add("write", lambda n, i, m, sv=self.entry_last_row_var: self.var_last_row_event(sv))
        self.entry_last_row = customtkinter.CTkEntry(self, placeholder_text="last row", textvariable=self.entry_last_row_var)
        self.entry_last_row.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        #
        self.btn_load = customtkinter.CTkButton(self, text="Reload BOM",
                                                command=self.button_load_event)
        self.btn_load.grid(row=0, column=6, pady=5, padx=5, sticky="e")

        #
        self.lbl_columns = customtkinter.CTkLabel(self, text="", justify="left")
        self.lbl_columns.grid(row=0, column=7, pady=5, padx=(15,5), sticky="w")
        self.update_lbl_columns()

        self.btn_columns = customtkinter.CTkButton(self, text="Select\ncolumns...",
                                                   command=self.button_columns_event)
        self.btn_columns.grid(row=0, column=8, pady=5, padx=5, sticky="")

        #
        self.btn_save = customtkinter.CTkButton(self, text="Save profile",
                                                command=self.button_save_event)
        self.btn_save.grid(row=0, column=9, pady=5, padx=5, sticky="e")
        self.btn_save.configure(state="disabled")
        self.grid_columnconfigure(9, weight=1)

    def load_profile(self):
        self.opt_separator_var.set(proj.profile.bom_separator)
        self.entry_first_row_var.set(str(proj.profile.bom_first_row + 1))
        self.entry_last_row_var.set("" if proj.profile.bom_last_row == -1 else str(proj.profile.bom_last_row))
        self.bom_view.clear_preview()
        self.update_lbl_columns()

    def update_lbl_columns(self):
        self.lbl_columns.configure(text=f"COLUMNS:\n• {proj.profile.bom_designator_col}\n• {proj.profile.bom_comment_col}")

    def opt_separator_event(self, new_sep: str):
        logging.debug(f"BOM separator: {new_sep}")
        proj.profile.bom_separator = new_sep
        self.btn_save.configure(state="enabled")
        self.button_load_event()

    def var_first_row_event(self, sv: customtkinter.StringVar):
        new_first_row = sv.get().strip()
        try:
            proj.profile.bom_first_row = int(new_first_row) - 1
            self.btn_save.configure(state="enabled")

            logging.debug(f"BOM 1st row: {proj.profile.bom_first_row+1}")
            self.button_load_event()
        except Exception as e:
            logging.error(f"Invalid row number: {e}")

    def var_last_row_event(self, sv: customtkinter.StringVar):
        new_last_row = sv.get().strip()
        try:
            # last row is optional, so it may be an empty string
            if new_last_row == "":
                proj.profile.bom_last_row = -1
            else:
                proj.profile.bom_last_row = int(new_last_row) - 1

            logging.debug(f"BOM last row: {proj.profile.bom_last_row+1}")
            self.button_load_event()
        except Exception as e:
            logging.error(f"Invalid row number: {e}")

    def button_columns_event(self):
        logging.debug("Select BOM columns...")
        if proj.bom_grid and len(proj.bom_grid.rows) >= proj.profile.bom_first_row:
            columns = proj.bom_grid.rows[proj.profile.bom_first_row]
        else:
            columns = ["..."]

        if self.column_selector:
            self.column_selector.destroy()
        self.column_selector = ColumnsSelectorWindow(self, columns=columns, callback=self.column_selector_callback)
        # self.wnd_column_selector.focusmodel(model="active")

    def column_selector_callback(self, result: ColumnsSelectorResult):
        logging.info(f"Selected BOM columns: des='{result.designator_col}', cmnt='{result.comment_col}'")
        proj.profile.bom_designator_col = result.designator_col
        proj.profile.bom_comment_col = result.comment_col
        self.update_lbl_columns()
        self.btn_save.configure(state="enabled")

    def button_save_event(self):
        self.btn_save.configure(state="disabled")
        proj.profile.save()
        logging.debug("Profile saved")

    def button_load_event(self):
        logging.debug("Load BOM...")
        try:
            self.bom_view.load_bom(proj.bom_path)
        except Exception as e:
            logging.error(f"Cannot load BOM: {e}")

# -----------------------------------------------------------------------------

class PnPView(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.textbox = customtkinter.CTkTextbox(self,
                                                font=customtkinter.CTkFont(size=12, family="Consolas"),
                                                activate_scrollbars=True,
                                                wrap='none')
        self.textbox.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.entry_search = customtkinter.CTkEntry(self, placeholder_text="search...")
        self.entry_search.grid(row=1, column=0, padx=5, pady=5, sticky="wens")

        self.btn_search = customtkinter.CTkButton(self, text="Find", command=self.button_find_event)
        self.btn_search.grid(row=1, column=1, pady=5, padx=5, sticky="we")

        self.lbl_occurences = customtkinter.CTkLabel(self, text="Found: 0")
        self.lbl_occurences.grid(row=1, column=2, pady=5, padx=5, sticky="")

    def load_pnp(self, path: str, path2: str):
        if not os.path.isfile(path):
            raise Exception(f"File '{path}' does not exists")

        # optional second PnP file
        if path2 != "" and not os.path.isfile(path2):
            raise Exception(f"File '{path2}' does not exists")

        delim = proj.profile.get_pnp_delimiter()
        logging.debug(f"Read PnP: {path}, delim='{delim}'")
        proj.pnp_grid = csv_reader.read_csv(path, delim)
        logging.info("Read PnP: {} rows x {} cols".format(proj.pnp_grid.nrows, proj.pnp_grid.ncols))

        if path2 != "":
            logging.debug(f"Read PnP2: {path2}, delim='{delim}'")
            pnp2_grid = csv_reader.read_csv(path2, delim)
            logging.info("Read PnP2: {} rows x {} cols".format(pnp2_grid.nrows, pnp2_grid.ncols))
            # merge
            if pnp2_grid.ncols != proj.pnp_grid.ncols:
                raise Exception("PnP has {} columns, but PnP2 has {} columns".format(proj.pnp_grid.ncols, pnp2_grid.ncols))
            proj.pnp_grid.nrows += pnp2_grid.nrows
            proj.pnp_grid.rows.extend(pnp2_grid.rows)

        pnp_txt_grid = proj.pnp_grid.format_grid(proj.profile.pnp_first_row, proj.profile.pnp_last_row)
        self.clear_preview()
        self.textbox.insert("0.0", pnp_txt_grid)
        logging.info("PnP ready")

    def clear_preview(self):
        self.textbox.delete("0.0", tkinter.END)

    def button_find_event(self):
        txt = self.entry_search.get()
        logging.info(f"Find '{txt}'")
        cnt = ui_helpers.textbox_find_text(self.textbox, txt)
        self.lbl_occurences.configure(text=f"Found: {cnt}")
        # logging.debug(f"Found {cnt} occurences")

# -----------------------------------------------------------------------------

class PnPConfig(customtkinter.CTkFrame):
    pnp_view: PnPView = None
    column_selector: ColumnsSelectorWindow = None

    def __init__(self, master, **kwargs):
        assert "pnp_view" in kwargs
        self.pnp_view = kwargs.pop("pnp_view")
        assert isinstance(self.pnp_view, PnPView)

        super().__init__(master, **kwargs)

        #
        lbl_separator = customtkinter.CTkLabel(self, text="CSV\nSeparator:")
        lbl_separator.grid(row=0, column=0, pady=5, padx=5, sticky="")

        self.opt_separator_var = customtkinter.StringVar(value="")
        opt_separator = customtkinter.CTkOptionMenu(self, values=Profile.get_separator_names(),
                                                    command=self.opt_separator_event,
                                                    variable=self.opt_separator_var)
        opt_separator.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        #
        # https://stackoverflow.com/questions/6548837/how-do-i-get-an-event-callback-when-a-tkinter-entry-widget-is-modified
        self.entry_first_row_var = customtkinter.StringVar(value="1")
        self.entry_first_row_var.trace_add("write", lambda n, i, m, sv=self.entry_first_row_var: self.var_first_row_event(sv))
        self.entry_first_row = customtkinter.CTkEntry(self, placeholder_text="first row", textvariable=self.entry_first_row_var)
        self.entry_first_row.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        #
        self.entry_last_row_var = customtkinter.StringVar(value="")
        self.entry_last_row_var.trace_add("write", lambda n, i, m, sv=self.entry_last_row_var: self.var_last_row_event(sv))
        self.entry_last_row = customtkinter.CTkEntry(self, placeholder_text="last row", textvariable=self.entry_last_row_var)
        self.entry_last_row.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        #
        self.btn_load = customtkinter.CTkButton(self, text="Reload PnP",
                                                command=self.button_load_event)
        self.btn_load.grid(row=0, column=6, pady=5, padx=5, sticky="e")

        #
        self.lbl_columns = customtkinter.CTkLabel(self, text="", justify="left")
        self.lbl_columns.grid(row=0, column=7, pady=5, padx=(15,5), sticky="w")
        self.update_lbl_columns()

        self.btn_columns = customtkinter.CTkButton(self, text="Select\ncolumn...",
                                                   command=self.button_columns_event)
        self.btn_columns.grid(row=0, column=8, pady=5, padx=5, sticky="")

        #
        self.btn_save = customtkinter.CTkButton(self, text="Save profile",
                                                command=self.button_save_event)
        self.btn_save.grid(row=0, column=9, pady=5, padx=5, sticky="e")
        self.btn_save.configure(state="disabled")
        self.grid_columnconfigure(9, weight=1)

    def load_profile(self):
        self.opt_separator_var.set(proj.profile.pnp_separator)
        self.entry_first_row_var.set(str(proj.profile.pnp_first_row + 1))
        self.entry_last_row_var.set("" if proj.profile.pnp_last_row == -1 else str(proj.profile.pnp_last_row))
        self.pnp_view.clear_preview()
        self.update_lbl_columns()

    def update_lbl_columns(self):
        self.lbl_columns.configure(text=f"COLUMNS:\n• {proj.profile.pnp_designator_col}\n• {proj.profile.pnp_comment_col}")

    def opt_separator_event(self, new_sep: str):
        logging.debug(f"PnP separator: {new_sep}")
        proj.profile.pnp_separator = new_sep
        self.btn_save.configure(state="enabled")
        self.button_load_event()

    def var_first_row_event(self, sv: customtkinter.StringVar):
        new_first_row = sv.get().strip()
        try:
            proj.profile.pnp_first_row = int(new_first_row) - 1
            self.btn_save.configure(state="enabled")

            logging.debug(f"PnP 1st row: {proj.profile.pnp_first_row+1}")
            self.button_load_event()
        except Exception as e:
            logging.error(f"Invalid row number: {e}")

    def var_last_row_event(self, sv: customtkinter.StringVar):
        new_last_row = sv.get().strip()
        try:
            # last row is optional, so it may be an empty string
            if new_last_row == "":
                proj.profile.pnp_last_row = -1
            else:
                proj.profile.pnp_last_row = int(new_last_row) - 1

            logging.debug(f"PnP last row: {proj.profile.pnp_last_row+1}")
            self.button_load_event()
        except Exception as e:
            logging.error(f"Invalid row number: {e}")

    def button_columns_event(self):
        logging.debug("Select PnP columns...")
        if proj.pnp_grid and len(proj.pnp_grid.rows) >= proj.profile.pnp_first_row:
            columns = proj.pnp_grid.rows[proj.profile.pnp_first_row]
        else:
            columns = ["..."]

        if self.column_selector:
            self.column_selector.destroy()
        self.column_selector = ColumnsSelectorWindow(self, columns=columns, callback=self.column_selector_callback)
        # self.wnd_column_selector.focusmodel(model="active")

    def column_selector_callback(self, result: ColumnsSelectorResult):
        logging.info(f"Selected PnP designator column: '{result.designator_col}'")

        proj.profile.pnp_designator_col = result.designator_col
        proj.profile.pnp_comment_col = result.comment_col
        self.update_lbl_columns()
        self.btn_save.configure(state="enabled")

    def button_save_event(self):
        self.btn_save.configure(state="disabled")
        proj.profile.save()
        logging.debug("Profile saved")

    def button_load_event(self):
        logging.debug("Load PnP...")
        pnp_path = os.path.join(os.path.dirname(proj.bom_path), proj.pnp_fname)
        pnp2_path = "" if proj.pnp2_fname == "" else os.path.join(os.path.dirname(proj.bom_path), proj.pnp2_fname)
        try:
            self.pnp_view.load_pnp(pnp_path, pnp2_path)
        except Exception as e:
            logging.error(f"Cannot load PnP: {e}")

# -----------------------------------------------------------------------------

class ReportView(customtkinter.CTkFrame):
    txt_grid: text_grid.TextGrid = None

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.textbox = customtkinter.CTkTextbox(self,
                                                font=customtkinter.CTkFont(size=12, family="Consolas"),
                                                activate_scrollbars=True,
                                                wrap='none')
        self.textbox.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        # self.textbox.insert("0.0", "𝐓𝐞𝐱𝐭 𝐄𝐝𝐢𝐭𝐨𝐫, 𝕋𝕖𝕩𝕥 𝔼𝕕𝕚𝕥𝕠𝕣")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.btn_analyze = customtkinter.CTkButton(self, text="Analyze documents", command=self.button_analyze_event)
        self.btn_analyze.grid(row=1, column=0, pady=5, padx=5, sticky="we")

        self.entry_search = customtkinter.CTkEntry(self, placeholder_text="search...")
        self.entry_search.grid(row=1, column=1, padx=5, pady=5, sticky="wens")

        self.btn_search = customtkinter.CTkButton(self, text="Find", command=self.button_find_event)
        self.btn_search.grid(row=1, column=2, pady=5, padx=5, sticky="we")

        self.lbl_occurences = customtkinter.CTkLabel(self, text="Found: 0")
        self.lbl_occurences.grid(row=1, column=3, pady=5, padx=5, sticky="")

    def clear_preview(self):
        self.textbox.delete("0.0", tkinter.END)

    def button_analyze_event(self):
        self.clear_preview()

        bom_cfg = text_grid.ConfiguredTextGrid()
        bom_cfg.text_grid = proj.bom_grid
        bom_cfg.designator_col = proj.profile.bom_designator_col
        bom_cfg.comment_col = proj.profile.bom_comment_col
        bom_cfg.first_row = proj.profile.bom_first_row
        bom_cfg.last_row = proj.profile.bom_last_row

        pnp_cfg = text_grid.ConfiguredTextGrid()
        pnp_cfg.text_grid = proj.pnp_grid
        pnp_cfg.designator_col = proj.profile.pnp_designator_col
        pnp_cfg.comment_col = proj.profile.pnp_comment_col
        pnp_cfg.first_row = proj.profile.pnp_first_row
        pnp_cfg.last_row = proj.profile.pnp_last_row

        rg = report_generator.ReportGenerator(bom_cfg, pnp_cfg)
        try:
            report = rg.analyze()
            self.textbox.insert("0.0", report)
        except Exception as e:
            logging.error(f"Report error: {e}")

    def button_find_event(self):
        txt = self.entry_search.get()
        logging.info(f"Find '{txt}'")
        cnt = ui_helpers.textbox_find_text(self.textbox, txt)
        self.lbl_occurences.configure(text=f"Found: {cnt}")
        # logging.debug(f"Found {cnt} occurences")

# -----------------------------------------------------------------------------

class CtkApp(customtkinter.CTk):
    def __init__(self):
        logging.info('Ctk app is starting')
        super().__init__()

        self.title("BOM & PnP verifier")
        self.geometry("1200x600")
        self.grid_columnconfigure(0, weight=1)

        # panel with Proj/BOM/PnP/Result
        tabview = customtkinter.CTkTabview(self)
        tabview.grid(row=1, column=0, padx=5, pady=5, sticky="wens")
        self.grid_rowconfigure(1, weight=1) # set row 1 height to all remaining space
        tab_prj = tabview.add("Project")
        tab_bom = tabview.add("Bill Of Materials")
        tab_pnp = tabview.add("Pick And Place")
        tab_report = tabview.add("Comparison Report")
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
        proj_frame.bom_config = self.bom_config
        proj_frame.bom_view = self.bom_view

        tab_bom.grid_columnconfigure(0, weight=1)
        tab_bom.grid_rowconfigure(0, weight=1)

        # panel with the PnP
        self.pnp_view = PnPView(tab_pnp)
        self.pnp_view.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        self.pnp_config = PnPConfig(tab_pnp, pnp_view=self.pnp_view)
        self.pnp_config.grid(row=1, column=0, padx=5, pady=5, sticky="we")
        proj_frame.pnp_config = self.pnp_config
        proj_frame.pnp_view = self.pnp_view

        tab_pnp.grid_columnconfigure(0, weight=1)
        tab_pnp.grid_rowconfigure(0, weight=1)

        # panel with the report
        self.report_view = ReportView(tab_report)
        self.report_view.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        proj_frame.report_view = self.report_view

        tab_report.grid_columnconfigure(0, weight=1)
        tab_report.grid_rowconfigure(0, weight=1)

        # UI ready
        logging.info('Ready')

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # logger config with dimmed time
    # https://docs.python.org/3/howto/logging.html
    logging.basicConfig(format='\033[30m%(asctime)s\033[39m %(levelname)s: %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    # https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
    # logging.addLevelName(logging.INFO,    "\033[1;37m%s\033[1;0m" % logging.getLevelName(logging.INFO))
    logging.addLevelName(logging.DEBUG,   "%s"                    % "DEBUG")
    logging.addLevelName(logging.INFO,    "\033[1;37m%s\033[1;0m" % "INFO ")
    logging.addLevelName(logging.WARNING, "\033[1;33m%s\033[1;0m" % "WARN ")
    logging.addLevelName(logging.ERROR,   "\033[1;31m%s\033[1;0m" % "ERROR")

    # https://customtkinter.tomschimansky.com/documentation/appearancemode
    customtkinter.set_appearance_mode("light")
    customtkinter.set_default_color_theme("green")

    ctkapp = CtkApp()
    ctkapp.mainloop()
