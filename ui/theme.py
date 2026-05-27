"""Apple-inspired design system for PySide6 UI."""

# ─── Color Palette (iOS System Colors) ───────────────────────────────────────

COLORS = {
    # Primary accent
    "primary": "#007AFF",
    "primary_hover": "#0062CC",
    "primary_light": "#E8F4FD",
    "primary_ultra_light": "#F0F8FF",

    # Surfaces
    "background": "#F2F2F7",
    "surface": "#FFFFFF",
    "card": "#FFFFFF",
    "elevated": "#FFFFFF",

    # Sidebar (frosted glass)
    "sidebar_bg": "#F5F5FA",
    "sidebar_border": "#E5E5EA",
    "sidebar_hover": "#EBF0FF",
    "sidebar_active": "#E0EAFF",
    "sidebar_text": "#3C3C43",
    "sidebar_text_active": "#007AFF",
    "sidebar_text_hint": "#8E8E93",

    # Semantic status
    "success": "#34C759",
    "success_light": "#E8F9ED",
    "warning": "#FF9500",
    "warning_light": "#FFF4E5",
    "danger": "#FF3B30",
    "danger_light": "#FFECEB",
    "info": "#5AC8FA",
    "info_light": "#E5F9FE",

    # Text hierarchy
    "text_primary": "#1C1C1E",
    "text_secondary": "#636366",
    "text_tertiary": "#AEAEB2",
    "text_hint": "#C7C7CC",
    "text_white": "#FFFFFF",

    # Borders
    "border": "#E5E5EA",
    "border_light": "#F2F2F7",
    "divider": "#D1D1D6",

    # Interactive
    "hover": "#F2F2F7",
    "pressed": "#E5E5EA",
    "table_hover": "#F8F9FA",
    "input_bg": "#F9F9FB",
    "input_border": "#D1D1D6",
    "input_focus": "#007AFF",
}


# ─── Typography ──────────────────────────────────────────────────────────────

FONT_FAMILY = "'MXNLSZ', '851tegakizatsu', 'ZCOOL KuaiLe', 'Segoe UI', 'Microsoft YaHei', sans-serif"

FONT_SIZES = {
    "large_title": 28,
    "title1": 22,
    "title2": 18,
    "title3": 16,
    "headline": 15,
    "body": 14,
    "callout": 13,
    "subhead": 12,
    "footnote": 11,
    "caption": 10,
}


# ─── QSS Stylesheet ─────────────────────────────────────────────────────────

def _base_styles():
    c = COLORS
    return f"""
    QMainWindow {{
        background-color: {c['background']};
    }}
    QWidget#main_content {{
        background: transparent;
    }}
    QWidget#main_content QStackedWidget {{
        background: transparent;
    }}
    QLabel {{
        color: {c['text_primary']};
        font-family: {FONT_FAMILY};
    }}
    """


def _sidebar_styles():
    c = COLORS
    return f"""
    QWidget#sidebar {{
        background-color: {c['sidebar_bg']};
        border-right: 1px solid {c['sidebar_border']};
    }}
    QLabel#sidebar_logo {{
        color: {c['text_primary']};
        font-size: 22px;
        font-weight: 700;
        padding: 4px 0;
        background: transparent;
        font-family: {FONT_FAMILY};
    }}
    QLabel#sidebar_subtitle {{
        color: {c['sidebar_text_hint']};
        font-size: 11px;
        padding: 0 0 2px 0;
        background: transparent;
        font-family: {FONT_FAMILY};
    }}
    QLabel#sidebar_version {{
        color: {c['text_tertiary']};
        font-size: 10px;
        padding: 8px 0;
        background: transparent;
        font-family: {FONT_FAMILY};
    }}
    QPushButton#nav_button {{
        background-color: transparent;
        color: {c['sidebar_text']};
        border: none;
        border-radius: 8px;
        padding: 10px 14px;
        text-align: left;
        font-size: 16px;
        font-weight: 600;
        font-family: {FONT_FAMILY};
    }}
    QPushButton#nav_button:hover {{
        background-color: {c['sidebar_hover']};
        color: {c['sidebar_text_active']};
    }}
    """


