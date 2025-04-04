# BOM & PnP verifier
#
# The purpose of this application is to read the PCB BillOfMaterial file
# together with the corresponding PickAndPlace file(s), and check the contents against
# differences in an electronic parts listed in both files, and additionally
# verify that the part comments (values) match.
#
# (c) 2023-2025 Mariusz Midor
# https://github.com/marmidr/boomer

import customtkinter
import tkinter
import os
import sys
import time
import klembord

import xls_reader
import xlsx_reader
import csv_reader
import ods_reader
import text_grid
import cross_check
import report_generator
from column_selector import ColumnsSelector, ColumnsSelectorResult
from project import *
from msg_box import MessageBox
import ui_helpers
import logger

# -----------------------------------------------------------------------------

APP_NAME = "BOM vs PnP Cross Checker v0.10.0"
APP_DATE = "(c) 2023-2025"

# -----------------------------------------------------------------------------

# global instance
proj = Project()

# -----------------------------------------------------------------------------

class ProjectProfileFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        lbl_config = customtkinter.CTkLabel(self, text="BOM+PnP profile:")
        lbl_config.grid(row=0, column=0, pady=5, padx=5, sticky="")

        profiles = proj.cfg_get_profiles()
        assert len(profiles) > 0
        self.opt_profile_var = customtkinter.StringVar(value=profiles[0])
        self.opt_profile = customtkinter.CTkOptionMenu(self, values=profiles,
                                                       command=self.opt_profile_event,
                                                       variable=self.opt_profile_var)
        self.opt_profile.grid(row=0, column=1, pady=5, padx=5, sticky="we")
        self.grid_columnconfigure(1, weight=1)

        btn_clone = customtkinter.CTkButton(self, text="Clone as...", command=self.button_clone_event)
        btn_clone.grid(row=0, column=3, pady=5, padx=5)

        btn_delete = customtkinter.CTkButton(self, text="Delete profile", command=self.button_del_event)
        btn_delete.grid(row=0, column=4, pady=5, padx=5)
        btn_delete.configure(state=tkinter.DISABLED)

    def button_clone_event(self):
        logger.debug("Clone profile as...")
        dialog = customtkinter.CTkInputDialog(text="Save profile as:", title="BOM & PnP profile", )
        # set the default value:
        time.sleep(0.1) # widgets are created with delay
        dialog.update()
        profilename = os.path.basename(os.path.dirname(proj.bom_path)) # project dir name as a new profile name
        dialog._entry.insert(0, profilename or "")
        new_profile_name = dialog.get_input().strip()

        if '[' in new_profile_name or ']' in new_profile_name:
            logger.error("Profile name cannot contain square bracket characters: []")
            return

        if len(new_profile_name) >= 3:
            old_name = proj.profile.name
            proj.profile.name = new_profile_name
            proj.profile.save()
            # restore original profile name, not touching the project configuration
            proj.profile.name = old_name
            # update list of profiles
            self.opt_profile.configure(values=proj.cfg_get_profiles())
        else:
            logger.error("Profile name length must be 3 or more")

    def button_del_event(self):
        prof = self.opt_profile_var.get()
        if prof != "":
            # FIXME: app behavior with this action is hardly predictable
            logger.debug(f"Del profile: {prof}")
            proj.del_profile(prof)
            self.opt_profile_var.set("")

    def opt_profile_event(self, new_profile: str):
        logger.info(f"Select profile: {new_profile}")
        proj.profile.load(new_profile)
        proj.cfg_save_project()
        try:
            # block the automatic loading of the files
            proj.loading = True
            self.project_frame.config_frames_load_profile()
        finally:
            proj.loading = False

# -----------------------------------------------------------------------------

class ProjectFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        assert "app" in kwargs
        self.app = kwargs.pop("app")

        super().__init__(master, **kwargs)

        self.bom_config = None
        self.pnp_config = None
        self.bom_view = None
        self.pnp_view = None
        self.report_view = None

        self.grid_columnconfigure(1, weight=1)
        # self.grid_rowconfigure(0, weight=1)

        lbl_proj_path = customtkinter.CTkLabel(self, text="Project (BOM) path:")
        lbl_proj_path.grid(row=0, column=0, pady=5, padx=5, sticky="w")

        self.bom_paths = proj.get_projects()
        self.opt_bom_var = customtkinter.StringVar(value="")
        self.opt_bom_path = customtkinter.CTkOptionMenu(self, values=self.bom_paths,
                                                        command=self.opt_bom_event,
                                                        variable=self.opt_bom_var)
        self.opt_bom_path.grid(row=0, column=1, pady=5, padx=5, columnspan=2, sticky="we")

        btn_browse = customtkinter.CTkButton(self, text="Browse...", command=self.button_browse_event)
        btn_browse.grid(row=0, column=3, pady=5, padx=5, sticky="e")

        btn_browse = customtkinter.CTkButton(self, text="Remove\nfrom list", command=self.button_remove_event)
        btn_browse.grid(row=0, column=5, pady=5, padx=5, sticky="e")

        # ---

        lbl_pnp_path = customtkinter.CTkLabel(self, text="Pick'n'Place file:")
        lbl_pnp_path.grid(row=1, column=0, pady=5, padx=5, sticky="w")

        self.pnp_names = []
        self.opt_pnp_var = customtkinter.StringVar(value="")
        self.opt_pnp_fname = customtkinter.CTkOptionMenu(self, values=self.pnp_names,
                                                        command=self.opt_pnp_event,
                                                        variable=self.opt_pnp_var)
        self.opt_pnp_fname.grid(row=1, column=1, pady=5, padx=5, sticky="we")
        self.opt_pnp_fname.configure(state=tkinter.DISABLED)


        lbl_pnp2_path = customtkinter.CTkLabel(self, text="PnP2 (optional):")
        lbl_pnp2_path.grid(row=2, column=0, pady=5, padx=5, sticky="w")

        self.opt_pnp2_var = customtkinter.StringVar(value="")
        self.opt_pnp2_fname = customtkinter.CTkOptionMenu(self, values=self.pnp_names,
                                                        command=self.opt_pnp2_event,
                                                        variable=self.opt_pnp2_var)
        self.opt_pnp2_fname.grid(row=2, column=1, pady=5, padx=5, sticky="we")
        self.opt_pnp2_fname.configure(state=tkinter.DISABLED)

        self.config_frame = ProjectProfileFrame(self)
        self.config_frame.grid(row=3, column=0, padx=5, pady=5, columnspan=2, sticky="we")
        self.config_frame.project_frame = self
        # self.config_frame.configure(state=tkinter.DISABLED)

        #
        self.config_logs = customtkinter.CTkFrame(self)
        self.config_logs.grid(row=4, column=0, pady=5, padx=5, columnspan=1, sticky="wns")

        self.config_logs.lbl_font = customtkinter.CTkLabel(self.config_logs, text="Console:")
        self.config_logs.lbl_font.grid(row=0, column=0, pady=5, padx=5, sticky="w")

        self.config_logs.colorlogs_var = customtkinter.BooleanVar(value=proj.color_logs)
        self.config_logs.chx_color_logs = customtkinter.CTkCheckBox(self.config_logs,
                                                        text="Colorful logs",
                                                        command=self.checkbox_colorfulogs_event,
                                                        variable=self.config_logs.colorlogs_var,
                                                        checkbox_width=18, checkbox_height=18)
        self.config_logs.chx_color_logs.grid(row=1, column=0, pady=5, padx=5, sticky="w")

    def clear_previews(self):
        self.opt_pnp_var.set("")
        self.opt_pnp2_var.set("")
        self.bom_view.clear_preview()
        self.pnp_view.clear_preview()
        self.report_view.clear_preview()

    def find_pnp_files(self, bom_path: str):
        if os.path.isfile(bom_path):
            # load all files from the BOM directory to the PnP list
            bom_dir = os.path.dirname(bom_path)
            logger.debug(f"Search PnP in: {bom_dir}")
            self.opt_pnp_var.set("")
            self.pnp_names = [""]
            for de in os.scandir(bom_dir):
                # logger.debug("PnP path: " + de.path)
                # take only the file name
                pnp_fname = os.path.basename(de.path)
                if pnp_fname != os.path.basename(bom_path):
                    if not pnp_fname.lower().endswith(".html"):
                        self.pnp_names.append(pnp_fname)
            self.opt_pnp_fname.configure(values=self.pnp_names, state=tkinter.NORMAL)
            self.opt_pnp2_fname.configure(values=self.pnp_names, state=tkinter.NORMAL)
            # self.config_frame.configure(state=tkinter.NORMAL)

    def opt_bom_event(self, bom_path: str):
        # sourcery skip: extract-method, use-fstring-for-concatenation
        logger.debug(f"Open BOM: {bom_path}")
        self.clear_previews()

        # reset entire project
        global proj
        proj = Project()
        proj.loading = True

        try:
            if os.path.isfile(bom_path):
                proj.bom_path = bom_path
                self.opt_bom_var.set(bom_path)
                # set pnp file name
                self.find_pnp_files(bom_path)
                section = proj.get_section("project." + proj.bom_path)
                proj.pnp_fname = section.get("pnp", "???")
                self.opt_pnp_var.set(proj.pnp_fname)
                proj.pnp2_fname = section.get("pnp2", "")
                self.opt_pnp2_var.set(proj.pnp2_fname)
                # select profile name in the option
                profile_name = section["profile"] or "???"
                self.config_frame.opt_profile_var.set(profile_name)
                # load the profile
                proj.profile.load(profile_name)
                self.config_frames_load_profile()
            else:
                logger.error(f"File '{bom_path}' does not exists")
        except Exception as e:
            logger.error(f"Cannot open project: {e}")
        finally:
            proj.loading = False

    def opt_pnp_event(self, pnp_fname: str):
        logger.debug(f"Select PnP: {pnp_fname}")
        # update config
        proj.pnp_fname = pnp_fname
        proj.cfg_save_project()

    def opt_pnp2_event(self, pnp_fname: str):
        logger.debug(f"Select PnP2: {pnp_fname}")
        # update config
        proj.pnp2_fname = pnp_fname
        proj.cfg_save_project()

    def button_browse_event(self):  # sourcery skip: de-morgan, extract-method
        logger.debug("Browse BOM")
        self.clear_previews()

        # https://docs.python.org/3/library/dialog.html
        # TODO: get the initial dir from the proj settings
        bom_path = tkinter.filedialog.askopenfilename(
            title="Select BOM file",
            initialdir=None,
            filetypes=(
                ("Supported (*.xls; *.xlsx; *.csv; *.ods)", "*.xls; *.xlsx; *.csv; *.ods"),
                ("All (*.*)", "*.*")
            ),
        )
        logger.info(f"Selected path: {bom_path}")

        if os.path.isfile(bom_path):
            try:
                # reset entire project
                global proj
                proj = Project()
                proj.loading = True

                if not bom_path in self.bom_paths:
                    self.bom_paths.append(bom_path)
                self.opt_bom_path.configure(values=self.bom_paths)
                self.opt_bom_var.set(bom_path)
                self.find_pnp_files(bom_path)
                # update config
                proj.bom_path = bom_path
                proj.cfg_save_project()
                self.activate_csv_separator_for_bom_pnp()
            except Exception as e:
                logger.error(f"Cannot open project: {e}")
            finally:
                proj.loading = False
        else:
            logger.error(f"Cannot access the file '{bom_path}'")

    def button_remove_event(self):
        logger.debug("Remove project from list")
        proj.del_project(self.opt_bom_var.get())
        self.opt_bom_var.set("")
        self.bom_paths = proj.get_projects()
        self.opt_bom_path.configure(values=self.bom_paths)

    def checkbox_colorfulogs_event(self):
        proj.color_logs = self.config_logs.colorlogs_var.get()
        # logger.debug(f"CHBX event: {Config.instance().color_logs}")
        proj.save()

    def config_frames_load_profile(self):
        self.bom_config.load_profile()
        self.pnp_config.load_profile()
        self.activate_csv_separator_for_bom_pnp()

    def activate_csv_separator_for_bom_pnp(self):
        bom_path = proj.bom_path.lower()
        if bom_path.endswith("xls") or bom_path.endswith("xlsx") or bom_path.endswith("ods"):
            self.bom_config.opt_separator.configure(state=tkinter.DISABLED)
        else:
            self.bom_config.opt_separator.configure(state=tkinter.NORMAL)

        pnp_fname = proj.pnp_fname.lower()
        if pnp_fname.endswith("xls") or pnp_fname.endswith("xlsx") or pnp_fname.endswith("ods"):
            self.pnp_config.opt_separator.configure(state=tkinter.DISABLED)
        else:
            self.pnp_config.opt_separator.configure(state=tkinter.NORMAL)

