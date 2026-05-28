"""Custom styled dialogs to replace native QMessageBox."""
from PySide6.QtWidgets import (QMessageBox, QDialog, QVBoxLayout, QLabel,
                               QHBoxLayout, QPushButton, QWidget)
from PySide6.QtCore import Qt
from ui.theme import COLORS, FONT_FAMILY


def _get_dialog_stylesheet():
    """Return stylesheet for custom dialogs."""
    c = COLORS
    return f"""
    QMessageBox {{
        background-color: {c['surface']};
    }}
    QMessageBox QLabel {{
        color: {c['text_primary']};
        background: transparent;
        font-size: 14px;
        font-family: {FONT_FAMILY};
    }}
    QMessageBox QPushButton {{
        background-color: {c['primary']};
        color: {c['text_white']};
        border: none;
        border-radius: 8px;
        padding: 8px 24px;
        font-size: 13px;
        font-weight: 600;
        font-family: {FONT_FAMILY};
        min-width: 80px;
    }}
    QMessageBox QPushButton:hover {{
        background-color: {c['primary_hover']};
    }}
    QMessageBox QPushButton:pressed {{
        background-color: #004999;
    }}
    """


def show_info(parent, title, message):
    """Show an information message box."""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStyleSheet(_get_dialog_stylesheet())
    return msg.exec()


def show_warning(parent, title, message):
    """Show a warning message box."""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStyleSheet(_get_dialog_stylesheet())
    return msg.exec()


def show_error(parent, title, message):
    """Show a critical/error message box."""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStyleSheet(_get_dialog_stylesheet())
    return msg.exec()


def show_question(parent, title, message, default_button=QMessageBox.No):
    """Show a question message box with Yes/No buttons."""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.setDefaultButton(default_button)
    msg.setStyleSheet(_get_dialog_stylesheet())
    return msg.exec()


def show_question_yes_default(parent, title, message):
    """Show a question message box with Yes/No buttons, default Yes."""
    return show_question(parent, title, message, QMessageBox.Yes)


def show_information(parent, title, message):
    """Alias for show_info for backward compatibility."""
    return show_info(parent, title, message)


def show_critical(parent, title, message):
    """Alias for show_error for backward compatibility."""
    return show_error(parent, title, message)