def _card_styles():
    c = COLORS
    return f"""
    QFrame[cssClass="card"] {{
        background-color: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 14px;
    }}
    QFrame[cssClass="danger-card"] {{
        background-color: {c['danger_light']};
        border: 1px solid {c['danger']};
        border-radius: 14px;
    }}
    QFrame[cssClass="separator"] {{
        background-color: {c['border']};
        max-height: 1px;
        border: none;
    }}
    """


def _button_styles():
    c = COLORS
    return f"""
    QPushButton[cssClass="primary-btn"] {{
        background-color: {c['primary']};
        color: {c['text_white']};
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
        font-size: 14px;
        font-family: {FONT_FAMILY};
    }}
    QPushButton[cssClass="primary-btn"]:hover {{
        background-color: {c['primary_hover']};
    }}

    QPushButton[cssClass="secondary-btn"] {{
        background-color: {c['primary_light']};
        color: {c['primary']};
        border: none;
        border-radius: 10px;
        padding: 8px 16px;
        font-size: 13px;
        font-family: {FONT_FAMILY};
    }}
    QPushButton[cssClass="secondary-btn"]:hover {{
        background-color: {c['primary']};
        color: {c['text_white']};
    }}

    QPushButton[cssClass="ghost-btn"] {{
        background-color: {c['border_light']};
        color: {c['text_secondary']};
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 13px;
        font-family: {FONT_FAMILY};
    }}
    QPushButton[cssClass="ghost-btn"]:hover {{
        background-color: {c['border']};
        color: {c['text_primary']};
    }}
    QPushButton[cssClass="ghost-btn"]:disabled {{
        color: {c['text_hint']};
        background-color: {c['border_light']};
    }}

    QPushButton[cssClass="danger-btn"] {{
        background-color: {c['danger']};
        color: {c['text_white']};
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
        font-size: 14px;
        font-family: {FONT_FAMILY};
    }}
    QPushButton[cssClass="danger-btn"]:hover {{
        background-color: #E0302A;
    }}

    QPushButton[cssClass="nav-arrow"] {{
        background-color: {c['border_light']};
        border: none;
        border-radius: 8px;
        font-size: 12px;
        padding: 6px 12px;
        font-family: {FONT_FAMILY};
    }}
    QPushButton[cssClass="nav-arrow"]:hover {{
        background-color: {c['border']};
    }}
    QPushButton[cssClass="nav-arrow"]:disabled {{
        color: {c['text_hint']};
    }}

    QPushButton[cssClass="link-btn"] {{
        background-color: transparent;
        border: none;
        font-size: 12px;
        padding: 4px 8px;
        font-family: {FONT_FAMILY};
    }}

    QPushButton[cssClass="period-btn"] {{
        background-color: {c['surface']};
        color: {c['text_secondary']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        font-size: 13px;
        font-family: {FONT_FAMILY};
    }}
    QPushButton[cssClass="period-btn"]:checked {{
        background-color: {c['primary']};
        color: white;
    }}

    QPushButton[cssClass="pill-btn"] {{
        background-color: {c['border_light']};
        color: {c['text_secondary']};
        border: none;
        border-radius: 20px;
        padding: 0 24px;
        font-size: 14px;
        font-family: {FONT_FAMILY};
    }}
    QPushButton[cssClass="pill-btn"]:checked {{
        background-color: {c['primary']};
        color: white;
    }}

    QPushButton[cssClass="export-btn"] {{
        color: white;
        border: none;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
        font-family: {FONT_FAMILY};
    }}
    """


