import configparser
import logging
import os

import text_grid

# -----------------------------------------------------------------------------

class Profile:
    CONFIG_FILE_NAME: str = "boomer.ini"

    def __init__(self, cfgparser: configparser.ConfigParser):
        self.name = "initial-profile"

        self.bom_has_column_headers = True
        self.bom_first_row = 0 # 0-based
        self.bom_last_row = -1 # 0-based, not saved in config file
        self.bom_separator = "COMMA"
        self.bom_designator_col = "?"
        self.bom_comment_col = "?"
        #
        self.pnp_has_column_headers = True
        self.pnp_first_row = 0 # 0-based
        self.pnp_last_row = -1 # 0-based, not saved in config file
        self.pnp_separator = "COMMA"
        self.pnp_designator_col = "?"
        self.pnp_comment_col = "?"
        self.pnp_coord_x_col = "?"
        self.pnp_coord_y_col = "?"
        #
        self.__config = cfgparser

    def load(self, name: str):
        if os.path.isfile(self.CONFIG_FILE_NAME):
            logging.info(f"Load profile: {name}")
            self.name = name

            if self.__config.has_section(f'profile.{self.name}'):
                section = self.__config[f'profile.{self.name}']

                self.bom_has_column_headers = section.get("bom_has_column_headers", "True") == "True"
                self.bom_first_row = int(section.get("bom_first_row", "0"))
                self.bom_last_row = -1
                self.bom_separator = section.get("bom_separator", "COMMA")
                self.bom_designator_col = section.get("bom_designator_col", "?")
                self.bom_comment_col = section.get("bom_comment_col", "?")
                if self.bom_has_column_headers == False:
                    self.bom_designator_col = int(self.bom_designator_col)
                    self.bom_comment_col = int(self.bom_comment_col)
                #
                self.pnp_has_column_headers = section.get("pnp_has_column_headers", "True") == "True"
                self.pnp_first_row = int(section.get("pnp_first_row", "0"))
                self.pnp_last_row = -1
                self.pnp_separator = section.get("pnp_separator", "COMMA")
                self.pnp_designator_col = section.get("pnp_designator_col", "?")
                self.pnp_comment_col = section.get("pnp_comment_col", "?")
                self.pnp_coord_x_col = section.get("pnp_coord_x_col", "?")
                self.pnp_coord_y_col = section.get("pnp_coord_y_col", "?")
                if not self.pnp_has_column_headers:
                    self.pnp_designator_col = int(self.pnp_designator_col)
                    self.pnp_comment_col = int(self.pnp_comment_col)
                    self.pnp_coord_x_col = int(self.pnp_coord_x_col)
                    self.pnp_coord_y_col = int(self.pnp_coord_y_col)
            else:
                logging.warning(f"No section {self.name} in config file")
        else:
            logging.error(f"Config file {self.CONFIG_FILE_NAME} not found")

    def save(self):
        logging.info(f"Save profile: {self.name}")
        self.__config[f"profile.{self.name}"] = {
            "bom_has_column_headers": self.bom_has_column_headers,
            "bom_first_row": self.bom_first_row,
            "bom_separator": self.bom_separator,
            "bom_designator_col": self.bom_designator_col,
            "bom_comment_col": self.bom_comment_col,
            #
            "pnp_has_column_headers": self.pnp_has_column_headers,
            "pnp_first_row": self.pnp_first_row,
            "pnp_separator": self.pnp_separator,
            "pnp_designator_col": self.pnp_designator_col,
            "pnp_comment_col": self.pnp_comment_col,
            "pnp_coord_x_col": self.pnp_coord_x_col,
            "pnp_coord_y_col": self.pnp_coord_y_col,
        }
        with open(self.CONFIG_FILE_NAME, 'w') as f:
            self.__config.write(f)

    @staticmethod
    def get_separator_names() -> list[str]:
        return ["COMMA", "SEMICOLON", "TAB", "SPACES", "FIXED-WIDTH", "REGEX"].copy()

    @staticmethod
    def translate_separator(sep: str) -> str:
        """
        # Python 3.10+
        match sep:
            case "COMMA":
                return ","
            case "SEMICOLON":
                return ";"
            case "TAB":
                return "\t"
            case "SPACES":
                return "*sp"
            case "FIXED-WIDTH":
                return "*fw"
            case "REGEX":
                return "*re"
            case _:
                raise RuntimeError("Unknown CSV separator")
        """

        if sep == "COMMA":
            return ","
        elif sep == "SEMICOLON":
            return ";"
        elif sep == "TAB":
            return "\t"
        elif sep == "SPACES":
            return "*sp"
        elif sep == "FIXED-WIDTH":
            return "*fw"
        elif sep == "REGEX":
            return "*re"
        else:
            raise RuntimeError("Unknown CSV separator")

    @property
    def bom_delimiter(self) -> str:
        return self.translate_separator(self.bom_separator)

    @property
    def pnp_delimiter(self) -> str:
        return self.translate_separator(self.pnp_separator)

