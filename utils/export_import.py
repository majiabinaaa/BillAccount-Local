"""File-dialog-based export/import helpers for use in the UI."""

from tkinter import filedialog, messagebox


def export_csv_dialog(app):
    filepath = filedialog.asksaveasfilename(
        parent=app,
        title="导出 CSV",
        defaultextension=".csv",
        filetypes=[("CSV 文件", "*.csv")],
        initialfile="账单数据.csv",
    )
    if not filepath:
        return
    try:
        app.db.export_to_csv(filepath)
        messagebox.showinfo("导出成功", f"数据已导出到:\n{filepath}")
    except Exception as e:
        messagebox.showerror("导出失败", str(e))


def import_csv_dialog(app):
    filepath = filedialog.askopenfilename(
        parent=app,
        title="导入 CSV",
        filetypes=[("CSV 文件", "*.csv")],
    )
    if not filepath:
        return
    try:
        count = app.db.import_from_csv(filepath)
        messagebox.showinfo("导入成功", f"成功导入 {count} 条账单记录")
        app.main_window.refresh_all()
    except Exception as e:
        messagebox.showerror("导入失败", str(e))


def export_json_dialog(app):
    filepath = filedialog.asksaveasfilename(
        parent=app,
        title="导出 JSON (完整备份)",
        defaultextension=".json",
        filetypes=[("JSON 文件", "*.json")],
        initialfile="账单备份.json",
    )
    if not filepath:
        return
    try:
        app.db.export_to_json(filepath)
        messagebox.showinfo("导出成功", f"完整数据已备份到:\n{filepath}")
    except Exception as e:
        messagebox.showerror("导出失败", str(e))


def import_json_dialog(app):
    filepath = filedialog.askopenfilename(
        parent=app,
        title="导入 JSON 备份",
        filetypes=[("JSON 文件", "*.json")],
    )
    if not filepath:
        return
    try:
        count = app.db.import_from_json(filepath)
        messagebox.showinfo("导入成功", f"成功导入 {count} 条账单记录")
        app.main_window.refresh_all()
    except Exception as e:
        messagebox.showerror("导入失败", str(e))
