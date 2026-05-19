import customtkinter as ctk
from datetime import date

from utils.date_utils import get_month_range


class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app
        self.db = app.db

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Header ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=25, pady=(25, 10))
        ctk.CTkLabel(header, text="仪表盘",
                     font=ctk.CTkFont(size=26, weight="bold")).pack(side="left")
        today_str = date.today().isoformat()
        ctk.CTkLabel(header, text=today_str,
                     font=ctk.CTkFont(size=14),
                     text_color=("gray40", "gray60")).pack(side="right")

        # --- Today stats row ---
        self.today_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.today_frame.grid(row=1, column=0, sticky="ew", padx=25, pady=(0, 5))
        for i in range(3):
            self.today_frame.grid_columnconfigure(i, weight=1)

        self.today_income_card = self._make_stat_card(self.today_frame, "今日收入", "#4CAF50", 0, 0)
        self.today_expense_card = self._make_stat_card(self.today_frame, "今日支出", "#F44336", 0, 1)
        self.today_balance_card = self._make_stat_card(self.today_frame, "今日结余", "#2196F3", 0, 2)

        # --- Month stats row ---
        self.month_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.month_frame.grid(row=2, column=0, sticky="ew", padx=25, pady=(0, 15))
        for i in range(3):
            self.month_frame.grid_columnconfigure(i, weight=1)

        self.month_income_card = self._make_stat_card(self.month_frame, "本月收入", "#81C784", 0, 0)
        self.month_expense_card = self._make_stat_card(self.month_frame, "本月支出", "#EF9A9A", 0, 1)
        self.month_balance_card = self._make_stat_card(self.month_frame, "本月结余", "#64B5F6", 0, 2)

        # --- Recent bills ---
        recent_frame = ctk.CTkFrame(self)
        recent_frame.grid(row=3, column=0, sticky="nsew", padx=25, pady=(0, 25))
        recent_frame.grid_rowconfigure(1, weight=1)
        recent_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(recent_frame, text="最近账单",
                     font=ctk.CTkFont(size=17, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=18, pady=(15, 8))

        self.recent_list = ctk.CTkScrollableFrame(recent_frame, fg_color="transparent")
        self.recent_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

    def _make_stat_card(self, parent, title: str, color: str, row: int, col: int):
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color=("gray90", "gray20"))
        card.grid(row=row, column=col, padx=6, pady=6, sticky="ew")

        # color indicator bar
        indicator = ctk.CTkFrame(card, height=4, fg_color=color, corner_radius=0)
        indicator.pack(fill="x", padx=1, pady=(1, 0))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=(10, 14))
        ctk.CTkLabel(inner, text=title,
                     font=ctk.CTkFont(size=13),
                     text_color=("gray40", "gray60")).pack(anchor="w")
        amount_label = ctk.CTkLabel(inner, text="¥ 0.00",
                                    font=ctk.CTkFont(size=26, weight="bold"))
        amount_label.pack(anchor="w", pady=(2, 0))
        card.amount_label = amount_label
        return card

    def on_show(self):
        self.refresh()

    def refresh(self):
        today = date.today()
        month_start, month_end = get_month_range()

        today_summary = self.db.get_summary(today, today)
        month_summary = self.db.get_summary(month_start, month_end)

        self._set_card(self.today_income_card, today_summary.total_income)
        self._set_card(self.today_expense_card, today_summary.total_expense)
        self._set_card(self.today_balance_card, today_summary.balance)
        self._set_card(self.month_income_card, month_summary.total_income)
        self._set_card(self.month_expense_card, month_summary.total_expense)
        self._set_card(self.month_balance_card, month_summary.balance)

        # recent bills
        for w in self.recent_list.winfo_children():
            w.destroy()
        bills = self.db.get_bills(limit=5)
        if not bills:
            ctk.CTkLabel(self.recent_list, text="暂无账单记录",
                         text_color=("gray40", "gray60"),
                         font=ctk.CTkFont(size=13)).pack(pady=20)
        else:
            for bill in bills:
                self._add_recent_row(bill)

    def _set_card(self, card, value):
        card.amount_label.configure(text=f"¥ {value:,.2f}")

    def _add_recent_row(self, bill):
        row = ctk.CTkFrame(self.recent_list, fg_color="transparent", height=40)
        row.pack(fill="x", padx=5, pady=1)

        sign = "+" if bill.type == "income" else "-"
        color = "#4CAF50" if bill.type == "income" else "#F44336"
        cat_name = bill.category_name or "未分类"
        desc = bill.description or ""
        date_str = bill.bill_date.isoformat() if bill.bill_date else ""

        ctk.CTkLabel(row, text=cat_name,
                     font=ctk.CTkFont(size=13)).pack(side="left", padx=(5, 10))
        if desc:
            ctk.CTkLabel(row, text=desc[:20],
                         font=ctk.CTkFont(size=12),
                         text_color=("gray40", "gray60")).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(row, text=date_str,
                     font=ctk.CTkFont(size=12),
                     text_color=("gray40", "gray60")).pack(side="right", padx=(0, 5))
        ctk.CTkLabel(row, text=f"{sign}¥{bill.amount:,.2f}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=color).pack(side="right", padx=10)
