"""Dashboard page - Apple-style card grid layout."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame, QScrollArea)
from PySide6.QtCore import Qt

from datetime import date
from ui.theme import COLORS, set_css_class, FONT_FAMILY
from ui.utils import make_label, make_title, make_subtitle, clear_layout
from ui.components.card import Card
from ui.components.stat_card import StatCard
from ui.components.badge import Badge
from ui.components.progress_bar import ProgressBar
from ui.components.empty_state import EmptyState
from utils.date_utils import get_month_range
from core.analytics import calculate_health_score


class DashboardPage(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.db = app.db
        self._week_offset = 0
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(24)

        # Header
        header = QHBoxLayout()
        header.addWidget(make_title("仪表盘"))
        header.addStretch()
        header.addWidget(make_label(date.today().isoformat(), 14, color=COLORS['text_tertiary']))
        layout.addLayout(header)

        # Weekly Report Card
        report_card = Card(padding=(24, 24, 24, 24), spacing=12)
        report_layout = report_card.content_layout()

        nav_row = QHBoxLayout()
        self.prev_btn = QPushButton("◀ 上周")
        self.prev_btn.setFixedSize(80, 32)
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['border_light']};
                border: none;
                border-radius: 8px;
                font-size: 12px;
                padding: 6px 12px;
                font-family: {FONT_FAMILY};
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
            }}
        """)
        self.prev_btn.clicked.connect(lambda: self._nav_week(-1))
        nav_row.addWidget(self.prev_btn)

        self.report_title = make_label("本周财务周报", 16, True)
        nav_row.addWidget(self.report_title)

        self.next_btn = QPushButton("下周 ▶")
        self.next_btn.setFixedSize(80, 32)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['border_light']};
                border: none;
                border-radius: 8px;
                font-size: 12px;
                padding: 6px 12px;
                font-family: {FONT_FAMILY};
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
            }}
        """)
        self.next_btn.clicked.connect(lambda: self._nav_week(1))
        nav_row.addWidget(self.next_btn)
        report_layout.addLayout(nav_row)

        self.report_text = make_label("", 13, color=COLORS['text_secondary'])
        self.report_text.setWordWrap(True)
        report_layout.addWidget(self.report_text)

        self.badges_layout = QHBoxLayout()
        self.badges_layout.setSpacing(8)
        report_layout.addLayout(self.badges_layout)

        layout.addWidget(report_card)

        # Health Score Card
        health_card = Card(padding=(24, 24, 24, 24), spacing=12)
        health_layout = health_card.content_layout()

        score_row = QHBoxLayout()
        score_row.setAlignment(Qt.AlignCenter)
        score_row.setSpacing(4)
        self.score_label = make_label("--", 48, True, COLORS['success'])
        self.score_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        score_row.addWidget(self.score_label)
        score_unit = make_label("分", 16, color=COLORS['text_tertiary'])
        score_unit.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        score_row.addWidget(score_unit)
        score_row.addStretch()
        health_layout.addLayout(score_row)

        detail_col = QVBoxLayout()
        detail_col.setSpacing(8)
        self.rating_label = make_label("财务健康", 16, True)
        detail_col.addWidget(self.rating_label)

        self.bar_frame = QVBoxLayout()
        self.bar_frame.setSpacing(6)
        detail_col.addLayout(self.bar_frame)
        health_layout.addLayout(detail_col, 1)

        layout.addWidget(health_card)

        # Stats - Today
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        self.today_income = StatCard("今日收入", COLORS['success'])
        self.today_expense = StatCard("今日支出", COLORS['danger'])
        self.today_balance = StatCard("今日结余", COLORS['info'])
        stats_layout.addWidget(self.today_income)
        stats_layout.addWidget(self.today_expense)
        stats_layout.addWidget(self.today_balance)
        layout.addLayout(stats_layout)

        # Stats - Month
        stats_layout2 = QHBoxLayout()
        stats_layout2.setSpacing(16)
        self.month_income = StatCard("本月收入", COLORS['success'])
        self.month_expense = StatCard("本月支出", COLORS['danger'])
        self.month_balance = StatCard("本月结余", COLORS['info'])
        stats_layout2.addWidget(self.month_income)
        stats_layout2.addWidget(self.month_expense)
        stats_layout2.addWidget(self.month_balance)
        layout.addLayout(stats_layout2)

        # Recent Bills Card
        recent_card = Card(padding=(24, 24, 24, 24), spacing=12)
        recent_layout = recent_card.content_layout()

        recent_layout.addWidget(make_label("最近账单", 17, True))
        self.recent_list = QVBoxLayout()
        self.recent_list.setSpacing(8)
        recent_layout.addLayout(self.recent_list)

        layout.addWidget(recent_card, 1)
        layout.addStretch()

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _nav_week(self, delta):
        self._week_offset += delta
        if self._week_offset > 0:
            self._week_offset = 0
            return
        self._load_report()

    def _load_report(self):
        from core.report_generator import generate_weekly_report
        report = generate_weekly_report(self.db, self._week_offset)

        self.prev_btn.setEnabled(True)
        self.next_btn.setEnabled(self._week_offset < 0)

        if report is None:
            self.report_title.setText("本周财务周报（暂无数据）")
            self.report_text.setText("这周还没有记账记录。开始记一笔吧！")
            self._clear_badges()
            return

        is_current = (self._week_offset == 0)
        title = f"{'本周' if is_current else ''}财务周报（{report['week_label']}）"
        self.report_title.setText(title)
        self.report_text.setText(report["report_text"])

        self._clear_badges()
        if report["record_days"] == report["checked_days"]:
            self.badges_layout.addWidget(Badge("全勤记录", COLORS['success']))
        if report["savings_rate"] > 40:
            self.badges_layout.addWidget(Badge("高储蓄率", COLORS['info']))
        if report["balance"] < 0 and report["total_expense"] > 0:
            self.badges_layout.addWidget(Badge("入不敷出", COLORS['danger']))

    def _clear_badges(self):
        clear_layout(self.badges_layout)

    def _update_health_card(self, health):
        score = health["score"]
        color = health["color"]
        self.score_label.setText(str(score))
        self.score_label.setStyleSheet(f"color: {color}; font-size: 48px; font-weight: bold;")
        self.rating_label.setText(f"财务健康 · {health['label']}")
        self.rating_label.setStyleSheet(f"color: {color}; font-weight: bold;")

        clear_layout(self.bar_frame)

        bd = health["breakdown"]
        dim_colors = {"savings": COLORS['success'], "coverage": COLORS['info'],
                      "consistency": COLORS['warning'], "diversity": "#AF52DE"}
        for key in ["savings", "coverage", "consistency", "diversity"]:
            item = bd[key]
            bar = ProgressBar(item["label"], item["score"], item["max"],
                              color=dim_colors.get(key, '#888'), show_value=True)
            bar.set_bar_width(300)
            self.bar_frame.addWidget(bar)

    def _add_recent_row(self, bill):
        row = QHBoxLayout()
        row.setSpacing(12)

        cat_name = bill.category_name or "未分类"
        row.addWidget(make_label(cat_name, 13))

        desc = bill.description or ""
        if desc:
            row.addWidget(make_label(desc[:20], 12, color=COLORS['text_tertiary']))

        row.addStretch()

        date_str = bill.bill_date.isoformat() if bill.bill_date else ""
        row.addWidget(make_label(date_str, 12, color=COLORS['text_tertiary']))

        sign = "+" if bill.type == "income" else "-"
        color = COLORS['success'] if bill.type == "income" else COLORS['danger']
        row.addWidget(make_label(f"{sign}¥{bill.amount:,.2f}", 14, True, color))

        self.recent_list.addLayout(row)

    def on_show(self):
        self.refresh()

    def refresh(self):
        today = date.today()
        month_start, month_end = get_month_range()

        self._load_report()

        health = calculate_health_score(self.db)
        self._update_health_card(health)

        today_summary = self.db.get_summary(today, today)
        month_summary = self.db.get_summary(month_start, month_end)
        self.today_income.set_value(today_summary.total_income)
        self.today_expense.set_value(today_summary.total_expense)
        self.today_balance.set_value(today_summary.balance)
        self.month_income.set_value(month_summary.total_income)
        self.month_expense.set_value(month_summary.total_expense)
        self.month_balance.set_value(month_summary.balance)

        clear_layout(self.recent_list)

        bills = self.db.get_bills(limit=5)
        if not bills:
            self.recent_list.addWidget(EmptyState("📭", "暂无账单", "开始记一笔吧"))
        else:
            for bill in bills:
                self._add_recent_row(bill)
