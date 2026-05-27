"""Reusable bill entry/edit form with Apple-style design."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QComboBox, QDateEdit,
                               QFrame)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from datetime import date
from typing import Callable, Optional

from core.models import Bill
from ui.theme import COLORS, set_css_class, FONT_FAMILY
from ui.utils import make_label


class BillForm(QWidget):
    def __init__(self, app, bill: Optional[Bill] = None, on_save: Callable = None, parent=None):
        super().__init__(parent)
        self.app = app
        self.db = app.db
        self.bill = bill
        self.on_save = on_save
        self._build_form()
        if bill:
            self._populate(bill)

    def _build_form(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)

        # Amount
        layout.addWidget(make_label("金额", 14, True))
        self.amount_entry = QLineEdit()
        self.amount_entry.setPlaceholderText("输入金额")
        self.amount_entry.setFixedHeight(52)
        font = QFont()
        font.setFamily(FONT_FAMILY)
        font.setPointSize(22)
        self.amount_entry.setFont(font)
        set_css_class(self.amount_entry, "underline-input")
        layout.addWidget(self.amount_entry)

        # Type selector - two separate buttons
        layout.addWidget(make_label("类型", 14, True))
        type_row = QHBoxLayout()
        type_row.setSpacing(12)

        self.type_buttons = {}
        for text, value in [("支出", "expense"), ("收入", "income")]:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setFixedHeight(44)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumWidth(120)
            btn.clicked.connect(lambda checked, v=value: self._on_type_change(v))
            type_row.addWidget(btn)
            self.type_buttons[value] = btn

        type_row.addStretch()
        layout.addLayout(type_row)

        self.type_buttons["expense"].setChecked(True)
        self._current_type = "expense"
        self._update_type_button_styles()

        # Category and Date
        row = QHBoxLayout()
        row.setSpacing(20)

        cat_col = QVBoxLayout()
        cat_col.setSpacing(8)
        cat_col.addWidget(make_label("分类", 14, True))
        self.category_combo = QComboBox()
        self.category_combo.setFixedHeight(40)
        cat_col.addWidget(self.category_combo)
        row.addLayout(cat_col, 1)

        date_col = QVBoxLayout()
        date_col.setSpacing(8)
        date_col.addWidget(make_label("日期", 14, True))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setFixedHeight(40)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        date_col.addWidget(self.date_edit)
        row.addLayout(date_col, 1)

        layout.addLayout(row)

        # Description
        layout.addWidget(make_label("备注", 14, True))
        self.desc_entry = QLineEdit()
        self.desc_entry.setPlaceholderText("添加备注 (可选)")
        self.desc_entry.setFixedHeight(40)
        layout.addWidget(self.desc_entry)

        # Error label
        self.error_label = QLabel()
        set_css_class(self.error_label, "error-text")
        layout.addWidget(self.error_label)

        # Submit button
        btn_text = "修改账单" if self.bill else "记一笔"
        self.submit_btn = QPushButton(btn_text)
        self.submit_btn.setFixedHeight(48)
        self.submit_btn.setCursor(Qt.PointingHandCursor)
        set_css_class(self.submit_btn, "primary-btn")
        self.submit_btn.setStyleSheet(f"""
            QPushButton {{
                border-radius: 24px;
                font-size: 16px;
            }}
        """)
        self.submit_btn.clicked.connect(self._submit)
        layout.addWidget(self.submit_btn)

        self._load_categories()

    def _load_categories(self):
        cats = self.db.get_categories(self._current_type)
        self.category_combo.clear()
        for c in cats:
            self.category_combo.addItem(c.name, c.id)

    def _on_type_change(self, value):
        self._current_type = value
        for v, btn in self.type_buttons.items():
            btn.setChecked(v == value)
        self._update_type_button_styles()
        self._load_categories()

    def _update_type_button_styles(self):
        colors = {
            "expense": (COLORS['danger'], COLORS['danger_light']),
            "income": (COLORS['success'], COLORS['success_light']),
        }
        for v, btn in self.type_buttons.items():
            is_active = btn.isChecked()
            accent, bg = colors[v]
            if is_active:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {accent};
                        color: white;
                        border: 2px solid {accent};
                        border-radius: 10px;
                        font-size: 15px;
                        font-weight: 700;
                        font-family: {FONT_FAMILY};
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {COLORS['text_secondary']};
                        border: 2px solid {COLORS['border']};
                        border-radius: 10px;
                        font-size: 15px;
                        font-weight: 600;
                        font-family: {FONT_FAMILY};
                    }}
                    QPushButton:hover {{
                        border-color: {accent};
                        color: {accent};
                    }}
                """)

    def _submit(self):
        amount_str = self.amount_entry.text().strip()
        if not amount_str:
            self.error_label.setText("请输入金额")
            return
        try:
            amount = float(amount_str)
        except ValueError:
            self.error_label.setText("金额格式无效")
            return
        if amount <= 0:
            self.error_label.setText("金额必须大于 0")
            return
        self.error_label.setText("")

        cat_id = self.category_combo.currentData()
        description = self.desc_entry.text().strip()
        bill_date = self.date_edit.date().toPython()

        bill = Bill(
            id=self.bill.id if self.bill else None,
            amount=amount,
            type=self._current_type,
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
        self.amount_entry.setText(str(bill.amount))
        self._on_type_change(bill.type)
        if bill.category_name:
            idx = self.category_combo.findText(bill.category_name)
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)
        self.desc_entry.setText(bill.description or "")
        if bill.bill_date:
            self.date_edit.setDate(QDate(bill.bill_date.year, bill.bill_date.month, bill.bill_date.day))

    def clear(self):
        self.amount_entry.clear()
        self._on_type_change("expense")
        self.desc_entry.clear()
        self.date_edit.setDate(QDate.currentDate())
        self.error_label.setText("")
