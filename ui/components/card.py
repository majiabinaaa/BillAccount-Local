"""Reusable card component with Apple-style shadow."""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from ui.theme import set_css_class


class Card(QFrame):
    def __init__(self, parent=None, padding=(20, 20, 20, 20), spacing=12, danger=False):
        super().__init__(parent)
        set_css_class(self, "danger-card" if danger else "card")

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(*padding)
        self._layout.setSpacing(spacing)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)

    def content_layout(self):
        return self._layout
