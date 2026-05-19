import customtkinter as ctk
from datetime import date
from tkinter import messagebox

from core.models import Bill


class BillListPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app
        self.db = app.db
        self._offset = 0
        self._page_size = 50
        self._edit_bill = None

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Header ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=25, pady=(25, 10))
        ctk.CTkLabel(header, text="账单列表",
                     font=ctk.CTkFont(size=26, weight="bold")).pack(side="left")

        # --- Filters ---
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=1, column=0, sticky="ew", padx=25, pady=(0, 10))
        filter_frame.grid_columnconfigure(7, weight=1)

        ctk.CTkLabel(filter_frame, text="开始:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, padx=(12, 2), pady=8)
        self.start_date = ctk.CTkEntry(filter_frame, width=110, placeholder_text="YYYY-MM-DD")
        self.start_date.grid(row=0, column=1, padx=(0, 8), pady=8)

        ctk.CTkLabel(filter_frame, text="结束:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=2, padx=(0, 2), pady=8)
        self.end_date = ctk.CTkEntry(filter_frame, width=110, placeholder_text="YYYY-MM-DD")
        self.end_date.grid(row=0, column=3, padx=(0, 8), pady=8)

        self.type_var = ctk.StringVar(value="全部")
        self.type_menu = ctk.CTkOptionMenu(filter_frame, values=["全部", "支出", "收入"],
                                           variable=self.type_var, width=80)
        self.type_menu.grid(row=0, column=4, padx=(0, 8), pady=8)

        self.keyword_entry = ctk.CTkEntry(filter_frame, width=140, placeholder_text="搜索备注...")
        self.keyword_entry.grid(row=0, column=5, padx=(0, 8), pady=8)

        search_btn = ctk.CTkButton(filter_frame, text="搜索", width=70,
                                   command=self._search)
        search_btn.grid(row=0, column=6, padx=(0, 16), pady=8)

        # --- Table ---
        self.table_frame = ctk.CTkScrollableFrame(self, fg_color=("gray95", "gray13"))
        self.table_frame.grid(row=2, column=0, sticky="nsew", padx=25, pady=(0, 5))

        # Table header
        self._build_table_header()

        # --- Pagination ---
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.grid(row=3, column=0, sticky="ew", padx=25, pady=(5, 20))
        self.prev_btn = ctk.CTkButton(nav_frame, text="上一页", width=80,
                                      command=self._prev_page)
        self.prev_btn.pack(side="left")
        self.page_label = ctk.CTkLabel(nav_frame, text="第 1 页", font=ctk.CTkFont(size=13))
        self.page_label.pack(side="left", padx=15)
        self.next_btn = ctk.CTkButton(nav_frame, text="下一页", width=80,
                                      command=self._next_page)
        self.next_btn.pack(side="left")

        # Total count
        self.total_label = ctk.CTkLabel(nav_frame, text="",
                                        font=ctk.CTkFont(size=13), text_color=("gray40", "gray60"))
        self.total_label.pack(side="right")

        # --- Edit dialog (hidden by default) ---
        self._edit_form = None

    def _build_table_header(self):
        header = ctk.CTkFrame(self.table_frame, fg_color=("gray85", "gray25"), height=36)
        header.pack(fill="x", padx=1, pady=(1, 0))
        cols = [
            ("日期", 0, 120),
            ("类型", 1, 70),
            ("分类", 2, 90),
            ("金额", 3, 110),
            ("备注", 4, 180),
            ("操作", 5, 120),
        ]
        for text, col, width in cols:
            lbl = ctk.CTkLabel(header, text=text, font=ctk.CTkFont(size=12, weight="bold"),
                             width=width)
            lbl.pack(side="left", padx=4, pady=5)

    def _search(self):
        self._offset = 0
        self._load_bills()

    def _prev_page(self):
        if self._offset >= self._page_size:
            self._offset -= self._page_size
            self._load_bills()

    def _next_page(self):
        self._offset += self._page_size
        self._load_bills()

    def _load_bills(self):
        # clear table (keep header)
        for w in self.table_frame.winfo_children()[1:]:
            w.destroy()

        # parse filters
        start = None
        end = None
        try:
            s = self.start_date.get().strip()
            if s:
                start = date.fromisoformat(s)
        except (ValueError, TypeError):
            start = None
        try:
            e = self.end_date.get().strip()
            if e:
                end = date.fromisoformat(e)
        except (ValueError, TypeError):
            end = None

        bill_type = None
        type_display = self.type_var.get()
        if type_display == "支出":
            bill_type = "expense"
        elif type_display == "收入":
            bill_type = "income"

        keyword = self.keyword_entry.get().strip()

        bills = self.db.get_bills(
            start_date=start, end_date=end,
            bill_type=bill_type, keyword=keyword,
            limit=self._page_size, offset=self._offset,
        )
        total = self.db.get_bill_count(
            start_date=start, end_date=end,
            bill_type=bill_type, keyword=keyword,
        )

        current_page = self._offset // self._page_size + 1
        total_pages = max(1, (total + self._page_size - 1) // self._page_size)
        self.page_label.configure(text=f"第 {current_page}/{total_pages} 页")
        self.total_label.configure(text=f"共 {total} 条记录")

        self.prev_btn.configure(state="normal" if self._offset > 0 else "disabled")
        self.next_btn.configure(state="normal" if self._offset + self._page_size < total else "disabled")

        if not bills:
            ctk.CTkLabel(self.table_frame, text="暂无数据",
                         text_color=("gray40", "gray60"), font=ctk.CTkFont(size=14)).pack(pady=30)
            return

        for bill in bills:
            self._add_bill_row(bill)

    def _add_bill_row(self, bill: Bill):
        row = ctk.CTkFrame(self.table_frame, fg_color="transparent", height=38)
        row.pack(fill="x", padx=1, pady=0)

        date_str = bill.bill_date.isoformat() if bill.bill_date else ""
        type_str = "收入" if bill.type == "income" else "支出"
        type_color = "#4CAF50" if bill.type == "income" else "#F44336"
        amount_str = f"{'+' if bill.type == 'income' else '-'}¥ {bill.amount:,.2f}"
        cat_str = bill.category_name or "-"
        desc_str = bill.description[:30] or "-"

        ctk.CTkLabel(row, text=date_str, font=ctk.CTkFont(size=12), width=120).pack(
            side="left", padx=4, pady=6)
        ctk.CTkLabel(row, text=type_str, font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=type_color, width=70).pack(side="left", padx=4, pady=6)
        ctk.CTkLabel(row, text=cat_str, font=ctk.CTkFont(size=12), width=90).pack(
            side="left", padx=4, pady=6)
        ctk.CTkLabel(row, text=amount_str, font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=type_color, width=110).pack(side="left", padx=4, pady=6)
        ctk.CTkLabel(row, text=desc_str, font=ctk.CTkFont(size=12),
                     text_color=("gray45", "gray55"), width=180).pack(side="left", padx=4, pady=6)

        btn_frame = ctk.CTkFrame(row, fg_color="transparent", width=120)
        btn_frame.pack(side="left", padx=4, pady=4)
        edit_btn = ctk.CTkButton(btn_frame, text="编辑", width=50, height=28,
                                 font=ctk.CTkFont(size=11),
                                 command=lambda b=bill: self._show_edit(b))
        edit_btn.pack(side="left", padx=(0, 4))
        del_btn = ctk.CTkButton(btn_frame, text="删除", width=50, height=28,
                                font=ctk.CTkFont(size=11),
                                fg_color="#C62828", hover_color="#B71C1C",
                                command=lambda b=bill: self._delete_bill(b))
        del_btn.pack(side="left")

        # separator line
        sep = ctk.CTkFrame(self.table_frame, height=1, fg_color=("gray85", "gray25"))
        sep.pack(fill="x", padx=4)

    def _delete_bill(self, bill: Bill):
        if messagebox.askyesno("确认删除", f"确定要删除这笔账单吗？\n¥{bill.amount:,.2f}"):
            self.db.delete_bill(bill.id)
            self._load_bills()

    def _show_edit(self, bill: Bill):
        dialog = ctk.CTkToplevel(self)
        dialog.title("编辑账单")
        dialog.geometry("480x440")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)

        from ui.components.bill_form import BillForm
        form = BillForm(dialog, self.app, bill=bill,
                        on_save=lambda: [self._load_bills(), dialog.destroy()])
        form.pack(fill="both", expand=True)

    def on_show(self):
        self._offset = 0
        self._load_bills()

    def refresh(self):
        self._load_bills()
