import customtkinter as ctk
from datetime import date
from typing import Callable

from core.models import Bill, Category


class BillForm(ctk.CTkFrame):
    """Reusable bill entry/edit form."""

    def __init__(self, master, app, bill: Bill = None, on_save: Callable = None, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.db = app.db
        self.bill = bill  # if editing, the bill to edit
        self.on_save = on_save

        self._build_form()
        if bill:
            self._populate(bill)

    def _build_form(self):
        # title
        ctk.CTkLabel(self, text="金额", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=(20, 10), pady=(15, 5))
        self.amount_entry = ctk.CTkEntry(self, placeholder_text="输入金额", height=40,
                                         font=ctk.CTkFont(size=20),
                                         width=280)
        self.amount_entry.grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 10), sticky="ew")

        # type switch
        ctk.CTkLabel(self, text="类型", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=2, column=0, sticky="w", padx=(20, 10), pady=(5, 5))
        self.type_var = ctk.StringVar(value="expense")
        self.type_seg = ctk.CTkSegmentedButton(
            self, values=["支出", "收入"],
            variable=self.type_var,
            command=self._on_type_change,
        )
        # map display values to internal values
        self._type_map = {"支出": "expense", "收入": "income"}
        self.type_seg.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="w")

        # category
        ctk.CTkLabel(self, text="分类", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=4, column=0, sticky="w", padx=(20, 10), pady=(5, 5))
        self.category_var = ctk.StringVar()
        self.category_menu = ctk.CTkOptionMenu(self, variable=self.category_var,
                                               values=[], width=200)
        self.category_menu.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="w")

        # date
        ctk.CTkLabel(self, text="日期", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=4, column=1, sticky="w", padx=(20, 10), pady=(5, 5))
        self.date_var = ctk.StringVar(value=date.today().isoformat())
        self.date_entry = ctk.CTkEntry(self, textvariable=self.date_var, width=140,
                                       placeholder_text="YYYY-MM-DD")
        self.date_entry.grid(row=5, column=1, padx=20, pady=(0, 10), sticky="w")

        # description
        ctk.CTkLabel(self, text="备注", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=6, column=0, sticky="w", padx=(20, 10), pady=(5, 5))
        self.desc_entry = ctk.CTkEntry(self, placeholder_text="添加备注 (可选)",
                                       height=36, width=400)
        self.desc_entry.grid(row=7, column=0, columnspan=3, padx=20, pady=(0, 10), sticky="ew")

        # submit button
        btn_text = "修改账单" if self.bill else "记一笔"
        self.submit_btn = ctk.CTkButton(self, text=btn_text,
                                        font=ctk.CTkFont(size=15, weight="bold"),
                                        height=44,
                                        command=self._submit)
        self.submit_btn.grid(row=8, column=0, columnspan=3, padx=20, pady=(10, 20), sticky="ew")

        # initialize categories
        self._load_categories()

    def _load_categories(self):
        bill_type = self._type_map.get(self.type_var.get(), "expense")
        cats = self.db.get_categories(bill_type)
        names = [c.name for c in cats]
        self.category_menu.configure(values=names)
        if names:
            self.category_var.set(names[0])

    def _on_type_change(self, value):
        self._load_categories()

    def _submit(self):
        amount_str = self.amount_entry.get().strip()
        if not amount_str:
            return
        try:
            amount = float(amount_str)
        except ValueError:
            return
        if amount <= 0:
            return

        bill_type = self._type_map.get(self.type_var.get(), "expense")
        category_name = self.category_var.get()
        description = self.desc_entry.get().strip()
        bill_date_str = self.date_var.get().strip()

        try:
            bill_date = date.fromisoformat(bill_date_str)
        except (ValueError, TypeError):
            bill_date = date.today()

        # resolve category id
        cats = self.db.get_categories(bill_type)
        cat_id = None
        for c in cats:
            if c.name == category_name:
                cat_id = c.id
                break
        if cat_id is None and cats:
            cat_id = cats[0].id

        bill = Bill(
            id=self.bill.id if self.bill else None,
            amount=amount,
            type=bill_type,
            category_id=cat_id,
            description=description,
            bill_date=bill_date,
        )

        if self.bill and self.bill.id:
            self.db.update_bill(bill)
        else:
            self.db.add_bill(bill)

        if self.on_save:
            self.on_save()

    def _populate(self, bill: Bill):
        self.amount_entry.insert(0, str(bill.amount))
        display_type = "收入" if bill.type == "income" else "支出"
        self.type_var.set(display_type)
        self._load_categories()
        if bill.category_name:
            self.category_var.set(bill.category_name)
        self.desc_entry.insert(0, bill.description)
        self.date_var.set(bill.bill_date.isoformat() if bill.bill_date else "")

    def clear(self):
        self.amount_entry.delete(0, "end")
        self.type_var.set("支出")
        self._load_categories()
        self.desc_entry.delete(0, "end")
        self.date_var.set(date.today().isoformat())
