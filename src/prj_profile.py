import configparser
import logging
import os

# -----------------------------------------------------------------------------

class Profile:
    CONFIG_FILE_NAME: str = "boomer.ini"

    name: str
    bom_has_column_headers: bool
    bom_first_row: int # 0-based
    bom_last_row: int # 0-based
    bom_separator: str
    bom_designator_col: str
    bom_comment_col: str
    pnp_has_column_headers: bool
    pnp_first_row: int # 0-based
    pnp_last_row: int # 0-based
    pnp_separator: str
    pnp_designator_col: str
    pnp_comment_col: str
    __config: configparser.ConfigParser

    def __init__(self, cfgparser: configparser.ConfigParser):
        self.name = "initial-profile"

        self.bom_has_column_headers = True
        self.bom_first_row = 0
        self.bom_last_row = -1 # not saved in config file
        self.bom_separator = "COMMA"
        self.bom_designator_col = "?"
        self.bom_comment_col = "?"

        self.pnp_has_column_headers = True
        self.pnp_first_row = 0
        self.pnp_last_row = -1 # not saved in config file
        self.pnp_separator = "COMMA"
        self.pnp_designator_col = "?"
        self.pnp_comment_col = "?"

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

                self.pnp_has_column_headers = section.get("pnp_has_column_headers", "True") == "True"
                self.pnp_first_row = int(section.get("pnp_first_row", "0"))
                self.pnp_last_row = -1
                self.pnp_separator = section.get("pnp_separator", "COMMA")
                self.pnp_designator_col = section.get("pnp_designator_col", "?")
                self.pnp_comment_col = section.get("pnp_comment_col", "?")
                if self.pnp_has_column_headers == False:
                    self.pnp_designator_col = int(self.pnp_designator_col)
                    self.pnp_comment_col = int(self.pnp_comment_col)

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
            "pnp_has_column_headers": self.pnp_has_column_headers,
            "pnp_first_row": self.pnp_first_row,
            "pnp_separator": self.pnp_separator,
            "pnp_designator_col": self.pnp_designator_col,
            "pnp_comment_col": self.pnp_comment_col,
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

    def get_bom_delimiter(self) -> str:
        return self.translate_separator(self.bom_separator)

    def get_pnp_delimiter(self) -> str:
        return self.translate_separator(self.pnp_separator)
