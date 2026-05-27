"""Summary page - period stats with charts."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame, QScrollArea)
from PySide6.QtCore import Qt

from datetime import date, timedelta
from ui.theme import COLORS, set_css_class, FONT_FAMILY
from ui.utils import make_label, make_title, clear_layout
from ui.components.stat_card import StatCard
from ui.components.card import Card
from ui.components.chart_view import ChartView
from utils.date_utils import get_date_range_label


class SummaryPage(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.db = app.db
        self._current_period = "month"
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(24)

        # Header with period selector
        header = QHBoxLayout()
        header.addWidget(make_title("统计分析"))

        period_frame = QHBoxLayout()
        period_frame.setSpacing(4)
        self.period_buttons = {}
        for text, period in [("日", "day"), ("周", "week"), ("月", "month"), ("年", "year")]:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedSize(48, 36)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['surface']};
                    color: {COLORS['text_secondary']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                    font-size: 13px;
                    font-family: {FONT_FAMILY};
                }}
                QPushButton:hover {{
                    border-color: {COLORS['primary']};
                    color: {COLORS['primary']};
                }}
                QPushButton:checked {{
                    background-color: {COLORS['primary']};
                    color: white;
                }}
            """)
            btn.clicked.connect(lambda checked, p=period: self._on_period_change(p))
            period_frame.addWidget(btn)
            self.period_buttons[period] = btn
        self.period_buttons["month"].setChecked(True)

        header.addStretch()
        header.addLayout(period_frame)
        layout.addLayout(header)

        # Stats
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        self.income_card = StatCard("总收入", COLORS['success'])
        self.expense_card = StatCard("总支出", COLORS['danger'])
        self.balance_card = StatCard("结余", COLORS['info'])
        stats_layout.addWidget(self.income_card)
        stats_layout.addWidget(self.expense_card)
        stats_layout.addWidget(self.balance_card)
        layout.addLayout(stats_layout)

        # Charts
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(16)

        pie_card = Card(padding=(16, 12, 16, 12))
        self.pie_chart = ChartView()
        pie_card.content_layout().addWidget(self.pie_chart)
        charts_layout.addWidget(pie_card, 1)

        bar_card = Card(padding=(16, 12, 16, 12))
        self.bar_chart = ChartView()
        bar_card.content_layout().addWidget(self.bar_chart)
        charts_layout.addWidget(bar_card, 1)

        layout.addLayout(charts_layout, 1)

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _on_period_change(self, period):
        self._current_period = period
        for p, btn in self.period_buttons.items():
            btn.setChecked(p == period)
        self._load_data()

    def _load_data(self):
        period = self._current_period
        start, end = get_date_range_label(period)

        summary = self.db.get_summary(start, end)
        self.income_card.set_value(summary.total_income)
        self.expense_card.set_value(summary.total_expense)
        balance = summary.balance
        sign = "+" if balance >= 0 else "-"
        self.balance_card.set_value_text(f"{sign}¥ {abs(balance):,.2f}")

        cat_data = self.db.get_category_summary(start, end, "expense")
        self.pie_chart.pie_chart(cat_data, "支出分类分布")

        if period == "year":
            # 年分析：年度总收入 vs 总支出对比
            self.bar_chart.bar_chart(
                [f"{start.year}年"],
                [summary.total_income],
                [summary.total_expense],
                "年度收支对比",
            )
        elif period == "month":
            # 月分析：展示当前年份 12 个月的收支柱状图（补全空月为 0）
            from datetime import date as _date
            year_start = _date(start.year, 1, 1)
            year_end = _date(start.year, 12, 31)
            labels, incomes, expenses = self._get_monthly_trend(year_start, year_end, fill_all_months=True)
            self.bar_chart.bar_chart(labels, incomes, expenses, f"{start.year}年月度收支趋势")
        else:
            trend = self.db.get_daily_trend(start, end)
            if trend:
                labels = [t[0] for t in trend]
                incomes = [t[1] for t in trend]
                expenses = [t[2] for t in trend]
            else:
                labels, incomes, expenses = [], [], []
            self.bar_chart.bar_chart(labels, incomes, expenses, "收支趋势")

    def _get_monthly_trend(self, start_date, end_date, fill_all_months=False):
        """Aggregate daily data into monthly buckets. Labels show MM月.

        When fill_all_months=True, all 12 months of the year are included
        even if they have no data (shown as 0).
        """
        trend = self.db.get_daily_trend(start_date, end_date)

        monthly = {}
        if trend:
            for day_str, income, expense in trend:
                month_key = day_str[:7]  # "YYYY-MM"
                if month_key not in monthly:
                    monthly[month_key] = [0.0, 0.0]
                monthly[month_key][0] += income
                monthly[month_key][1] += expense

        if fill_all_months:
            year = start_date.year
            all_months = {}
            for m in range(1, 13):
                key = f"{year}-{m:02d}"
                all_months[key] = monthly.get(key, [0.0, 0.0])
            monthly = all_months

        sorted_months = sorted(monthly.keys())
        labels = [f"{int(m[5:])}月" for m in sorted_months]
        incomes = [monthly[m][0] for m in sorted_months]
        expenses = [monthly[m][1] for m in sorted_months]
        return labels, incomes, expenses

    def on_show(self):
        self._load_data()

    def refresh(self):
        self._load_data()