def _input_styles():
    c = COLORS
    return f"""
    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {{
        background-color: {c['surface']};
        border: 1px solid {c['input_border']};
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 14px;
        color: {c['text_primary']};
        font-family: {FONT_FAMILY};
        selection-background-color: {c['primary_light']};
    }}
    QLineEdit:focus, QTextEdit:focus {{
        border-color: {c['primary']};
    }}

    QDateEdit {{
        background-color: {c['surface']};
        border: 1px solid {c['input_border']};
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 14px;
        color: {c['text_primary']};
        font-family: {FONT_FAMILY};
    }}
    QDateEdit:focus {{
        border-color: {c['primary']};
    }}
    QDateEdit::drop-down {{
        border: none;
        padding-right: 8px;
    }}

    QComboBox {{
        background-color: {c['surface']};
        border: 1px solid {c['input_border']};
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 14px;
        color: {c['text_primary']};
        font-family: {FONT_FAMILY};
    }}
    QComboBox:focus {{
        border-color: {c['primary']};
    }}
    QComboBox::drop-down {{
        border: none;
        padding-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 4px;
        selection-background-color: {c['primary_light']};
        selection-color: {c['text_primary']};
        outline: none;
    }}
    QComboBox QAbstractItemView::item {{
        padding: 8px 12px;
        min-height: 28px;
        color: {c['text_primary']};
        background: transparent;
    }}
    QComboBox QAbstractItemView::item:hover {{
        background-color: {c['hover']};
    }}

    QLineEdit[cssClass="underline-input"],
    QDateEdit[cssClass="underline-input"],
    QComboBox[cssClass="underline-input"] {{
        border: none;
        border-bottom: 2px solid {c['input_border']};
        border-radius: 0;
        padding: 8px 4px;
        background-color: {c['surface']};
    }}
    QLineEdit[cssClass="underline-input"]:focus,
    QDateEdit[cssClass="underline-input"]:focus,
    QComboBox[cssClass="underline-input"]:focus {{
        border-bottom-color: {c['primary']};
    }}

    QLabel[cssClass="error-text"] {{
        color: {c['danger']};
        font-size: 13px;
        background: transparent;
    }}
    """


def _table_styles():
    c = COLORS
    return f"""
    QTableWidget {{
        background-color: {c['surface']};
        border: none;
        border-radius: 10px;
        gridline-color: {c['border_light']};
        alternate-background-color: {c['table_hover']};
        font-size: 13px;
        font-family: {FONT_FAMILY};
    }}
    QTableWidget::item {{
        padding: 8px 12px;
        border-bottom: 1px solid {c['border_light']};
    }}
    QTableWidget::item:selected {{
        background-color: {c['primary_light']};
        color: {c['text_primary']};
    }}
    QHeaderView::section {{
        background-color: {c['border_light']};
        border: none;
        border-bottom: 1px solid {c['border']};
        padding: 10px 12px;
        font-weight: 600;
        font-size: 12px;
        color: {c['text_secondary']};
        font-family: {FONT_FAMILY};
    }}
    """


def _scrollbar_styles():
    return """
    QScrollBar:vertical {
        background: transparent;
        width: 8px;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background: rgba(0, 0, 0, 0.15);
        border-radius: 4px;
        min-height: 30px;
    }
    QScrollBar::handle:vertical:hover {
        background: rgba(0, 0, 0, 0.3);
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
    """


def _stat_card_styles():
    c = COLORS
    return f"""
    QWidget[cssClass="stat-card"] {{
        background-color: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 14px;
    }}
    """


def _badge_styles():
    c = COLORS
    return f"""
    QLabel[cssClass="badge"] {{
        color: white;
        border-radius: 10px;
        padding: 3px 10px;
        font-size: 11px;
        font-weight: 600;
        background: transparent;
    }}
    """


def _progress_styles():
    c = COLORS
    return f"""
    QFrame[cssClass="progress-bg"] {{
        background-color: {c['border_light']};
        border-radius: 4px;
    }}
    """


def _misc_styles():
    c = COLORS
    return f"""
    QWidget#page_header {{
        background: transparent;
    }}
    QMessageBox, QDialog, QFileDialog {{
        background-color: {c['surface']};
    }}
    QMessageBox QLabel, QDialog QLabel {{
        background: transparent;
    }}
    """


def _build_stylesheet():
    sections = [
        _base_styles(),
        _sidebar_styles(),
        _card_styles(),
        _button_styles(),
        _input_styles(),
        _table_styles(),
        _scrollbar_styles(),
        _stat_card_styles(),
        _badge_styles(),
        _progress_styles(),
        _misc_styles(),
    ]
    return "\n".join(sections)


STYLESHEET = _build_stylesheet()


# ─── Utility ─────────────────────────────────────────────────────────────────

def set_css_class(widget, class_name: str):
    widget.setProperty("cssClass", class_name)
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def get_income_color():
    return COLORS["success"]


def get_expense_color():
    return COLORS["danger"]


def get_balance_color():
    return COLORS["info"]
