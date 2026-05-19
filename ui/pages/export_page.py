import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import date


class ExportPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app
        self.db = app.db

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)

        # ---- Header ----
        ctk.CTkLabel(container, text="导出报告",
                     font=ctk.CTkFont(size=26, weight="bold")).pack(
            anchor="w", padx=25, pady=(25, 8))
        ctk.CTkLabel(container, text="生成精美 PDF，记录并分享你的财务故事 ✨",
                     font=ctk.CTkFont(size=13),
                     text_color=("gray40", "gray60")).pack(
            anchor="w", padx=25, pady=(0, 20))

        # ---- Three Preview Cards ----
        cards_data = [
            {
                "title": "📅 本周消费手帐",
                "subtitle": "正方形社交卡片 · 适合发朋友圈",
                "color": "#FF7043",
                "bg": ("#FFF3E0", "#3E2723"),
                "desc": (
                    "暖橙色调 · 支出饼图 · 分类进度条\n"
                    "本周人格标签 · 成就徽章 · 每日格言"
                ),
                "action": self._export_weekly,
                "action_text": "导出本周手帐",
            },
            {
                "title": "📆 月度财务护照",
                "subtitle": "A5 护照尺寸 · 像一本迷你护照",
                "color": "#43A047",
                "bg": ("#E8F5E9", "#1B5E20"),
                "desc": (
                    "清新绿调 · 月度回顾 · 护照封面\n"
                    "月度之最榜单 · 下月预测 · 理财Tips"
                ),
                "action": self._export_monthly,
                "action_text": "导出月度护照",
            },
            {
                "title": "📊 年度财务故事",
                "subtitle": "A4 完整画册 · 年度回忆录",
                "color": "#1E88E5",
                "bg": ("#E3F2FD", "#0D47A1"),
                "desc": (
                    "梦蓝画册 · 12月趋势图 · 年度人格\n"
                    "消费TOP5榜单 · 趣味数据 · 关键词 · 新年寄语"
                ),
                "action": self._export_yearly,
                "action_text": "导出年度故事",
            },
        ]

        for i, card in enumerate(cards_data):
            self._make_card(container, card, i)

    def _make_card(self, parent, card: dict, index: int):
        frame = ctk.CTkFrame(parent, corner_radius=14)
        frame.pack(fill="x", padx=25, pady=(0, 14))

        # color indicator at top
        indicator = ctk.CTkFrame(frame, height=5, fg_color=card["color"],
                                 corner_radius=0)
        indicator.pack(fill="x", padx=1, pady=(1, 0))

        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=(16, 18))

        # left: icon + title
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(left, text=card["title"],
                     font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(left, text=card["subtitle"],
                     font=ctk.CTkFont(size=12),
                     text_color=("gray40", "gray60")).pack(anchor="w", pady=(2, 8))

        # description
        for line in card["desc"].split("\n"):
            ctk.CTkLabel(left, text=line.strip(),
                         font=ctk.CTkFont(size=12),
                         text_color=("gray35", "gray65")).pack(anchor="w")

        # right: button
        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right", padx=(20, 0))

        ctk.CTkButton(
            right, text=card["action_text"],
            font=ctk.CTkFont(size=14, weight="bold"),
            height=42, width=150,
            fg_color=card["color"],
            hover_color=card["color"] + "CC" if False else card["color"],
            command=card["action"],
        ).pack()

    # ==================== Export handlers ====================

    def _export_weekly(self):
        path = filedialog.asksaveasfilename(
            title="导出本周消费手帐",
            defaultextension=".pdf",
            filetypes=[("PDF 文件", "*.pdf")],
            initialfile=f"本周消费手帐_{date.today().isoformat()}.pdf",
        )
        if not path:
            return
        try:
            from core.pdf_exporter import generate_weekly_pdf
            generate_weekly_pdf(self.db, path)
        except Exception as e:
            messagebox.showerror("导出失败", str(e))
            return
        self._ask_open(path)

    def _export_monthly(self):
        path = filedialog.asksaveasfilename(
            title="导出月度财务护照",
            defaultextension=".pdf",
            filetypes=[("PDF 文件", "*.pdf")],
            initialfile=f"月度财务护照_{date.today().strftime('%Y%m')}.pdf",
        )
        if not path:
            return
        try:
            from core.pdf_exporter import generate_monthly_pdf
            generate_monthly_pdf(self.db, path)
        except Exception as e:
            messagebox.showerror("导出失败", str(e))
            return
        self._ask_open(path)

    def _export_yearly(self):
        path = filedialog.asksaveasfilename(
            title="导出年度财务故事",
            defaultextension=".pdf",
            filetypes=[("PDF 文件", "*.pdf")],
            initialfile=f"年度财务故事_{date.today().year}.pdf",
        )
        if not path:
            return
        try:
            from core.pdf_exporter import generate_yearly_pdf
            generate_yearly_pdf(self.db, path)
        except Exception as e:
            messagebox.showerror("导出失败", str(e))
            return
        self._ask_open(path)

    def _ask_open(self, path):
        import os, subprocess, sys
        if messagebox.askyesno("导出成功", f"PDF 已生成!\n{path}\n\n是否打开查看？"):
            try:
                if sys.platform == "win32":
                    os.startfile(path)
                elif sys.platform == "darwin":
                    subprocess.run(["open", path])
                else:
                    subprocess.run(["xdg-open", path])
            except Exception:
                pass

    def on_show(self):
        pass

    def refresh(self):
        pass
