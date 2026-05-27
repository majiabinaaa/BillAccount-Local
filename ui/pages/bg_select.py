"""Background selection page."""
import os
from pathlib import Path

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QFrame, QScrollArea, QGridLayout, QPushButton)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

from ui.theme import COLORS, FONT_FAMILY
from ui.utils import make_title, make_heading

_ASSETS = Path(__file__).resolve().parent.parent.parent / "assets" / "background"


def _scan_themes():
    """Scan background assets and return structured theme data."""
    themes = []
    if not _ASSETS.is_dir():
        return themes
    for theme_dir in sorted(_ASSETS.iterdir()):
        if not theme_dir.is_dir():
            continue
        characters = []
        for char_dir in sorted(theme_dir.iterdir()):
            if not char_dir.is_dir():
                continue
            images = []
            for f in sorted(char_dir.iterdir()):
                if f.suffix.lower() in (".jpg", ".jpeg", ".png"):
                    images.append(f)
            if images:
                characters.append({"name": char_dir.name, "images": images})
        if characters:
            themes.append({"name": theme_dir.name, "characters": characters})
    return themes


class _ImageCard(QFrame):
    """Clickable image thumbnail card."""
    clicked = Signal(str)

    def __init__(self, image_path: str, label: str, is_active=False, parent=None):
        super().__init__(parent)
        self._path = image_path
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(180, 130)
        self._apply_style(is_active)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 4)
        layout.setSpacing(4)

        self._img = QLabel()
        self._img.setFixedHeight(88)
        self._img.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(str(image_path))
        if not pixmap.isNull():
            scaled = pixmap.scaled(160, 88, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._img.setPixmap(scaled)
        layout.addWidget(self._img)

        self._name = QLabel(label)
        self._name.setAlignment(Qt.AlignCenter)
        self._name.setStyleSheet(
            f"color: {COLORS['text_primary']}; font-size: 11px; "
            "background: transparent; border: none;"
        )
        layout.addWidget(self._name)

    def _apply_style(self, active):
        border = "#007AFF" if active else "#E5E5EA"
        self.setStyleSheet(
            f"QFrame {{ background-color: white; border: 2px solid {border}; border-radius: 10px; }}"
            f"QFrame:hover {{ border-color: #007AFF; }}"
        )

    def set_active(self, active):
        self._apply_style(active)

    def mousePressEvent(self, event):
        self.clicked.emit(self._path)


class BgSelectPage(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self._cards = []  # list of (path_str, card)
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(20)

        layout.addWidget(make_title("背景选择"))

        hint = QLabel("选择一张喜欢的图片作为应用背景，不透明度 35%")
        hint.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        layout.addWidget(hint)

        self._current_bg = self.app.config.get("background_path", "")

        themes = _scan_themes()
        for theme in themes:
            # Theme heading
            layout.addWidget(make_heading(theme["name"]))

            for char in theme["characters"]:
                # Character sub-heading
                char_label = QLabel(f"  {char['name']}")
                char_label.setStyleSheet(
                    f"color: {COLORS['text_secondary']}; font-size: 13px; "
                    f"font-family: {FONT_FAMILY};"
                )
                layout.addWidget(char_label)

                grid = QGridLayout()
                grid.setSpacing(10)
                for i, img_path in enumerate(char["images"]):
                    path_str = str(img_path)
                    card = _ImageCard(path_str, img_path.stem, is_active=(path_str == self._current_bg))
                    card.clicked.connect(self._on_select)
                    grid.addWidget(card, i // 4, i % 4)
                    self._cards.append((path_str, card))
                layout.addLayout(grid)

        # Reset button
        reset_row = QHBoxLayout()
        reset_row.addStretch()
        reset_btn = QPushButton("恢复默认背景")
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['border_light']};
                color: {COLORS['text_secondary']};
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px;
                font-family: {FONT_FAMILY};
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
            }}
        """)
        reset_btn.clicked.connect(self._on_reset)
        reset_row.addWidget(reset_btn)
        layout.addLayout(reset_row)

        layout.addStretch()

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _on_select(self, path: str):
        self.app.config.set("background_path", path)
        self._current_bg = path
        self._refresh_cards()
        self.app.main_window.set_background(path)

    def _on_reset(self):
        self.app.config.set("background_path", "")
        self._current_bg = ""
        self._refresh_cards()
        self.app.main_window.set_background("")

    def _refresh_cards(self):
        for path_str, card in self._cards:
            card.set_active(path_str == self._current_bg)
