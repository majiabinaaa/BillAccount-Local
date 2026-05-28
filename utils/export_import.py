"""File-dialog-based export/import helpers for use in the UI."""

from PySide6.QtWidgets import QFileDialog
from ui.dialogs import show_info, show_error, show_warning


def export_csv_dialog(app):
    filepath, _ = QFileDialog.getSaveFileName(
        None, "导出 CSV", "账单数据.csv", "CSV 文件 (*.csv)"
    )
    if not filepath:
        return
    try:
        app.db.export_to_csv(filepath)
        show_info(None, "导出成功", f"数据已导出到:\n{filepath}")
    except Exception as e:
        show_error(None, "导出失败", str(e))


def import_csv_dialog(app):
    filepath, _ = QFileDialog.getOpenFileName(
        None, "导入 CSV", "", "CSV 文件 (*.csv)"
    )
    if not filepath:
        return
    try:
        count, errors = app.db.import_from_csv(filepath)
        if errors:
            detail = "\n".join(errors[:10])
            if len(errors) > 10:
                detail += f"\n... 共 {len(errors)} 条错误"
            show_warning(
                None, "导入完成",
                f"成功导入 {count} 条记录，{len(errors)} 条跳过:\n{detail}",
            )
        else:
            show_info(None, "导入成功", f"成功导入 {count} 条账单记录")
        app.main_window.refresh_all()
    except Exception as e:
        show_error(None, "导入失败", str(e))


def export_json_dialog(app):
    filepath, _ = QFileDialog.getSaveFileName(
        None, "导出 JSON (完整备份)", "账单备份.json", "JSON 文件 (*.json)"
    )
    if not filepath:
        return
    try:
        app.db.export_to_json(filepath)
        show_info(None, "导出成功", f"完整数据已备份到:\n{filepath}")
    except Exception as e:
        show_error(None, "导出失败", str(e))


def import_json_dialog(app):
    filepath, _ = QFileDialog.getOpenFileName(
        None, "导入 JSON 备份", "", "JSON 文件 (*.json)"
    )
    if not filepath:
        return
    try:
        count = app.db.import_from_json(filepath)
        show_info(None, "导入成功", f"成功导入 {count} 条账单记录")
        app.main_window.refresh_all()
    except Exception as e:
        show_error(None, "导入失败", str(e))
