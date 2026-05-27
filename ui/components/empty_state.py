"""Reusable empty state placeholder component."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.theme import COLORS, FONT_FAMILY
from ui.utils import make_label


class EmptyState(QWidget):
    def __init__(self, icon="📭", title="暂无数据", subtitle="", parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 40, 0, 40)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)

        icon_label = QLabel(icon)
        icon_font = QFont()
        icon_font.setPointSize(36)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        title_label = make_label(title, 16, bold=True, color=COLORS['text_secondary'])
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        if subtitle:
            sub_label = make_label(subtitle, 13, color=COLORS['text_tertiary'])
            sub_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(sub_label)