# -----------------------------------------------------------------------------

class BOMView(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        assert "app" in kwargs
        self.app = kwargs.pop("app")

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
        self.clear_preview()

        if not os.path.isfile(path):
            raise FileNotFoundError(f"File '{path}' does not exists")

        path_lower = path.lower()
        if path_lower.endswith("xls"):
            proj.bom_grid = xls_reader.read_xls_sheet(path)
        elif path_lower.endswith("xlsx"):
            proj.bom_grid = xlsx_reader.read_xlsx_sheet(path)
        elif path_lower.endswith("ods"):
            proj.bom_grid = ods_reader.read_ods_sheet(path)
        elif path_lower.endswith("csv"):
            delim = proj.profile.bom_delimiter
            proj.bom_grid = csv_reader.read_csv(path, delim)
        else:
            raise RuntimeError("Unknown file type")

        logger.info(f"BOM: {proj.bom_grid.nrows} rows x {proj.bom_grid.ncols} cols")

        bom_txt_grid = proj.bom_grid.format_grid(proj.profile.bom_first_row, proj.profile.bom_last_row)
        self.textbox.insert("0.0", bom_txt_grid)
        proj.bom_grid_dirty = False

    def clear_preview(self):
        self.textbox.delete("0.0", tkinter.END)

    def button_find_event(self):
        txt = self.entry_search.get()
        logger.info(f"Find '{txt}'")
        cnt = ui_helpers.textbox_find_text(self.textbox, txt)
        self.lbl_occurences.configure(text=f"Found: {cnt}")

# -----------------------------------------------------------------------------

class BOMConfig(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        assert "app" in kwargs
        self.app = kwargs.pop("app")

        assert "bom_view" in kwargs
        self.bom_view: BOMView = kwargs.pop("bom_view")
        assert isinstance(self.bom_view, BOMView)
        # kwargs cleared from unexpected arguments -> call init
        super().__init__(master, **kwargs)

        self.column_selector: ColumnsSelector = None

        #
        lbl_separator = customtkinter.CTkLabel(self, text="CSV\nSeparator:")
        lbl_separator.grid(row=0, column=0, pady=5, padx=5, sticky="")

        self.opt_separator_var = customtkinter.StringVar(value="")
        self.opt_separator = customtkinter.CTkOptionMenu(self, values=Profile.get_separator_names(),
                                                    command=self.opt_separator_event,
                                                    variable=self.opt_separator_var)
        self.opt_separator.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        self.opt_separator.configure(state=tkinter.DISABLED)

        #
        # https://stackoverflow.com/questions/6548837/how-do-i-get-an-event-callback-when-a-tkinter-entry-widget-is-modified
        self.entry_first_row_var = customtkinter.StringVar(value="1")
        self.entry_first_row_var.trace_add("write", lambda n, i, m, sv=self.entry_first_row_var: self.var_first_row_event(sv))
        self.entry_first_row = customtkinter.CTkEntry(self, width=60, placeholder_text="first row", textvariable=self.entry_first_row_var)
        self.entry_first_row.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        #
        self.entry_last_row_var = customtkinter.StringVar(value="")
        self.entry_last_row_var.trace_add("write", lambda n, i, m, sv=self.entry_last_row_var: self.var_last_row_event(sv))
        self.entry_last_row = customtkinter.CTkEntry(self, width=60, placeholder_text="last row", textvariable=self.entry_last_row_var)
        self.entry_last_row.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        #
        self.btn_load = customtkinter.CTkButton(self, text="Reload BOM",
                                                command=self.button_load_event)
        self.btn_load.grid(row=0, column=6, pady=5, padx=5, sticky="e")

        #
        sep_v = tkinter.ttk.Separator(self, orient='vertical')
        sep_v.grid(row=0, column=7, pady=2, padx=5, sticky="ns")

        #
        self.lbl_columns = customtkinter.CTkLabel(self, text="", justify="left")
        self.lbl_columns.grid(row=0, column=8, pady=5, padx=(15,5), sticky="w")
        self.update_lbl_columns()

        self.btn_columns = customtkinter.CTkButton(self, text="Select\ncolumns...",
                                                   command=self.button_columns_event)
        self.btn_columns.grid(row=0, column=9, pady=5, padx=5, sticky="")
        self.btn_columns.configure(state=tkinter.DISABLED)

        #
        self.btn_save = customtkinter.CTkButton(self, text="Save profile",
                                                command=self.button_save_event)
        self.btn_save.grid(row=0, column=10, pady=5, padx=5, sticky="e")
        self.btn_save.configure(state=tkinter.DISABLED)
        self.grid_columnconfigure(10, weight=1)

    def load_profile(self):
        self.opt_separator_var.set(proj.profile.bom_separator)
        self.entry_first_row_var.set(str(proj.profile.bom_first_row + 1))
        self.entry_last_row_var.set("" if proj.profile.bom_last_row == -1 else str(proj.profile.bom_last_row))
        self.bom_view.clear_preview()
        self.update_lbl_columns()
        self.btn_save.configure(state=tkinter.DISABLED)
        self.btn_save.configure(text="Save profile" + "\n" + proj.profile.name)

    def update_lbl_columns(self):
        prepare_id = lambda id: id if type(id) is str else id+1
        self.lbl_columns.configure(text=f"COLUMNS:\n"\
                                    f"• DSGN: {prepare_id(proj.profile.bom_designator_col)}\n"\
                                    f"• CMNT: {prepare_id(proj.profile.bom_comment_col)}")

    def opt_separator_event(self, new_sep: str):
        logger.info(f"  BOM separator: {new_sep}")
        proj.profile.bom_separator = new_sep
        self.btn_save.configure(state=tkinter.NORMAL)
        self.button_load_event()

    def var_first_row_event(self, sv: customtkinter.StringVar):
        new_first_row = sv.get().strip()
        try:
            proj.profile.bom_first_row = int(new_first_row) - 1
            logger.info(f"  BOM 1st row: {proj.profile.bom_first_row+1}")
            self.btn_save.configure(state=tkinter.NORMAL)
            if not proj.loading:
                self.button_load_event()
        except Exception as e:
            logger.error(f"  Invalid row number: {e}")

    def var_last_row_event(self, sv: customtkinter.StringVar):
        new_last_row = sv.get().strip()
        try:
            # last row is optional, so it may be an empty string
            proj.profile.bom_last_row = -1 if new_last_row == "" else int(new_last_row) - 1
            logger.info(f"  BOM last row: {proj.profile.bom_last_row+1}")
            if not proj.loading:
                self.button_load_event()
        except Exception as e:
            logger.error(f"  Invalid row number: {e}")

    def button_columns_event(self):
        logger.debug("Select BOM columns...")
        if proj.bom_grid and len(proj.bom_grid.rows_raw()) >= proj.profile.bom_first_row:
            columns = proj.bom_grid.rows_raw()[proj.profile.bom_first_row]
        else:
            columns = ["..."]

        if self.column_selector:
            self.column_selector.destroy()
        self.column_selector = ColumnsSelector(self, app=self.app,
                                    columns=columns, callback=self.column_selector_callback,
                                    has_column_headers=proj.profile.bom_has_column_headers,
                                    designator_default=proj.profile.bom_designator_col,
                                    comment_default=proj.profile.bom_comment_col)

    def column_selector_callback(self, result: ColumnsSelectorResult):
        logger.info("Selected BOM columns: "\
                    f"dsgn='{result.designator_col}', cmnt='{result.comment_col}'")
        proj.profile.bom_designator_col = result.designator_col
        proj.profile.bom_comment_col = result.comment_col
        proj.profile.bom_has_column_headers = result.has_column_headers
        self.update_lbl_columns()
        self.btn_save.configure(state=tkinter.NORMAL)

    def button_save_event(self):
        if (n := proj.cfg_count_profile(proj.profile.name)) > 1:
            MessageBox(app=self.app, dialog_type="yn",
                        message=f"Profile '{proj.profile.name}' is used in {n} projects.\nDo you want to overwrite it?",
                        callback=self.onmsgbox_on_click)
            return

        self.btn_save.configure(state=tkinter.DISABLED)
        proj.profile.save()

    def onmsgbox_on_click(self, btn: str):
        if btn == "y":
            self.btn_save.configure(state=tkinter.DISABLED)
            proj.profile.save()
        else:
            logger.info("Profile NOT saved")

    def button_load_event(self):
        logger.debug("Load BOM...")
        self.btn_columns.configure(state=tkinter.NORMAL)
        try:
            self.bom_view.load_bom(proj.bom_path)
        except Exception as e:
            logger.error(f"Cannot load BOM: {e}")

# -----------------------------------------------------------------------------

class PnPView(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        assert "app" in kwargs
        self.app = kwargs.pop("app")

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
        # sourcery skip: extract-method, use-fstring-for-formatting
        self.clear_preview()

        if not os.path.isfile(path):
            raise FileNotFoundError(f"File '{path}' does not exists")

        # check if optional second PnP file exists
        if path2 != "" and not os.path.isfile(path2):
            raise FileNotFoundError(f"File '{path2}' does not exists")

        path_lower = path.lower()
        if path_lower.endswith("xls"):
            proj.pnp_grid = xls_reader.read_xls_sheet(path)
        elif path_lower.endswith("xlsx"):
            proj.pnp_grid = xlsx_reader.read_xlsx_sheet(path)
        elif path_lower.endswith("ods"):
            proj.pnp_grid = ods_reader.read_ods_sheet(path)
        else: # assume CSV
            delim = proj.profile.pnp_delimiter
            proj.pnp_grid = csv_reader.read_csv(path, delim)

        log_f = logger.info if proj.pnp_grid.nrows > 0 else logger.warning
        log_f(f"PnP: {proj.pnp_grid.nrows} rows x {proj.pnp_grid.ncols} cols")

        # load the optional second PnP file
        if path2 != "":
            path2_lower = path2.lower()
            if path2_lower.endswith("xls"):
                pnp2_grid = xls_reader.read_xls_sheet(path2)
            elif path2_lower.endswith("xlsx"):
                pnp2_grid = xlsx_reader.read_xlsx_sheet(path)
            elif path2_lower.endswith("ods"):
                pnp2_grid = ods_reader.read_ods_sheet(path2)
            else: # assume CSV
                delim = proj.profile.pnp_delimiter
                pnp2_grid = csv_reader.read_csv(path2, delim)

            log_f = logger.info if pnp2_grid.nrows > 0 else logger.warning
            log_f("PnP2: {} rows x {} cols".format(pnp2_grid.nrows, pnp2_grid.ncols))

            # merge
            if pnp2_grid.ncols != proj.pnp_grid.ncols:
                raise ValueError("PnP has {} columns, but PnP2 has {} columns".format(
                    proj.pnp_grid.ncols, pnp2_grid.ncols
                ))

            # add a layer column (only for 2 separate files)
            for row in proj.pnp_grid.rows_raw():
                row.append("top")
            for row in pnp2_grid.rows_raw():
                row.append("bot")

            proj.pnp_grid.nrows += pnp2_grid.nrows
            proj.pnp_grid.rows_raw().extend(pnp2_grid.rows_raw())

        pnp_txt_grid = proj.pnp_grid.format_grid(proj.profile.pnp_first_row, proj.profile.pnp_last_row)
        self.textbox.insert("0.0", pnp_txt_grid)
        proj.pnp_grid_dirty = False

    def clear_preview(self):
        self.textbox.delete("0.0", tkinter.END)

    def button_find_event(self):
        txt = self.entry_search.get()
        logger.info(f"Find '{txt}'")
        cnt = ui_helpers.textbox_find_text(self.textbox, txt)
        self.lbl_occurences.configure(text=f"Found: {cnt}")

# -----------------------------------------------------------------------------

class PnPConfig(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        assert "app" in kwargs
        self.app = kwargs.pop("app")

        assert "pnp_view" in kwargs
        self.pnp_view: PnPView = kwargs.pop("pnp_view")
        assert isinstance(self.pnp_view, PnPView)
        # kwargs cleared from unexpected arguments -> call init
        super().__init__(master, **kwargs)

        self.column_selector: ColumnsSelector = None

        #
        lbl_separator = customtkinter.CTkLabel(self, text="CSV\nSeparator:")
        lbl_separator.grid(row=0, column=0, pady=5, padx=5, sticky="")

        self.opt_separator_var = customtkinter.StringVar(value="")
        self.opt_separator = customtkinter.CTkOptionMenu(self, values=Profile.get_separator_names(),
                                                    command=self.opt_separator_event,
                                                    variable=self.opt_separator_var)
        self.opt_separator.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        self.opt_separator.configure(state=tkinter.DISABLED)

        #
        # https://stackoverflow.com/questions/6548837/how-do-i-get-an-event-callback-when-a-tkinter-entry-widget-is-modified
        self.entry_first_row_var = customtkinter.StringVar(value="1")
        self.entry_first_row_var.trace_add("write", lambda n, i, m, sv=self.entry_first_row_var: self.var_first_row_event(sv))
        self.entry_first_row = customtkinter.CTkEntry(self, width=60, placeholder_text="first row", textvariable=self.entry_first_row_var)
        self.entry_first_row.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        #
        self.entry_last_row_var = customtkinter.StringVar(value="")
        self.entry_last_row_var.trace_add("write", lambda n, i, m, sv=self.entry_last_row_var: self.var_last_row_event(sv))
        self.entry_last_row = customtkinter.CTkEntry(self, width=60, placeholder_text="last row", textvariable=self.entry_last_row_var)
        self.entry_last_row.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        #
        self.btn_load = customtkinter.CTkButton(self, text="Reload PnP",
                                                command=self.button_load_event)
        self.btn_load.grid(row=0, column=6, pady=5, padx=5, sticky="e")

        #
        sep_v = tkinter.ttk.Separator(self, orient='vertical')
        sep_v.grid(row=0, column=7, pady=2, padx=5, sticky="ns")

        #
        self.lbl_columns = customtkinter.CTkLabel(self, text="", justify="left")
        self.lbl_columns.grid(row=0, column=8, pady=5, padx=(15,5), sticky="w")
        self.update_lbl_columns()

        self.btn_columns = customtkinter.CTkButton(self, text="Select\ncolumn...",
                                                   command=self.button_columns_event)
        self.btn_columns.grid(row=0, column=9, pady=5, padx=5, sticky="")
        self.btn_columns.configure(state=tkinter.DISABLED)

        #
        self.btn_save = customtkinter.CTkButton(self, text="Save profile",
                                                command=self.button_save_event)
        self.btn_save.grid(row=0, column=10, pady=5, padx=5, sticky="e")
        self.btn_save.configure(state=tkinter.DISABLED)
        self.grid_columnconfigure(10, weight=1)

    def load_profile(self):
        self.opt_separator_var.set(proj.profile.pnp_separator)
        self.entry_first_row_var.set(str(proj.profile.pnp_first_row + 1))
        self.entry_last_row_var.set("" if proj.profile.pnp_last_row == -1 else str(proj.profile.pnp_last_row))
        self.pnp_view.clear_preview()
        self.update_lbl_columns()
        self.btn_save.configure(state=tkinter.DISABLED)
        self.btn_save.configure(text="Save profile" + "\n" + proj.profile.name)

    def update_lbl_columns(self):
        prepare_id = lambda id: id if type(id) is str else id+1
        self.lbl_columns.configure(text=f"COLUMNS:\n"\
            f"• DSGN: {prepare_id(proj.profile.pnp_designator_col)}\n"\
            f"• CMNT: {prepare_id(proj.profile.pnp_comment_col)}\n"\
            f"• X: {prepare_id(proj.profile.pnp_coord_x_col)} • Y: {prepare_id(proj.profile.pnp_coord_y_col)}\n"\
            f"• LR: {prepare_id(proj.profile.pnp_layer_col)}")

    def opt_separator_event(self, new_sep: str):
        logger.info(f"  PnP separator: {new_sep}")
        proj.profile.pnp_separator = new_sep
        self.btn_save.configure(state=tkinter.NORMAL)
        self.button_load_event()

    def var_first_row_event(self, sv: customtkinter.StringVar):
        new_first_row = sv.get().strip()
        try:
            proj.profile.pnp_first_row = int(new_first_row) - 1
            logger.info(f"  PnP 1st row: {proj.profile.pnp_first_row+1}")
            self.btn_save.configure(state=tkinter.NORMAL)
            if not proj.loading:
                self.button_load_event()
        except Exception as e:
            logger.error(f"  Invalid row number: {e}")

    def var_last_row_event(self, sv: customtkinter.StringVar):
        new_last_row = sv.get().strip()
        try:
            # last row is optional, so it may be an empty string
            proj.profile.pnp_last_row = -1 if new_last_row == "" else int(new_last_row) - 1
            logger.info(f"  PnP last row: {proj.profile.pnp_last_row+1}")
            if not proj.loading:
                self.button_load_event()
        except Exception as e:
            logger.error(f"  Invalid row number: {e}")

    def button_columns_event(self):
        logger.debug("Select PnP columns...")
        if proj.pnp_grid and len(proj.pnp_grid.rows_raw()) >= proj.profile.pnp_first_row:
            columns = proj.pnp_grid.rows_raw()[proj.profile.pnp_first_row]
        else:
            columns = ["..."]

        if self.column_selector:
            self.column_selector.destroy()
        self.column_selector = ColumnsSelector(self, app=self.app,
                                    columns=columns, callback=self.column_selector_callback,
                                    has_column_headers=proj.profile.pnp_has_column_headers,
                                    designator_default=proj.profile.pnp_designator_col,
                                    comment_default=proj.profile.pnp_comment_col,
                                    coord_x_default=proj.profile.pnp_coord_x_col,
                                    coord_y_default=proj.profile.pnp_coord_y_col,
                                    layer_default=proj.profile.pnp_layer_col,
                                    coord_mils_default=proj.profile.pnp_coord_unit_mils,
                                )
        # self.wnd_column_selector.focusmodel(model="active")

    def column_selector_callback(self, result: ColumnsSelectorResult):
        logger.info("Selected PnP columns: "\
                    f"dsgn='{result.designator_col}', cmnt='{result.comment_col}', "\
                    f"x='{result.coord_x_col}', y='{result.coord_y_col}', lr='{result.layer_col}'")
        proj.profile.pnp_has_column_headers = result.has_column_headers
        proj.profile.pnp_designator_col = result.designator_col
        proj.profile.pnp_comment_col = result.comment_col
        proj.profile.pnp_coord_x_col = result.coord_x_col
        proj.profile.pnp_coord_y_col = result.coord_y_col
        proj.profile.pnp_coord_unit_mils = result.coord_unit_mils
        proj.profile.pnp_layer_col = result.layer_col
        self.update_lbl_columns()
        self.btn_save.configure(state=tkinter.NORMAL)

    def button_save_event(self):
        if (n := proj.cfg_count_profile(proj.profile.name)) > 1:
            MessageBox(app=self.app, dialog_type="yn",
                        message=f"Profile '{proj.profile.name}' is used in {n} projects.\nDo you want to overwrite it?",
                        callback=self.onmsgbox_on_click)
            return

        self.btn_save.configure(state=tkinter.DISABLED)
        proj.profile.save()

    def onmsgbox_on_click(self, btn: str):
        if btn == "y":
            self.btn_save.configure(state=tkinter.DISABLED)
            proj.profile.save()
        else:
            logger.info("Profile NOT saved")

    def button_load_event(self):
        logger.debug("Load PnP...")
        self.btn_columns.configure(state=tkinter.NORMAL)
        pnp_path = os.path.join(os.path.dirname(proj.bom_path), proj.pnp_fname)
        pnp2_path = "" if proj.pnp2_fname == "" else os.path.join(os.path.dirname(proj.bom_path), proj.pnp2_fname)
        try:
            self.pnp_view.load_pnp(pnp_path, pnp2_path)
        except Exception as e:
            logger.error(f"Cannot load PnP: {e}")

# -----------------------------------------------------------------------------

class ReportView(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        assert "app" in kwargs
        self.app = kwargs.pop("app")

        assert "bom_view" in kwargs
        self.bom_view: BOMView = kwargs.pop("bom_view")
        assert isinstance(self.bom_view, BOMView)

        assert "pnp_view" in kwargs
        self.pnp_view: PnPView = kwargs.pop("pnp_view")
        assert isinstance(self.pnp_view, PnPView)

        # kwargs cleared from unexpected arguments -> call init
        super().__init__(master, **kwargs)

        self.report_html = """
            <h1>The PRE element</h1>
            <p>List <em>of</em> <b>items</b>:</p>
            <pre>
            C1   : <span style="color: Gray">BOM=</span>2u2/25/0603                           , <span style="color: Gray">PnP=</span>2u2_25V
            C2   : <span style="color: Gray">BOM=</span><span style="color: IndianRed"></span>22pF<span style="color: IndianRed">/50/0603/COG                      </span>, <span style="color: Gray">PnP=</span>22pF
            C7   : <span style="color: Gray">BOM=</span>2u2/25/0603                           , <span style="color: Gray">PnP=</span>2u2_25V
            C3   : <span style="color: Gray">BOM=</span><span style="color: IndianRed"></span>22pF<span style="color: ForestGreen">/50/0603/COG                      </span>, <span style="color: Gray">PnP=</span>22pF
            R65  : <span style="color: Gray">BOM=</span>0603; 220Ω; 100mW; ±1%; 100ppm        , <span style="color: Gray">PnP=</span>220R
            </pre>
            <p> The summary <b>is</b>: None</p>
        """
        self.htmlview = ui_helpers.HTMLScrolledTextWithPPM(self, wrap='none', html=self.report_html, menuitems="c")
        self.htmlview.grid(row=0, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.btn_crosscheck = customtkinter.CTkButton(self, text="Cross-check the files", command=self.button_crosscheck_event)
        self.btn_crosscheck.grid(row=1, column=0, pady=5, padx=5, sticky="we")

        self.btn_search = customtkinter.CTkButton(self, text="Copy HTML", command=self.button_copyhtml_event)
        self.btn_search.grid(row=1, column=1, pady=5, padx=5, sticky="")

        self.entry_search = customtkinter.CTkEntry(self, placeholder_text="search...")
        self.entry_search.grid(row=1, column=2, padx=5, pady=5, sticky="wens")

        self.btn_search = customtkinter.CTkButton(self, text="Find", command=self.button_find_event)
        self.btn_search.grid(row=1, column=3, pady=5, padx=5, sticky="we")

        self.lbl_occurences = customtkinter.CTkLabel(self, text="Found: 0")
        self.lbl_occurences.grid(row=1, column=4, pady=5, padx=5, sticky="")

    def clear_preview(self):
        self.report_html = ""
        self.htmlview.delete("0.0", tkinter.END)

    def button_crosscheck_event(self):
        logger.info("Performing cross-check...")
        self.clear_preview()

        if proj.bom_grid and proj.bom_grid_dirty:
            # reload file if manual load was successful
            try:
                logger.info("Reload BOM...")
                self.bom_view.load_bom(proj.bom_path)
            except Exception as e:
                logger.error(f"Cannot load BOM: {e}")
                return

        if proj.pnp_grid and proj.pnp_grid_dirty:
            # reload file if manual load was successful
            try:
                logger.info("Reload PnP...")
                pnp_path = os.path.join(os.path.dirname(proj.bom_path), proj.pnp_fname)
                pnp2_path = "" if proj.pnp2_fname == "" else os.path.join(os.path.dirname(proj.bom_path), proj.pnp2_fname)
                self.pnp_view.load_pnp(pnp_path, pnp2_path)
            except Exception as e:
                logger.error(f"Cannot load PnP: {e}")
                return

        bom_cols_ok = proj.profile.check_bom_columns()
        if not bom_cols_ok[0]:
            MessageBox(app=self.app, dialog_type="o",
                        message=bom_cols_ok[1],
                        callback=lambda btn: btn)
            return

        pnp_cols_ok = proj.profile.check_pnp_columns()
        if not pnp_cols_ok[0]:
            MessageBox(app=self.app, dialog_type="o",
                        message=pnp_cols_ok[1],
                        callback=lambda btn: btn)
            return

        bom_cfg = text_grid.ConfiguredTextGrid()
        bom_cfg.text_grid = proj.bom_grid
        bom_cfg.has_column_headers = proj.profile.bom_has_column_headers
        bom_cfg.designator_col = proj.profile.bom_designator_col
        bom_cfg.comment_col = proj.profile.bom_comment_col
        bom_cfg.first_row = proj.profile.bom_first_row
        bom_cfg.last_row = proj.profile.bom_last_row

        pnp_cfg = text_grid.ConfiguredTextGrid()
        pnp_cfg.text_grid = proj.pnp_grid
        pnp_cfg.has_column_headers = proj.profile.pnp_has_column_headers
        pnp_cfg.designator_col = proj.profile.pnp_designator_col
        pnp_cfg.comment_col = proj.profile.pnp_comment_col
        pnp_cfg.first_row = proj.profile.pnp_first_row
        pnp_cfg.last_row = proj.profile.pnp_last_row
        pnp_cfg.coord_x_col = proj.profile.pnp_coord_x_col
        pnp_cfg.coord_y_col = proj.profile.pnp_coord_y_col
        pnp_cfg.layer_col = proj.profile.pnp_layer_col

        try:
            ccresult = cross_check.compare(bom_cfg, pnp_cfg, proj.get_min_distance(), proj.profile.pnp_coord_unit_mils)
            pnps = (proj.pnp_fname, proj.pnp2_fname)
            self.report_html = report_generator.prepare_html_report(proj.get_name(), pnps, proj.get_min_distance(), ccresult)
            self.htmlview.set_html(self.report_html)
            self.save_report_to_file()
        except Exception as e:
            logger.error(f"Report generator error: {e}")
        finally:
            # mark as potentially dirty, meaning that the files could have been changed manually
            # since the last cross-check was performed so the local copy is out-of-date
            proj.bom_grid_dirty = True
            proj.pnp_grid_dirty = True

    def save_report_to_file(self):
        report_dir = os.path.dirname(proj.bom_path)
        report_fname = os.path.splitext(os.path.basename(proj.bom_path))[0]
        report_fname += "_report.html"
        report_path = os.path.join(report_dir, report_fname)
        logger.debug("Saving to .html file...")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('<html>\n<body>\n')
            f.write(self.report_html)
            f.write('</body>\n</html>\n')
            logger.info(f"Report saved to: {report_path}")

    def button_copyhtml_event(self):
        logger.debug("Copy as HTML")
        plain_txt = self.htmlview.get("0.0", tkinter.END)
        klembord.set_with_rich_text(text=plain_txt, html=self.report_html)

    def button_find_event(self):
        txt = self.entry_search.get()
        logger.info(f"Find '{txt}'")
        cnt = ui_helpers.textbox_find_text(self.htmlview, txt)
        self.lbl_occurences.configure(text=f"Found: {cnt}")

# -----------------------------------------------------------------------------

class CtkApp(customtkinter.CTk):
    def __init__(self):
        logger.info('Ctk app is starting')
        super().__init__()

        self.title(f"{APP_NAME}")
        self.geometry("1200x600")
        self.grid_columnconfigure(0, weight=1)

        # panel with Proj/BOM/PnP/Result
        tabview = customtkinter.CTkTabview(self)
        tabview.grid(row=1, column=0, padx=5, pady=5, sticky="wens")
        self.grid_rowconfigure(1, weight=1) # set row 1 height to all remaining space
        tab_prj = tabview.add("Project")
        tab_bom = tabview.add("Bill Of Materials")
        tab_pnp = tabview.add("Pick And Place")
        tab_report = tabview.add("Cross-check Report")
        tabview.set("Project")  # set currently visible tab

        # panel with predefined configs
        proj_frame = ProjectFrame(tab_prj, app=self)
        proj_frame.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        tab_prj.grid_columnconfigure(0, weight=1)
        tab_prj.grid_rowconfigure(0, weight=1)

        # panel with the BOM
        self.bom_view = BOMView(tab_bom, app=self)
        self.bom_view.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        self.bom_config = BOMConfig(tab_bom, app=self, bom_view=self.bom_view)
        self.bom_config.grid(row=1, column=0, pady=5, padx=5, sticky="we")
        proj_frame.bom_config = self.bom_config
        proj_frame.bom_view = self.bom_view

        tab_bom.grid_columnconfigure(0, weight=1)
        tab_bom.grid_rowconfigure(0, weight=1)

        # panel with the PnP
        self.pnp_view = PnPView(tab_pnp, app=self)
        self.pnp_view.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        self.pnp_config = PnPConfig(tab_pnp, app=self, pnp_view=self.pnp_view)
        self.pnp_config.grid(row=1, column=0, padx=5, pady=5, sticky="we")
        proj_frame.pnp_config = self.pnp_config
        proj_frame.pnp_view = self.pnp_view

        tab_pnp.grid_columnconfigure(0, weight=1)
        tab_pnp.grid_rowconfigure(0, weight=1)

        # panel with the report
        self.report_view = ReportView(tab_report, app=self, bom_view=self.bom_view, pnp_view=self.pnp_view)
        self.report_view.grid(row=0, column=0, padx=5, pady=5, sticky="wens")
        proj_frame.report_view = self.report_view

        tab_report.grid_columnconfigure(0, weight=1)
        tab_report.grid_rowconfigure(0, weight=1)

        # UI ready
        logger.info('Application ready.')

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    logger.config(proj.color_logs)
    logger.info(f"{APP_NAME}   {APP_DATE}")

    if (sys.version_info.major < 3) or (sys.version_info.major == 3 and sys.version_info.minor < 9):
        logger.error("Required Python version 3.9 or later!")
        sys.exit()
    else:
        logger.info(
            f"Python version: {sys.version_info.major}.{sys.version_info.minor}"
        )

    # https://customtkinter.tomschimansky.com/documentation/appearancemode
    customtkinter.set_appearance_mode("light")
    customtkinter.set_default_color_theme("green")

    klembord.init()
    ctkapp = CtkApp()
    ctkapp.mainloop()

    logger.info('Program ended.')
