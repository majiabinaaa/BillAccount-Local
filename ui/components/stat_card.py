"""Reusable stat card component with Apple-style design."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

from ui.theme import COLORS, set_css_class
from ui.utils import make_label


class StatCard(QWidget):
    def __init__(self, title, color, show_indicator=True, parent=None):
        super().__init__(parent)
        set_css_class(self, "stat-card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 16)
        layout.setSpacing(6)

        top_row = QHBoxLayout()
        top_row.setSpacing(6)

        if show_indicator:
            dot = QLabel()
            dot.setFixedSize(8, 8)
            dot.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
            top_row.addWidget(dot)

        top_row.addWidget(make_label(title, 13, color=COLORS['text_secondary']))
        top_row.addStretch()
        layout.addLayout(top_row)

        self.amount = make_label("¥ 0.00", 24, True)
        layout.addWidget(self.amount)

    def set_value(self, value):
        self.amount.setText(f"¥ {value:,.2f}")

    def set_value_text(self, text):
        self.amount.setText(text)
