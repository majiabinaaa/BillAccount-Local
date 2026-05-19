import customtkinter as ctk

from core.config_manager import ConfigManager
from core.database import Database
from ui.main_window import MainWindow


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.config = ConfigManager()
        self.db = Database(self.config.data_path)

        ctk.set_appearance_mode(self.config.theme)
        ctk.set_default_color_theme("blue")

        self.title("记账本")

        # clamp window size to screen
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        max_w = int(sw * 0.88)
        max_h = int(sh * 0.85)
        win_w = min(self.config.get("window_width", 1050), max_w)
        win_h = min(self.config.get("window_height", 700), max_h)
        self.geometry(f"{win_w}x{win_h}")
        self.minsize(900, 600)

        # center on screen
        x = (sw - win_w) // 2
        y = (sh - win_h) // 2
        self.geometry(f"+{x}+{y}")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.main_window = MainWindow(self)
        self.main_window.pack(fill="both", expand=True)

        self._register_pages()
        self.main_window.show_page("dashboard")

    def _register_pages(self):
        from ui.pages.dashboard import DashboardPage
        from ui.pages.add_bill import AddBillPage
        from ui.pages.bill_list import BillListPage
        from ui.pages.summary import SummaryPage
        from ui.pages.settings import SettingsPage

        self.main_window.register_page("dashboard", DashboardPage)
        self.main_window.register_page("add_bill", AddBillPage)
        self.main_window.register_page("bill_list", BillListPage)
        self.main_window.register_page("summary", SummaryPage)
        self.main_window.register_page("settings", SettingsPage)

    def reload_database(self):
        self.db = Database(self.config.data_path)
        self.main_window.refresh_all()

    def _on_close(self):
        self.config.set("window_width", self.winfo_width())
        self.config.set("window_height", self.winfo_height())
        self.destroy()
