"""Main content area with page switching."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QColor, QImage


class MainWindow(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app

        self.setObjectName("main_content")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Background layer
        self._bg_label = QLabel(self)
        self._bg_label.setScaledContents(False)
        self._bg_label.lower()

        # Frosted glass overlay (semi-transparent white between bg and content)
        self._overlay = QLabel(self)
        self._overlay.setStyleSheet("background-color: rgba(255, 255, 255, 180);")
        self._overlay.setScaledContents(True)
        self._overlay.lower()

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        layout.addWidget(self.stack)

        self.pages = {}
        self._page_classes = {}
        self._current_page = None
        self._bg_pixmap = None

    def set_background(self, path: str):
        if not path or not __import__("os").path.exists(path):
            self._bg_pixmap = None
            self._bg_label.clear()
            self._bg_label.setStyleSheet("background: transparent;")
            self._overlay.setVisible(False)
            return
        self._bg_pixmap = QPixmap(path)
        self._overlay.setVisible(True)
        self._apply_background()

    def _apply_background(self):
        if self._bg_pixmap is None or self._bg_pixmap.isNull():
            self._bg_label.clear()
            self._bg_label.setStyleSheet("background: transparent;")
            self._overlay.setVisible(False)
            return
        # Scale to fill window, maintain aspect ratio
        scaled = self._bg_pixmap.scaled(
            self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
        )
        # Apply 35% opacity
        result = QImage(scaled.size(), QImage.Format_ARGB32)
        result.fill(Qt.transparent)
        painter = QPainter(result)
        painter.setOpacity(0.35)
        painter.drawPixmap(0, 0, scaled)
        painter.end()
        self._bg_label.setPixmap(QPixmap.fromImage(result))
        self._bg_label.resize(self.size())
        self._bg_label.setAlignment(Qt.AlignCenter)
        self._overlay.resize(self.size())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_background()

    def register_page(self, key: str, page_class):
        self._page_classes[key] = page_class

    def show_page(self, key: str):
        if key not in self.pages:
            if key in self._page_classes:
                page = self._page_classes[key](self.app, self)
                self.pages[key] = page
                self.stack.addWidget(page)
            else:
                return

        if self._current_page and hasattr(self._current_page, 'on_hide'):
            self._current_page.on_hide()

        self._current_page = self.pages[key]
        self.stack.setCurrentWidget(self._current_page)

        if hasattr(self._current_page, 'on_show'):
            self._current_page.on_show()

    def refresh_all(self):
        for page in self.pages.values():
            if hasattr(page, 'refresh'):
                page.refresh()
        if self._current_page and hasattr(self._current_page, 'on_show'):
            self._current_page.on_show()
