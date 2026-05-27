"""Reusable progress bar component with Apple-style design."""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

from ui.theme import COLORS, set_css_class, FONT_FAMILY
from ui.utils import make_label


class ProgressBar(QWidget):
    def __init__(self, label_text, value=0, maximum=100, color=None, show_value=True, parent=None):
        super().__init__(parent)
        self._color = color or COLORS['primary']
        self._bar_width = 200
        self._show_value = show_value
        self._value = value
        self._maximum = maximum

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)

        self._label = QLabel(label_text)
        self._label.setFont(self._make_label_font())
        self._label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self._label.setFixedWidth(90)
        self._label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._layout.addWidget(self._label)

        self._bar_bg = QFrame()
        self._bar_bg.setFixedHeight(8)
        set_css_class(self._bar_bg, "progress-bg")
        self._bar_fill = QFrame(self._bar_bg)
        self._bar_fill.setFixedHeight(8)
        self._bar_fill.setStyleSheet(
            f"background-color: {self._color}; border-radius: 4px;"
        )
        self._layout.addWidget(self._bar_bg, 1)

        self._value_label = make_label("", 11, color=COLORS['text_tertiary'])
        self._value_label.setFixedWidth(50)
        if show_value:
            self._layout.addWidget(self._value_label)

        self.update(value, maximum)

    def _make_label_font(self):
        from PySide6.QtGui import QFont
        f = QFont()
        f.setFamily(FONT_FAMILY)
        f.setPointSize(11)
        return f

    def set_label_width(self, width):
        self._label.setFixedWidth(width)

    def set_bar_width(self, width):
        self._bar_width = width
        self.update(self._value, self._maximum)

    def update(self, value, maximum):
        self._value = value
        self._maximum = maximum
        pct = value / maximum if maximum > 0 else 0
        self._bar_fill.setFixedWidth(int(self._bar_width * max(pct, 0.02)))
        if self._show_value:
            self._value_label.setText(f"{value}/{maximum}")
