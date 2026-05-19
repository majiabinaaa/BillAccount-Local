import customtkinter as ctk


class MainWindow(ctk.CTkFrame):
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.app = app

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        from ui.sidebar import Sidebar
        self.sidebar = Sidebar(self, on_navigate=self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 0))
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.pages = {}
        self._current_page = None

        # load pages lazily
        self._page_classes = {}

    def register_page(self, key: str, page_class):
        self._page_classes[key] = page_class

    def show_page(self, key: str):
        if key not in self.pages:
            if key in self._page_classes:
                page = self._page_classes[key](self.content_frame, self.app)
                page.grid(row=0, column=0, sticky="nsew")
                self.pages[key] = page
            else:
                return

        if self._current_page:
            self._current_page.grid_remove()

        self._current_page = self.pages[key]
        self._current_page.grid()
        self._current_page.on_show()

    def refresh_all(self):
        for page in self.pages.values():
            if hasattr(page, 'refresh'):
                page.refresh()
        if self._current_page and hasattr(self._current_page, 'on_show'):
            self._current_page.on_show()
