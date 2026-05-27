"""Reusable section title component."""
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt

from ui.utils import make_heading


class SectionTitle(QWidget):
    def __init__(self, text, right_widget=None, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addWidget(make_heading(text))

        if right_widget:
            layout.addStretch()
            layout.addWidget(right_widget)
