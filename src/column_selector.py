import customtkinter
import tkinter
import logging
import typing

# -----------------------------------------------------------------------------

class ColumnsSelectorResult:
    def __init__(self):
        self.designator_col = ""
        self.comment_col = ""
        self.coord_x_col = ""
        self.coord_y_col = ""
        self.has_column_headers = True

# -----------------------------------------------------------------------------

class ColumnsSelectorWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        assert "columns" in kwargs
        columns = kwargs.pop("columns")

        assert type(columns) is list
        # logging.debug("columns: {}".format(self.columns))
        assert "callback" in kwargs
        self.callback: typing.Callable = kwargs.pop("callback")

        assert "has_column_headers" in kwargs
        has_column_headers = kwargs.pop("has_column_headers")
        assert type(has_column_headers) is bool

        # ----------

        assert "designator_default" in kwargs
        designator_default = kwargs.pop("designator_default")
        designator_default = self.__format_column(has_column_headers, columns, designator_default)

        # ----------

        assert "comment_default" in kwargs
        comment_default = kwargs.pop("comment_default")
        comment_default = self.__format_column(has_column_headers, columns, comment_default)

        # ----------

        # optional, only for PnP
        if "coord_x_default" in kwargs and "coord_y_default" in kwargs:
            coord_x_default = kwargs.pop("coord_x_default")
            coord_x_default = self.__format_column(has_column_headers, columns, coord_x_default)
            coord_y_default = kwargs.pop("coord_y_default")
            coord_y_default = self.__format_column(has_column_headers, columns, coord_y_default)
            self.show_coords = True
        else:
            coord_x_default = ""
            coord_y_default = ""
            self.show_coords = False

        # ----------

        super().__init__(*args, **kwargs)
        self.geometry("400x250")

        # prepend column titles with their corresponding index
        columns = [f"{idx}. {item}" for (idx,item) in enumerate(columns)]
        #
        lbl_col_headers = customtkinter.CTkLabel(self, text="File has column headers")
        lbl_col_headers.grid(row=0, column=0, pady=5, padx=5, sticky="w")

        self.chbx_columnheaders_var = customtkinter.BooleanVar(value=has_column_headers)
        chbx_column_headers = customtkinter.CTkCheckBox(self, text="",
                                                        command=self.chbx_event, variable=self.chbx_columnheaders_var,
                                                        checkbox_width=18, checkbox_height=18)
        chbx_column_headers.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        #
        lbl_designator = customtkinter.CTkLabel(self, text="Designator column:")
        lbl_designator.grid(row=1, column=0, pady=5, padx=5, sticky="w")

        self.opt_designator_var = customtkinter.StringVar(value=designator_default)
        opt_designator = customtkinter.CTkOptionMenu(self, values=columns,
                                                     command=self.opt_event,
                                                     variable=self.opt_designator_var)
        opt_designator.grid(row=1, column=1, pady=5, padx=5, sticky="we")
        self.grid_columnconfigure(1, weight=1)

        #
        lbl_comment = customtkinter.CTkLabel(self, text="Comment (value) column:")
        lbl_comment.grid(row=2, column=0, pady=5, padx=5, sticky="w")

        self.opt_comment_var = customtkinter.StringVar(value=comment_default)
        opt_comment = customtkinter.CTkOptionMenu(self, values=columns,
                                                command=self.opt_event,
                                                variable=self.opt_comment_var)
        opt_comment.grid(row=2, column=1, pady=5, padx=5, sticky="we")

        #
        lbl_coord_x = customtkinter.CTkLabel(self, text="X-center")
        lbl_coord_x.grid(row=3, column=0, pady=5, padx=5, sticky="w")

        self.opt_coord_x_var = customtkinter.StringVar(value=coord_x_default)
        if self.show_coords:
            opt_coord_x = customtkinter.CTkOptionMenu(self, values=columns,
                                                    command=self.opt_event,
                                                    variable=self.opt_coord_x_var)
            opt_coord_x.grid(row=3, column=1, pady=5, padx=5, sticky="we")

        #
        lbl_coord_y = customtkinter.CTkLabel(self, text="Y-center")
        lbl_coord_y.grid(row=4, column=0, pady=5, padx=5, sticky="w")

        self.opt_coord_y_var = customtkinter.StringVar(value=coord_y_default)
        if self.show_coords:
            opt_coord_y = customtkinter.CTkOptionMenu(self, values=columns,
                                                    command=self.opt_event,
                                                    variable=self.opt_coord_y_var)
            opt_coord_y.grid(row=4, column=1, pady=5, padx=5, sticky="we")

        #
        sep_h = tkinter.ttk.Separator(self, orient='horizontal')
        sep_h.grid(row=5, column=0, columnspan=2, pady=5, padx=5, sticky="we",)

        self.btn_cancel = customtkinter.CTkButton(self, text="Cancel",
                                                   command=self.button_cancel_event)
        #
        self.btn_cancel.grid(row=6, column=0, pady=5, padx=5, sticky="")

        self.btn_ok = customtkinter.CTkButton(self, text="OK",
                                                command=self.button_ok_event)
        self.btn_ok.grid(row=6, column=1, pady=5, padx=5, sticky="we")
        self.btn_ok.configure(state="disabled")

        # enable "always-on-top" for this popup window
        self.attributes('-topmost', True)

    def __format_column(self, has_headers: bool, columns: list[str], col_default: str) -> str:
        if has_headers:
            # prepend column title with its index
            try:
                default_idx = columns.index(col_default)
            except ValueError as e:
                default_idx = 0
            col_default = f"{default_idx}. {col_default}"
        else:
            # designator is a column index
            col_default = f"{col_default}. {columns[col_default]}"

        return col_default

    def chbx_event(self):
        self.btn_ok.configure(state="enabled")

    def opt_event(self, _new_choice: str):
        if self.opt_designator_var.get() != "" and self.opt_comment_var.get() != "":
            self.btn_ok.configure(state="enabled")

    def button_cancel_event(self):
        logging.info("Column selector: cancelled")
        self.destroy()

    def button_ok_event(self):
        result = ColumnsSelectorResult()
        result.has_column_headers = self.chbx_columnheaders_var.get()
        result.designator_col = self.opt_designator_var.get()
        result.comment_col = self.opt_comment_var.get()
        result.coord_x_col = self.opt_coord_x_var.get()
        result.coord_y_col = self.opt_coord_y_var.get()
        if result.has_column_headers:
            # extract column name
            result.designator_col = result.designator_col.split(sep=". ")[1]
            result.comment_col = result.comment_col.split(sep=". ")[1]
            if self.show_coords:
                result.coord_x_col = result.coord_x_col.split(sep=". ")[1]
                result.coord_y_col = result.coord_y_col.split(sep=". ")[1]
        else:
            # extract column index
            result.designator_col = int(result.designator_col.split(sep=". ")[0])
            result.comment_col = int(result.comment_col.split(sep=". ")[0])
            if not self.show_coords:
                result.coord_x_col = int(result.coord_x_col.split(sep=". ")[0])
                result.coord_y_col = int(result.coord_y_col.split(sep=". ")[0])
        self.callback(result)
        self.destroy()
