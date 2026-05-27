"""
打包安装器 — 运行此脚本后显示可视化界面，选择安装路径并一键打包安装。
"""
import sys
import os
import subprocess
import shutil
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

PROJECT_DIR = Path(__file__).parent.resolve()
APP_NAME = "BillAccount"
MAIN_SCRIPT = PROJECT_DIR / "main.py"


def get_pyinstaller_cmd(dist_dir: str) -> list:
    assets_src = str(PROJECT_DIR / "assets")
    if sys.platform == "win32":
        assets_arg = f"{assets_src};assets"
    else:
        assets_arg = f"{assets_src}:assets"

    return [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", APP_NAME,
        "--distpath", dist_dir,
        "--workpath", str(Path(dist_dir) / "build_temp"),
        "--specpath", str(Path(dist_dir) / "build_temp"),
        "--add-data", assets_arg,
        "--collect-all", "ui",
        "--collect-all", "core",
        "--collect-all", "utils",
        "--hidden-import", "PySide6",
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtGui",
        "--hidden-import", "numpy",
        "--hidden-import", "PIL",
        "--hidden-import", "ui.components.styled_combo",
        "--hidden-import", "matplotlib",
        "--hidden-import", "matplotlib.backends.backend_qtagg",
        str(MAIN_SCRIPT),
    ]


class BuildInstaller(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("记账本 - 安装打包工具")
        self.geometry("560x500")
        self.resizable(False, False)
        self._center()

        self.build()

    def _center(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w = self.winfo_width()
        h = self.winfo_height()
        self.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

    def build(self):
        # Title
        ctk.CTkLabel(
            self, text="记账本 安装打包工具",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(pady=(30, 25))

        # --- Install path ---
        path_frame = ctk.CTkFrame(self)
        path_frame.pack(fill="x", padx=35, pady=(0, 10))

        ctk.CTkLabel(
            path_frame, text="选择安装目录",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(14, 4))

        ctk.CTkLabel(
            path_frame,
            text="打包后的 .exe 文件将被复制到此目录下",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60"),
        ).pack(anchor="w", padx=16, pady=(0, 8))

        path_row = ctk.CTkFrame(path_frame, fg_color="transparent")
        path_row.pack(fill="x", padx=16, pady=(0, 14))
        path_row.grid_columnconfigure(0, weight=1)

        default_path = str(Path.home() / "Desktop" / APP_NAME)
        self.path_var = ctk.StringVar(value=default_path)
        self.path_entry = ctk.CTkEntry(path_row, textvariable=self.path_var, height=34)
        self.path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkButton(path_row, text="浏览", width=70,
                      command=self._browse).grid(row=0, column=1)

        # --- Options ---
        opt_frame = ctk.CTkFrame(self)
        opt_frame.pack(fill="x", padx=35, pady=(0, 10))

        ctk.CTkLabel(
            opt_frame, text="打包选项",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(14, 4))

        self.create_shortcut_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            opt_frame, text="在桌面创建快捷方式",
            variable=self.create_shortcut_var,
            font=ctk.CTkFont(size=13),
        ).pack(anchor="w", padx=16, pady=(4, 14))

        # --- Build button ---
        self.build_btn = ctk.CTkButton(
            self, text="开始打包安装",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=48,
            command=self._start_build,
        )
        self.build_btn.pack(fill="x", padx=35, pady=(5, 8))

        # --- Progress ---
        self.progress_text = ctk.CTkTextbox(self, height=150, font=ctk.CTkFont(size=11))
        self.progress_text.pack(fill="both", expand=True, padx=35, pady=(5, 20))
        self.progress_text.insert("end", "准备就绪，请点击上方按钮开始打包。\n")
        self.progress_text.configure(state="disabled")

    def _browse(self):
        path = filedialog.askdirectory(title="选择安装目录")
        if path:
            self.path_var.set(path)

    def _log(self, msg: str):
        self.progress_text.configure(state="normal")
        self.progress_text.insert("end", msg + "\n")
        self.progress_text.see("end")
        self.progress_text.configure(state="disabled")

    def _start_build(self):
        install_dir = self.path_var.get().strip()
        if not install_dir:
            messagebox.showerror("错误", "请先选择安装目录")
            return

        self.build_btn.configure(state="disabled", text="正在打包中...")
        self.progress_text.configure(state="normal")
        self.progress_text.delete("1.0", "end")
        self.progress_text.configure(state="disabled")
        thread = threading.Thread(target=self._run_build, args=(install_dir,), daemon=True)
        thread.start()

    def _run_build(self, install_dir: str):
        os.makedirs(install_dir, exist_ok=True)

        self._log(f"目标目录: {install_dir}")
        self._log("开始打包... (这可能需要几分钟)")

        dist_dir = str(PROJECT_DIR / "dist_build")
        cmd = get_pyinstaller_cmd(dist_dir)
        self._log(f"命令: {' '.join(cmd)}")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(PROJECT_DIR),
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            for line in process.stdout:
                line = line.strip()
                if line:
                    self.after(0, self._log, line)

            process.wait()

            if process.returncode != 0:
                self.after(0, self._on_build_error, "PyInstaller 打包失败，请检查上方日志")
                return

            # locate built exe
            built_exe = Path(dist_dir) / f"{APP_NAME}.exe"
            if not built_exe.exists():
                self.after(0, self._on_build_error, f"未找到生成的文件: {built_exe}")
                return

            # copy to install dir
            target_exe = Path(install_dir) / f"{APP_NAME}.exe"
            shutil.copy2(str(built_exe), str(target_exe))
            self._log(f"已复制到: {target_exe}")

            # create desktop shortcut
            if self.create_shortcut_var.get():
                self._create_shortcut(str(target_exe))

            # clean up build artifacts
            try:
                shutil.rmtree(dist_dir, ignore_errors=True)
            except Exception:
                pass

            self.after(0, self._on_build_success, str(target_exe))

        except Exception as e:
            self.after(0, self._on_build_error, str(e))

    def _create_shortcut(self, exe_path: str):
        try:
            import pythoncom
            import win32com.client

            pythoncom.CoInitialize()
            shell = win32com.client.Dispatch("WScript.Shell")
            desktop = shell.SpecialFolders("Desktop")
            shortcut_path = str(Path(desktop) / f"{APP_NAME}.lnk")

            shortcut = shell.CreateShortcut(shortcut_path)
            shortcut.TargetPath = exe_path
            shortcut.WorkingDirectory = str(Path(exe_path).parent)
            shortcut.Description = "记账本 - 个人财务管理"
            shortcut.Save()

            self._log(f"桌面快捷方式已创建: {shortcut_path}")
        except ImportError:
            self._log("(跳过快捷方式创建 — 需要 pywin32 模块)")
        except Exception as e:
            self._log(f"快捷方式创建失败: {e}")

    def _on_build_error(self, msg: str):
        self.build_btn.configure(state="normal", text="开始打包安装")
        self._log(f"错误: {msg}")
        messagebox.showerror("打包失败", msg)

    def _on_build_success(self, exe_path: str):
        self.build_btn.configure(state="normal", text="开始打包安装")
        self._log("打包完成!")
        messagebox.showinfo(
            "打包成功",
            f"安装完成!\n\n"
            f"程序位置: {exe_path}\n\n"
            f"直接运行 .exe 即可使用。",
        )


if __name__ == "__main__":
    app = BuildInstaller()
    app.mainloop()
