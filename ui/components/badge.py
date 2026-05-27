"""Reusable badge component."""
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QFont
from ui.theme import set_css_class, FONT_FAMILY


class Badge(QLabel):
    def __init__(self, text, color, parent=None):
        super().__init__(text, parent)
        set_css_class(self, "badge")
        font = QFont()
        font.setFamily(FONT_FAMILY)
        font.setPointSize(10)
        font.setBold(True)
        self.setFont(font)
        self.setStyleSheet(f"background-color: {color}; color: white;")
