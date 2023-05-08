import customtkinter
import logging
import typing

# -----------------------------------------------------------------------------

class ColumnsSelectorResult:
    designator_col: str
    comment_col: str

    def __init__(self):
        self.designator_col = ""
        self.comment_col = ""

# -----------------------------------------------------------------------------

class ColumnsSelectorWindow(customtkinter.CTkToplevel):
    callback: typing.Callable
    comment_active: bool

    def __init__(self, *args, **kwargs):
        assert "columns" in kwargs
        self.columns = kwargs.pop("columns")
        assert type(self.columns) is list
        # logging.debug("columns: {}".format(self.columns))
        assert "callback" in kwargs
        self.callback = kwargs.pop("callback")
        assert "comment_active" in kwargs
        self.comment_active = kwargs.pop("comment_active")

        super().__init__(*args, **kwargs)
        self.geometry("400x160")

        lbl_designator = customtkinter.CTkLabel(self, text="Part designator column:")
        lbl_designator.grid(row=0, column=0, pady=5, padx=5, sticky="w")

        self.opt_designator_var = customtkinter.StringVar(value="")
        opt_designator = customtkinter.CTkOptionMenu(self, values=self.columns,
                                                     command=self.opt_event,
                                                     variable=self.opt_designator_var)
        opt_designator.grid(row=0, column=1, pady=5, padx=5, sticky="we")
        self.grid_columnconfigure(1, weight=1)

        if self.comment_active:
            lbl_comment = customtkinter.CTkLabel(self, text="Part comment/value column:")
            lbl_comment.grid(row=1, column=0, pady=5, padx=5, sticky="w")

            self.opt_comment_var = customtkinter.StringVar(value="")
            opt_comment = customtkinter.CTkOptionMenu(self, values=self.columns,
                                                    command=self.opt_event,
                                                    variable=self.opt_comment_var)
            opt_comment.grid(row=1, column=1, pady=5, padx=5, sticky="we")
            opt_comment.configure(state="normal" if self.comment_active else "disabled")

        lbl_hline = customtkinter.CTkLabel(self, text="—" * 50)
        lbl_hline.grid(row=2, column=0, columnspan=2, pady=5, padx=5, sticky="we",)

        self.btn_cancel = customtkinter.CTkButton(self, text="Cancel",
                                                   command=self.button_cancel_event)
        self.btn_cancel.grid(row=3, column=0, pady=5, padx=5, sticky="")

        self.btn_ok = customtkinter.CTkButton(self, text="OK",
                                                   command=self.button_ok_event)
        self.btn_ok.grid(row=3, column=1, pady=5, padx=5, sticky="we")
        self.btn_ok.configure(state="disabled")

        # enable "always-on-top" for this popup window
        self.attributes('-topmost', True)

    def opt_event(self, new_profile: str):
        if self.opt_designator_var.get() != "" and (not self.comment_active or self.opt_comment_var.get() != ""):
            self.btn_ok.configure(state="enabled")

    def button_cancel_event(self):
        logging.info("Column selector: cancelled")
        self.destroy()

    def button_ok_event(self):
        result = ColumnsSelectorResult()
        result.designator_col = self.opt_designator_var.get()
        result.comment_col = self.opt_comment_var.get()
        self.callback(result)
        self.destroy()
