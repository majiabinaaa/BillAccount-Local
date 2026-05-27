"""Custom QComboBox with opaque popup styling."""
from PySide6.QtWidgets import QComboBox, QAbstractItemView, QFrame
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QFont

from ui.theme import COLORS, FONT_FAMILY


class StyledComboBox(QComboBox):
    """QComboBox that forces opaque white background on its dropdown popup."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._popup_style = self._build_popup_style()
        self.view().setStyleSheet(self._popup_style)

    def _build_popup_style(self):
        c = COLORS
        return f"""
            QAbstractItemView {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 4px;
                selection-background-color: {c['primary_light']};
                selection-color: {c['text_primary']};
                outline: none;
                font-family: {FONT_FAMILY};
                font-size: 14px;
            }}
            QAbstractItemView::item {{
                padding: 8px 12px;
                min-height: 28px;
                color: {c['text_primary']};
                background-color: {c['surface']};
            }}
            QAbstractItemView::item:hover {{
                background-color: {c['hover']};
            }}
        """

    def showPopup(self):
        super().showPopup()
        popup = self.findChild(QFrame)
        if popup:
            popup.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['surface']};
                    border: 1px solid {COLORS['border']};
                }}
            """)
        self.view().setStyleSheet(self._popup_style)
