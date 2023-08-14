import customtkinter
import tkinter
import logging
import typing

# -----------------------------------------------------------------------------

class ColumnsSelectorResult:
    def __init__(self):
        self.designator_col = ""
        self.comment_col = ""
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

        assert "designator_default" in kwargs
        designator_default = kwargs.pop("designator_default")
        if has_column_headers:
            # prepend column title with its index
            try:
                designator_default_idx = columns.index(designator_default)
            except ValueError as e:
                designator_default_idx = 0
            designator_default = f"{designator_default_idx}. {designator_default}"
        else:
            # designator is a column index
            designator_default = f"{designator_default}. {columns[designator_default]}"

        assert "comment_default" in kwargs
        comment_default = kwargs.pop("comment_default")
        if has_column_headers:
            try:
                comment_default_idx = columns.index(comment_default)
            except ValueError as e:
                comment_default_idx = 0
            comment_default = f"{comment_default_idx}. {comment_default}"
        else:
            comment_default = f"{comment_default}. {columns[comment_default]}"

        super().__init__(*args, **kwargs)
        self.geometry("400x195")

        # prepend column titles with their corresponding index
        columns = [f"{idx}. {item}" for (idx,item) in enumerate(columns)]

        lbl_col_headers = customtkinter.CTkLabel(self, text="File has column headers")
        lbl_col_headers.grid(row=0, column=0, pady=5, padx=5, sticky="w")

        self.chbx_columnheaders_var = customtkinter.BooleanVar(value=has_column_headers)
        chbx_column_headers = customtkinter.CTkCheckBox(self, text="",
                                                        command=self.chbx_event, variable=self.chbx_columnheaders_var,
                                                        checkbox_width=18, checkbox_height=18)
        chbx_column_headers.grid(row=0, column=1, pady=5, padx=5, sticky="w")

        lbl_designator = customtkinter.CTkLabel(self, text="Part designator column:")
        lbl_designator.grid(row=1, column=0, pady=5, padx=5, sticky="w")

        self.opt_designator_var = customtkinter.StringVar(value=designator_default)
        opt_designator = customtkinter.CTkOptionMenu(self, values=columns,
                                                     command=self.opt_event,
                                                     variable=self.opt_designator_var)
        opt_designator.grid(row=1, column=1, pady=5, padx=5, sticky="we")
        self.grid_columnconfigure(1, weight=1)

        lbl_comment = customtkinter.CTkLabel(self, text="Part comment (value) column:")
        lbl_comment.grid(row=2, column=0, pady=5, padx=5, sticky="w")

        self.opt_comment_var = customtkinter.StringVar(value=comment_default)
        opt_comment = customtkinter.CTkOptionMenu(self, values=columns,
                                                command=self.opt_event,
                                                variable=self.opt_comment_var)
        opt_comment.grid(row=2, column=1, pady=5, padx=5, sticky="we")

        sep_h = tkinter.ttk.Separator(self, orient='horizontal')
        sep_h.grid(row=3, column=0, columnspan=2, pady=5, padx=5, sticky="we")

        self.btn_cancel = customtkinter.CTkButton(self, text="Cancel",
                                                   command=self.button_cancel_event)
        self.btn_cancel.grid(row=4, column=0, pady=5, padx=5, sticky="")

        self.btn_ok = customtkinter.CTkButton(self, text="OK",
                                                command=self.button_ok_event)
        self.btn_ok.grid(row=4, column=1, pady=5, padx=5, sticky="we")
        self.btn_ok.configure(state="disabled")

        # enable "always-on-top" for this popup window
        self.attributes('-topmost', True)

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
        if result.has_column_headers:
            # extract column name
            result.designator_col = result.designator_col.split(sep=". ")[1]
            result.comment_col = result.comment_col.split(sep=". ")[1]
        else:
            # extract column index
            result.designator_col = int(result.designator_col.split(sep=". ")[0])
            result.comment_col = int(result.comment_col.split(sep=". ")[0])
        self.callback(result)
        self.destroy()
