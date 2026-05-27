"""Main application window using PySide6 with Apple-style design."""
import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QFontDatabase, QIcon

from core.config_manager import ConfigManager
from core.database import Database
from ui.theme import STYLESHEET, FONT_FAMILY
from ui.sidebar import Sidebar
from ui.main_window import MainWindow


def _load_custom_fonts():
    """Load custom fonts from the assets/fonts directory."""
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "fonts")
    if not os.path.isdir(assets_dir):
        return
    for fname in os.listdir(assets_dir):
        if fname.lower().endswith((".ttf", ".otf")):
            fpath = os.path.join(assets_dir, fname)
            QFontDatabase.addApplicationFont(fpath)


class App(QMainWindow):
    def __init__(self):
        super().__init__()

        _load_custom_fonts()

        self.config = ConfigManager()
        self.db = Database(self.config.data_path)

        # Apply system font globally
        font = QFont()
        font.setFamily(FONT_FAMILY)
        font.setPointSize(14)
        QApplication.instance().setFont(font)

        # Window setup
        self.setWindowTitle("记账本")
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "appearance.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setMinimumSize(1000, 650)

        # Restore window size
        win_w = self.config.get("window_width", 1100)
        win_h = self.config.get("window_height", 720)
        self.resize(win_w, win_h)

        # Center on screen
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - win_w) // 2
        y = (screen.height() - win_h) // 2
        self.move(x, y)

        # Apply stylesheet
        self.setStyleSheet(STYLESHEET)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create sidebar
        self.sidebar = Sidebar(self)
        layout.addWidget(self.sidebar)

        # Create main content area
        self.main_window = MainWindow(self)
        layout.addWidget(self.main_window)

        # Connect sidebar navigation to main window
        self.sidebar.navigate_signal.connect(self.main_window.show_page)

        # Register pages
        self._register_pages()

        # Show dashboard by default
        self.sidebar.navigate("dashboard")

        # Restore saved background
        saved_bg = self.config.get("background_path", "")
        if saved_bg:
            from ui.pages.bg_select import _resolve_bg_path
            resolved = _resolve_bg_path(saved_bg)
            if resolved:
                self.main_window.set_background(resolved)

    def _register_pages(self):
        from ui.pages.dashboard import DashboardPage
        from ui.pages.add_bill import AddBillPage
        from ui.pages.bill_list import BillListPage
        from ui.pages.summary import SummaryPage
        from ui.pages.profile import ProfilePage
        from ui.pages.export_page import ExportPage
        from ui.pages.settings import SettingsPage

        self.main_window.register_page("dashboard", DashboardPage)
        self.main_window.register_page("add_bill", AddBillPage)
        self.main_window.register_page("bill_list", BillListPage)
        self.main_window.register_page("summary", SummaryPage)
        self.main_window.register_page("profile", ProfilePage)
        self.main_window.register_page("export_page", ExportPage)
        self.main_window.register_page("settings", SettingsPage)

        from ui.pages.bg_select import BgSelectPage
        self.main_window.register_page("bg_select", BgSelectPage)

    def reload_database(self):
        self.db = Database(self.config.data_path)
        self.main_window.refresh_all()

    def closeEvent(self, event):
        self.config.set("window_width", self.width())
        self.config.set("window_height", self.height())
        event.accept()
