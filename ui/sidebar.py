import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate, **kwargs):
        super().__init__(master, width=210, corner_radius=0, **kwargs)

        self.on_navigate = on_navigate
        self.active_btn = None
        self.buttons = {}

        # logo
        self.logo_label = ctk.CTkLabel(
            self, text="记账本",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("gray15", "gray90"),
        )
        self.logo_label.pack(pady=(30, 35))

        # Navigation items — all 4-char Chinese labels for visual consistency
        nav_items = [
            ("dashboard", "仪表盘"),
            ("add_bill", "记一笔"),
            ("bill_list", "账单列表"),
            ("summary", "统计分析"),
            ("profile", "消费画像"),
            ("export_page", "导出报告"),
            ("settings", "设置"),
        ]

        for key, label in nav_items:
            btn = ctk.CTkButton(
                self, text=label,
                font=ctk.CTkFont(size=15),
                anchor="center",
                fg_color="transparent",
                text_color=("gray20", "gray85"),
                hover_color=("gray80", "gray30"),
                corner_radius=8,
                height=44,
                width=170,
                command=lambda k=key: self.navigate(k),
            )
            btn.pack(padx=15, pady=4)
            self.buttons[key] = btn

        # spacer
        ctk.CTkLabel(self, text="").pack(fill="both", expand=True)

        # version
        ctk.CTkLabel(
            self, text="v1.1.0",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray45"),
        ).pack(pady=(0, 15))

    def navigate(self, key: str):
        if self.active_btn:
            self.active_btn.configure(fg_color="transparent")
        self.active_btn = self.buttons[key]
        self.active_btn.configure(fg_color=("gray80", "gray30"))
        self.on_navigate(key)
