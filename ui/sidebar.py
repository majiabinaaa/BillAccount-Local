"""Sidebar navigation component with frosted glass effect."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QPainter, QPen

from ui.theme import COLORS, set_css_class, FONT_FAMILY


class Sidebar(QWidget):
    navigate_signal = Signal(str)

    NAV_ITEMS = [
        ("dashboard",   "仪表盘"),
        ("add_bill",    "记一笔"),
        ("bill_list",   "账单列表"),
        ("summary",     "统计分析"),
        ("profile",     "消费画像"),
        ("export_page", "导出报告"),
        ("bg_select",   "背景选择"),
        ("settings",    "设置"),
    ]

    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.setObjectName("sidebar")
        self.setFixedWidth(220)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.buttons = {}
        self.active_key = None

        self._setup_ui()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(245, 245, 250, 217))
        painter.setPen(QPen(QColor(229, 229, 234), 1))
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
        painter.end()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 16)
        layout.setSpacing(4)

        # Logo
        logo = QLabel("记账本")
        logo.setObjectName("sidebar_logo")
        logo.setAlignment(Qt.AlignLeft)
        font = QFont()
        font.setFamily(FONT_FAMILY)
        font.setPointSize(22)
        font.setBold(True)
        logo.setFont(font)
        layout.addWidget(logo)

        subtitle = QLabel("Bill Account")
        subtitle.setObjectName("sidebar_subtitle")
        subtitle.setAlignment(Qt.AlignLeft)
        layout.addWidget(subtitle)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        set_css_class(sep, "separator")
        layout.addSpacing(12)
        layout.addWidget(sep)
        layout.addSpacing(8)

        # Navigation items
        for key, label in self.NAV_ITEMS:
            btn = QPushButton(label)
            btn.setObjectName("nav_button")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(38)
            btn.clicked.connect(lambda checked, k=key: self.navigate(k))
            layout.addWidget(btn)
            self.buttons[key] = btn

        # Spacer
        layout.addStretch()

        # Version
        version = QLabel("v2.3 · Provided by 笨拙")
        version.setObjectName("sidebar_version")
        version.setAlignment(Qt.AlignLeft)
        layout.addWidget(version)

    def navigate(self, key: str):
        # Reset previous active button style
        if self.active_key and self.active_key in self.buttons:
            prev = self.buttons[self.active_key]
            prev.setStyleSheet("")

        self.active_key = key
        btn = self.buttons.get(key)
        if btn:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['sidebar_active']};
                    color: {COLORS['sidebar_text_active']};
                    border: none;
                    border-radius: 8px;
                    padding: 10px 14px;
                    text-align: left;
                    font-size: 16px;
                    font-weight: 700;
                    font-family: {FONT_FAMILY};
                }}
            """)

        self.navigate_signal.emit(key)
