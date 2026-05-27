"""Shared UI utility functions."""
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.theme import COLORS, FONT_FAMILY


def _make_font(size=None, bold=False):
    font = QFont()
    font.setFamily(FONT_FAMILY)
    if size is not None:
        font.setPointSize(size)
    font.setBold(bold)
    return font


def make_label(text, size=14, bold=False, color=None):
    label = QLabel(text)
    label.setFont(_make_font(size, bold))
    if color:
        label.setStyleSheet(f"color: {color};")
    return label


def make_title(text, size=28):
    return make_label(text, size, bold=True)


def make_subtitle(text):
    return make_label(text, 13, color=COLORS['text_tertiary'])


def make_heading(text, size=18):
    return make_label(text, size, bold=True)


def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()
        elif item.layout():
            clear_layout(item.layout())


def make_separator():
    sep = QFrame()
    sep.setFrameShape(QFrame.HLine)
    sep.setStyleSheet(f"background-color: {COLORS['border']}; max-height: 1px;")
    return sep