# -----------------------------------------------------------------------------

class Project:
    """Represents configuration and data of currently selected BOM+PnP files"""
    def __init__(self):
        self.bom_path = "<bom_path>"
        self.pnp_fname = "<pnp_fname>"
        self.pnp2_fname = ""
        self.bom_grid: text_grid.TextGrid = None
        self.bom_grid_dirty = False
        self.pnp_grid: text_grid.TextGrid = None
        self.pnp_grid_dirty = False
        self.loading = False

        # https://docs.python.org/3/library/configparser.html
        self.__config = configparser.ConfigParser()

        if os.path.isfile(Profile.CONFIG_FILE_NAME):
            self.__config.read(Profile.CONFIG_FILE_NAME)
        else:
            self.__config['common'] = {
                "initial_dir": "",
            }

        self.profile = Profile(cfgparser=self.__config)

    def get_name(self) -> str:
        return os.path.basename(self.bom_path)

    def cfg_get_section(self, sect_name: str) -> configparser.SectionProxy:
        try:
            self.__config[sect_name]
        except Exception:
            self.__config[sect_name] = {}

        return self.__config[sect_name]

    def get_projects(self) -> list[str]:
        projects = [
            sect.removeprefix("project.")
            for sect in self.__config.sections()
            if sect.startswith("project.")
        ]
        for prj_path in reversed(projects):
            if not os.path.exists(prj_path):
                logging.info(f"Project '{prj_path}' not found - removed")
                projects.remove(prj_path)
                self.del_project(prj_path)

        projects.sort()
        return projects

    def del_project(self, proj_path: str):
        sect_name = f"project.{proj_path}"
        if sect_name in self.__config.sections():
            self.__config.remove_section(sect_name)
            with open(Profile.CONFIG_FILE_NAME, 'w') as f:
                self.__config.write(f)
        else:
            logging.warning(f"Project '{proj_path}' not found")

    def del_profile(self, name):
        sect_name = f"profile.{name}"
        if sect_name in self.__config.sections():
            self.__config.remove_section(sect_name)
            with open(Profile.CONFIG_FILE_NAME, 'w') as f:
                self.__config.write(f)
            # reset profile
            self.profile = Profile(cfgparser=self.__config)
        else:
            logging.warning(f"Profile '{name}' not found")

    def cfg_count_profile(self, profile_name: str) -> int:
        cnt = 0
        projs = self.get_projects()
        for prj in projs:
            section = self.cfg_get_section(f"project.{prj}")
            if section["profile"] == profile_name:
                cnt += 1
        return cnt

    def cfg_get_profiles(self) -> list[str]:
        profiles = [
            sect.removeprefix("profile.")
            for sect in self.__config.sections()
            if sect.startswith("profile.")
        ]
        if not profiles:
            profiles.append("default-profile")

        profiles.sort()
        return profiles

    def cfg_save_project(self):
        section = self.cfg_get_section(f"project.{self.bom_path}")
        section["pnp"] = self.pnp_fname
        section["pnp2"] = self.pnp2_fname
        section["profile"] = self.profile.name
        with open(Profile.CONFIG_FILE_NAME, 'w') as f:
            self.__config.write(f)
