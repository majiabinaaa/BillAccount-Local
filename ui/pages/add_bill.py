import customtkinter as ctk
from datetime import date
from tkinter import messagebox

from ui.components.bill_form import BillForm


class AddBillPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = ctk.CTkFrame(self)
        container.grid(row=0, column=0, padx=40, pady=30, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(container, text="记一笔",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(25, 15))

        self.form = BillForm(container, app, on_save=self._on_saved)
        self.form.pack(fill="x", padx=30, pady=(0, 25))

    def _on_saved(self):
        messagebox.showinfo("成功", "账单已保存！")
        self.form.clear()

    def on_show(self):
        pass

    def refresh(self):
        pass
