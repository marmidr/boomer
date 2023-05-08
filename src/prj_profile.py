import configparser
import logging
import os

# -----------------------------------------------------------------------------

class Profile:
    CONFIG_FILE_NAME: str = "boomer.ini"

    name: str
    bom_first_row: int # 0-based
    bom_separator: str
    bom_designator_col: str
    bom_comment_col: str
    pnp_first_row: int # 0-based
    pnp_separator: str
    pnp_designator_col: str
    __config: configparser.ConfigParser

    def __init__(self, config: configparser.ConfigParser):
        self.name = "noname"
        self.bom_first_row = 0
        self.bom_separator = "COMMA"
        self.bom_designator_col = "?"
        self.bom_comment_col = "?"
        self.pnp_first_row = 0
        self.pnp_separator = "COMMA"
        self.pnp_designator_col = "?"
        self.__config = config

    def load(self, name: str):
        if os.path.isfile(self.CONFIG_FILE_NAME):
            logging.debug(f"Load profile {name}")
            self.name = name
            section = self.__config['profile.' + self.name]

            self.bom_first_row = int(section.get("bom_first_row", "0"))
            self.bom_separator = section.get("bom_separator", "COMMA")
            self.bom_designator_col = section.get("bom_designator_col", "?")
            self.bom_comment_col = section.get("bom_comment_col", "?")

            self.pnp_first_row = int(section.get("pnp_first_row", "0"))
            self.pnp_separator = section.get("pnp_separator", "COMMA")
            self.pnp_designator_col = section.get("pnp_designator_col", "?")
        else:
            logging.warning("Config file not found")

    def save(self):
        logging.debug(f"Save profile: {self.name}")
        self.__config["profile." + self.name] = {
            "bom_first_row": self.bom_first_row,
            "bom_separator": self.bom_separator,
            "bom_designator_col": self.bom_designator_col,
            "bom_comment_col": self.bom_comment_col,

            "pnp_first_row": self.pnp_first_row,
            "pnp_separator": self.pnp_separator,
            "pnp_designator_col": self.pnp_designator_col,
        }
        with open(self.CONFIG_FILE_NAME, 'w') as f:
            self.__config.write(f)

    @staticmethod
    def get_separator_names() -> list[str]:
        return ["COMMA", "SEMICOLON", "TAB", "SPACES", "FIXED-WIDTH", "REGEX"].copy()

    @staticmethod
    def translate_separator(sep: str) -> str:
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

    def get_bom_delimiter(self) -> str:
        return self.translate_separator(self.bom_separator)

    def get_pnp_delimiter(self) -> str:
        return self.translate_separator(self.pnp_separator)
