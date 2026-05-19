import customtkinter as ctk
from tkinter import filedialog, messagebox

from utils.export_import import (
    export_csv_dialog, import_csv_dialog,
    export_json_dialog, import_json_dialog,
)


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = ctk.CTkFrame(self)
        container.grid(row=0, column=0, sticky="nsew", padx=25, pady=(25, 20))

        ctk.CTkLabel(container, text="设置",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 25))

        # --- Theme ---
        theme_frame = ctk.CTkFrame(container)
        theme_frame.pack(fill="x", padx=25, pady=(0, 15))

        ctk.CTkLabel(theme_frame, text="外观主题",
                     font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=18, pady=(15, 5))

        ctk.CTkLabel(theme_frame, text="选择暗色/亮色模式，即时生效",
                     font=ctk.CTkFont(size=12), text_color=("gray40", "gray60")).grid(
            row=1, column=0, sticky="w", padx=18, pady=(0, 10))

        self._theme_map = {"暗色模式": "dark", "亮色模式": "light"}
        self.theme_var = ctk.StringVar(
            value="暗色模式" if self.app.config.theme == "dark" else "亮色模式"
        )
        self.theme_seg = ctk.CTkSegmentedButton(
            theme_frame, values=["暗色模式", "亮色模式"],
            variable=self.theme_var,
            command=self._on_theme_change,
        )

        self.theme_seg.grid(row=2, column=0, sticky="w", padx=18, pady=(0, 15))

        # --- Data Path ---
        path_frame = ctk.CTkFrame(container)
        path_frame.pack(fill="x", padx=25, pady=(0, 15))

        ctk.CTkLabel(path_frame, text="数据存储路径",
                     font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=18, pady=(15, 5))

        ctk.CTkLabel(path_frame, text="更改后会自动迁移到新路径",
                     font=ctk.CTkFont(size=12), text_color=("gray40", "gray60")).grid(
            row=1, column=0, sticky="w", padx=18, pady=(0, 8))

        path_row = ctk.CTkFrame(path_frame, fg_color="transparent")
        path_row.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 15))
        path_row.grid_columnconfigure(0, weight=1)

        self.path_entry = ctk.CTkEntry(path_row, height=34)
        self.path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.path_entry.insert(0, self.app.config.data_path)

        browse_btn = ctk.CTkButton(path_row, text="浏览", width=70,
                                   command=self._browse_path)
        browse_btn.grid(row=0, column=1)

        save_path_btn = ctk.CTkButton(path_frame, text="应用新路径", width=130,
                                      command=self._save_path)
        save_path_btn.grid(row=3, column=0, sticky="w", padx=18, pady=(0, 15))

        # --- Import / Export ---
        io_frame = ctk.CTkFrame(container)
        io_frame.pack(fill="x", padx=25, pady=(0, 15))

        ctk.CTkLabel(io_frame, text="导入 & 导出",
                     font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=18, pady=(15, 5))

        btn_row = ctk.CTkFrame(io_frame, fg_color="transparent")
        btn_row.grid(row=1, column=0, sticky="ew", padx=18, pady=(5, 15))

        ctk.CTkButton(btn_row, text="导出 CSV", width=110,
                       command=lambda: export_csv_dialog(self.app)).pack(
            side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text="导入 CSV", width=110,
                       command=lambda: import_csv_dialog(self.app)).pack(
            side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text="导出 JSON 备份", width=130,
                       command=lambda: export_json_dialog(self.app)).pack(
            side="left", padx=(0, 8))
        ctk.CTkButton(btn_row, text="导入 JSON 备份", width=130,
                       command=lambda: import_json_dialog(self.app)).pack(
            side="left", padx=(0, 8))

        # --- Danger zone ---
        danger_frame = ctk.CTkFrame(container)
        danger_frame.pack(fill="x", padx=25, pady=(0, 15))

        ctk.CTkLabel(danger_frame, text="危险操作",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#F44336").grid(
            row=0, column=0, sticky="w", padx=18, pady=(15, 5))

        ctk.CTkLabel(danger_frame, text="清空所有账单数据，此操作不可撤销",
                     font=ctk.CTkFont(size=12), text_color=("gray40", "gray60")).grid(
            row=1, column=0, sticky="w", padx=18, pady=(0, 8))

        clear_btn = ctk.CTkButton(danger_frame, text="清空所有数据", width=130,
                                  fg_color="#C62828", hover_color="#B71C1C",
                                  command=self._clear_all)
        clear_btn.grid(row=2, column=0, sticky="w", padx=18, pady=(0, 15))

    def _on_theme_change(self, value):
        theme = self._theme_map.get(value, "dark")
        ctk.set_appearance_mode(theme)
        self.app.config.theme = theme
        self.app.main_window.refresh_all()

    def _browse_path(self):
        path = filedialog.askdirectory(title="选择数据存储目录")
        if path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path)

    def _save_path(self):
        raw_path = self.path_entry.get().strip()
        if not raw_path:
            return
        import os
        import shutil
        from pathlib import Path

        # normalize to absolute .db file path
        p = Path(raw_path)
        if p.is_dir() or p.suffix != ".db":
            p = p / "bill_data.db"
        new_path = str(p.resolve())

        old_path = self.app.config.data_path
        if new_path == old_path:
            return

        # find the actual source DB (current path may be stale from old buggy versions)
        src_path = old_path
        if not os.path.exists(src_path) or os.path.getsize(src_path) == 0:
            # try default location
            default_db = str(Path(__file__).parent.parent.parent / "bill_data.db")
            if os.path.exists(default_db) and os.path.getsize(default_db) > 0:
                src_path = default_db

        # ensure parent directory exists
        os.makedirs(p.parent, exist_ok=True)

        # copy existing DB to new location
        if os.path.exists(src_path) and os.path.getsize(src_path) > 0:
            try:
                shutil.copy2(src_path, new_path)
            except Exception as e:
                messagebox.showerror("错误", f"复制数据库失败:\n{e}")
                return
        else:
            # no existing data to migrate, new DB will be created
            pass

        # update config and reload
        self.app.config.data_path = new_path
        self.app.reload_database()

        # verify the new DB is accessible
        count = self.app.db.get_bill_count()
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, new_path)
        messagebox.showinfo(
            "成功",
            f"数据路径已更改到:\n{new_path}\n\n当前账单数: {count} 条"
        )

    def _clear_all(self):
        if messagebox.askyesno("确认清空", "确定要清空所有账单数据吗？\n此操作不可撤销！"):
            self.app.db.delete_all_bills()
            messagebox.showinfo("成功", "所有账单数据已清空")
            self.app.main_window.refresh_all()

    def on_show(self):
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, self.app.config.data_path)

    def refresh(self):
        pass
