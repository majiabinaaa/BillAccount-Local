"""Bill list page - clean table with refined filters."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame, QTableWidget, QTableWidgetItem,
                               QLineEdit, QComboBox, QHeaderView, QMessageBox,
                               QDialog, QDateEdit, QCalendarWidget)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor

from datetime import date
from ui.theme import COLORS, set_css_class, FONT_FAMILY
from ui.utils import make_label, make_title, make_subtitle
from ui.components.empty_state import EmptyState
from core.models import Bill


class DatePicker(QWidget):
    """Date picker with a text display and a calendar button."""
    def __init__(self, initial_date=None, parent=None):
        super().__init__(parent)
        self._date = initial_date or date.today()
        self._popup = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._display = QLineEdit()
        self._display.setReadOnly(True)
        self._display.setFixedHeight(36)
        self._display.setMinimumWidth(110)
        self._display.setText(self._date.isoformat())
        self._display.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['input_border']};
                border-radius: 8px;
                padding: 8px 10px;
                font-size: 13px;
                color: {COLORS['text_primary']};
                font-family: {FONT_FAMILY};
            }}
        """)
        layout.addWidget(self._display)

        self._btn = QPushButton("📅")
        self._btn.setFixedSize(36, 36)
        self._btn.setCursor(Qt.PointingHandCursor)
        self._btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['border_light']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
            }}
        """)
        self._btn.clicked.connect(self._show_calendar)
        layout.addWidget(self._btn)

    def date(self):
        return self._date

    def setDate(self, d):
        self._date = d
        self._display.setText(d.isoformat())

    def _show_calendar(self):
        if self._popup and self._popup.isVisible():
            self._popup.close()
            return

        self._popup = QWidget(self, Qt.Popup)
        self._popup.setStyleSheet(f"""
            QWidget {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
            }}
        """)
        cal_layout = QVBoxLayout(self._popup)
        cal_layout.setContentsMargins(4, 4, 4, 4)

        cal = QCalendarWidget()
        cal.setSelectedDate(QDate(self._date.year, self._date.month, self._date.day))
        cal.setGridVisible(True)
        cal.setStyleSheet(f"""
            QCalendarWidget {{
                background: transparent;
                border: none;
            }}
            QCalendarWidget QToolButton {{
                color: {COLORS['text_primary']};
                background: transparent;
                font-size: 13px;
            }}
            QCalendarWidget QAbstractItemView {{
                selection-background-color: {COLORS['primary']};
                selection-color: white;
            }}
        """)
        cal.clicked.connect(lambda d: self._on_date_selected(d))
        cal_layout.addWidget(cal)

        # Position below the button
        btn_pos = self._btn.mapToGlobal(self._btn.rect().bottomLeft())
        self._popup.move(btn_pos)
        self._popup.show()

    def _on_date_selected(self, qdate):
        self._date = qdate.toPython()
        self._display.setText(self._date.isoformat())
        if self._popup:
            self._popup.close()


class BillListPage(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.db = app.db
        self._offset = 0
        self._page_size = 50
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        header.addWidget(make_title("账单列表"))
        header.addStretch()
        layout.addLayout(header)

        # Filters
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        self.start_date = DatePicker(date(2020, 1, 1))
        filter_layout.addWidget(self.start_date)

        filter_layout.addWidget(make_label("~", 13, color=COLORS['text_tertiary']))

        self.end_date = DatePicker(date.today())
        filter_layout.addWidget(self.end_date)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["全部", "支出", "收入"])
        self.type_combo.setFixedHeight(36)
        self.type_combo.setMinimumWidth(80)
        filter_layout.addWidget(self.type_combo)

        self.keyword_entry = QLineEdit()
        self.keyword_entry.setPlaceholderText("搜索备注...")
        self.keyword_entry.setFixedHeight(36)
        self.keyword_entry.setMinimumWidth(120)
        filter_layout.addWidget(self.keyword_entry)

        search_btn = QPushButton("搜索")
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.setFixedHeight(36)
        search_btn.setMinimumWidth(64)
        set_css_class(search_btn, "primary-btn")
        search_btn.clicked.connect(self._search)
        filter_layout.addWidget(search_btn)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["日期", "类型", "分类", "金额", "备注", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 120)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)

        # Pagination
        nav_layout = QHBoxLayout()

        self.prev_btn = QPushButton("上一页")
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        set_css_class(self.prev_btn, "ghost-btn")
        self.prev_btn.clicked.connect(self._prev_page)
        self.prev_btn.setEnabled(False)
        nav_layout.addWidget(self.prev_btn)

        self.page_label = make_label("第 1 页", 13, color=COLORS['text_tertiary'])
        nav_layout.addWidget(self.page_label)

        self.next_btn = QPushButton("下一页")
        self.next_btn.setCursor(Qt.PointingHandCursor)
        set_css_class(self.next_btn, "ghost-btn")
        self.next_btn.clicked.connect(self._next_page)
        self.next_btn.setEnabled(False)
        nav_layout.addWidget(self.next_btn)

        nav_layout.addStretch()
        self.total_label = make_label("", 13, color=COLORS['text_tertiary'])
        nav_layout.addWidget(self.total_label)

        layout.addLayout(nav_layout)

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
        self.table.setRowCount(0)
        start = self.start_date.date()
        end = self.end_date.date()

        bill_type = None
        type_display = self.type_combo.currentText()
        if type_display == "支出":
            bill_type = "expense"
        elif type_display == "收入":
            bill_type = "income"

        keyword = self.keyword_entry.text().strip()
        bills = self.db.get_bills(start_date=start, end_date=end, bill_type=bill_type,
                                  keyword=keyword, limit=self._page_size, offset=self._offset)
        total = self.db.get_bill_count(start_date=start, end_date=end, bill_type=bill_type, keyword=keyword)

        current_page = self._offset // self._page_size + 1
        total_pages = max(1, (total + self._page_size - 1) // self._page_size)
        self.page_label.setText(f"第 {current_page}/{total_pages} 页")
        self.total_label.setText(f"共 {total} 条记录")

        self.prev_btn.setEnabled(self._offset > 0)
        self.next_btn.setEnabled(self._offset + self._page_size < total)

        for bill in bills:
            self._add_bill_row(bill)

    def _add_bill_row(self, bill: Bill):
        row = self.table.rowCount()
        self.table.insertRow(row)

        date_str = bill.bill_date.isoformat() if bill.bill_date else ""
        type_str = "收入" if bill.type == "income" else "支出"
        type_color = COLORS['success'] if bill.type == "income" else COLORS['danger']
        amount_str = f"{'+' if bill.type == 'income' else '-'}¥ {bill.amount:,.2f}"
        cat_str = bill.category_name or "-"
        desc_str = (bill.description or "")[:30] or "-"

        self.table.setItem(row, 0, QTableWidgetItem(date_str))

        type_item = QTableWidgetItem(type_str)
        type_item.setForeground(QColor(type_color))
        self.table.setItem(row, 1, type_item)

        self.table.setItem(row, 2, QTableWidgetItem(cat_str))

        amount_item = QTableWidgetItem(amount_str)
        amount_item.setForeground(QColor(type_color))
        font = QFont()
        font.setFamily(FONT_FAMILY)
        font.setBold(True)
        amount_item.setFont(font)
        self.table.setItem(row, 3, amount_item)

        self.table.setItem(row, 4, QTableWidgetItem(desc_str))

        # Action buttons
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(4, 4, 4, 4)
        action_layout.setSpacing(4)

        edit_btn = QPushButton("编辑")
        edit_btn.setCursor(Qt.PointingHandCursor)
        set_css_class(edit_btn, "link-btn")
        edit_btn.setStyleSheet(f"color: {COLORS['primary']};")
        edit_btn.clicked.connect(lambda checked, b=bill: self._show_edit(b))
        action_layout.addWidget(edit_btn)

        del_btn = QPushButton("删除")
        del_btn.setCursor(Qt.PointingHandCursor)
        set_css_class(del_btn, "link-btn")
        del_btn.setStyleSheet(f"color: {COLORS['danger']};")
        del_btn.clicked.connect(lambda checked, b=bill: self._delete_bill(b))
        action_layout.addWidget(del_btn)

        self.table.setCellWidget(row, 5, action_widget)

    def _delete_bill(self, bill: Bill):
        reply = QMessageBox.question(self, "确认删除", f"确定要删除这笔账单吗？\n¥{bill.amount:,.2f}",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_bill(bill.id)
            self._load_bills()

    def _show_edit(self, bill: Bill):
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑账单")
        dialog.setFixedSize(480, 440)
        dialog.setWindowModality(Qt.WindowModal)

        from ui.components.bill_form import BillForm
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 24, 24, 24)
        form = BillForm(self.app, bill=bill, on_save=lambda: [self._load_bills(), dialog.accept()])
        layout.addWidget(form)
        dialog.exec()

    def on_show(self):
        self._offset = 0
        self._load_bills()

    def refresh(self):
        self._load_bills()
