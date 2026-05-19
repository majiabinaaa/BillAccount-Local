import customtkinter as ctk
from datetime import date, timedelta

from utils.date_utils import (
    get_date_range_label, get_weeks_in_month, get_months_in_year,
)
from ui.components.chart_view import ChartView


class SummaryPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app
        self.db = app.db
        self._current_period = "month"  # use callback value, not variable

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = ctk.CTkFrame(self)
        container.grid(row=0, column=0, sticky="nsew", padx=25, pady=(25, 20))
        container.grid_rowconfigure(2, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # ---- Header ----
        top = ctk.CTkFrame(container, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 8))

        ctk.CTkLabel(top, text="统计分析",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")

        self.period_seg = ctk.CTkSegmentedButton(
            top, values=["日", "周", "月", "年"],
            command=self._on_period_change,
        )
        self.period_seg.pack(side="right")
        self.period_seg.set("月")

        # ---- Summary cards ----
        cards_frame = ctk.CTkFrame(container, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(5, 10))
        for i in range(3):
            cards_frame.grid_columnconfigure(i, weight=1)

        self.income_card = self._make_card(cards_frame, "总收入", "#4CAF50")
        self.income_card.grid(row=0, column=0, padx=6, sticky="ew")
        self.expense_card = self._make_card(cards_frame, "总支出", "#F44336")
        self.expense_card.grid(row=0, column=1, padx=6, sticky="ew")
        self.balance_card = self._make_card(cards_frame, "结余", "#2196F3")
        self.balance_card.grid(row=0, column=2, padx=6, sticky="ew")

        # ---- Chart area ----
        self.chart_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.chart_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.chart_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(1, weight=1)

    def _make_card(self, parent, title: str, color: str):
        card = ctk.CTkFrame(parent, corner_radius=10)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=16, pady=14, fill="x")
        ctk.CTkLabel(inner, text=title, font=ctk.CTkFont(size=12),
                     text_color=("gray45", "gray55")).pack(anchor="w")
        amount_lbl = ctk.CTkLabel(inner, text="¥ 0.00",
                                  font=ctk.CTkFont(size=24, weight="bold"),
                                  text_color=color)
        amount_lbl.pack(anchor="w", pady=(2, 0))
        card.amount_label = amount_lbl
        return card

    def _on_period_change(self, value: str):
        """value is the clicked segment text: '日'/'周'/'月'/'年'"""
        period_map = {"日": "day", "周": "week", "月": "month", "年": "year"}
        self._current_period = period_map.get(value, "month")
        self._load_data()

    def on_show(self):
        self._load_data()

    def refresh(self):
        self._load_data()

    # ------------------------------------------------------------------
    def _load_data(self):
        period = self._current_period
        start, end = get_date_range_label(period)

        summary = self.db.get_summary(start, end)
        self.income_card.amount_label.configure(text=f"¥ {summary.total_income:,.2f}")
        self.expense_card.amount_label.configure(text=f"¥ {summary.total_expense:,.2f}")
        balance = summary.balance
        self.balance_card.amount_label.configure(
            text=f"{'+' if balance >= 0 else '-'}¥ {abs(balance):,.2f}")

        # clear old charts
        for w in self.chart_frame.winfo_children():
            w.destroy()

        expense_data = self.db.get_category_summary(start, end, "expense")

        if period == "day":
            self._render_day(expense_data)
        elif period == "week":
            self._render_week(expense_data, start)
        elif period == "month":
            self._render_month(expense_data, start)
        elif period == "year":
            self._render_year(expense_data, start)

    # ---- Day: single pie chart ----
    def _render_day(self, expense_data):
        self.chart_frame.grid_columnconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(1, weight=0)
        pie = ChartView(self.chart_frame)
        pie.grid(row=0, column=0, sticky="nsew", padx=40, pady=5)
        pie.pie_chart(expense_data, "今日支出分类")

    # ---- Week: pie + weekly bars (weeks of this month) ----
    def _render_week(self, expense_data, start):
        self.chart_frame.grid_columnconfigure(1, weight=1)
        pie = ChartView(self.chart_frame)
        pie.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        pie.pie_chart(expense_data, "本周支出分类")

        bar = ChartView(self.chart_frame)
        bar.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        weeks = get_weeks_in_month(start.year, start.month)
        labels, incomes, expenses = [], [], []
        for ws, we in weeks:
            s = self.db.get_summary(ws, we)
            labels.append(f"{ws.month}/{ws.day}-{we.day}")
            incomes.append(s.total_income)
            expenses.append(s.total_expense)
        bar.bar_chart(labels, incomes, expenses, f"{start.year}年{start.month}月 周收支")

    # ---- Month: pie + monthly bars (months of this year) ----
    def _render_month(self, expense_data, start):
        self.chart_frame.grid_columnconfigure(1, weight=1)
        pie = ChartView(self.chart_frame)
        pie.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        pie.pie_chart(expense_data, "本月支出分类")

        bar = ChartView(self.chart_frame)
        bar.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        months = get_months_in_year(start.year)
        labels, incomes, expenses = [], [], []
        for ms, me in months:
            s = self.db.get_summary(ms, me)
            labels.append(f"{ms.month}月")
            incomes.append(s.total_income)
            expenses.append(s.total_expense)
        bar.bar_chart(labels, incomes, expenses, f"{start.year}年 月收支")

    # ---- Year: pie + yearly bars (all available years) ----
    def _render_year(self, expense_data, start):
        self.chart_frame.grid_columnconfigure(1, weight=1)
        pie = ChartView(self.chart_frame)
        pie.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        pie.pie_chart(expense_data, "本年支出分类")

        bar = ChartView(self.chart_frame)
        bar.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        labels, incomes, expenses = [], [], []
        # get all years that have data
        current_year = start.year
        for year in range(current_year - 2, current_year + 1):
            ys = date(year, 1, 1)
            ye = date(year, 12, 31)
            s = self.db.get_summary(ys, ye)
            if s.total_income > 0 or s.total_expense > 0 or year == current_year:
                labels.append(f"{year}年")
                incomes.append(s.total_income)
                expenses.append(s.total_expense)
        bar.bar_chart(labels, incomes, expenses, "每年收支")
