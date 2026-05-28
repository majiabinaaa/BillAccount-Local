"""Settings page - grouped settings sections."""
import os
import shutil
from pathlib import Path

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame, QLineEdit, QFileDialog,
                               QScrollArea, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.theme import COLORS, set_css_class, FONT_FAMILY
from ui.utils import make_label, make_title, make_heading, make_subtitle
from ui.components.card import Card
from utils.export_import import (
    export_csv_dialog, import_csv_dialog,
    export_json_dialog, import_json_dialog,
)
from ui.dialogs import show_info, show_error, show_question


class SettingsPage(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(24)

        # Header
        layout.addWidget(make_title("设置"))

        # Theme card
        theme_card = Card(padding=(20, 20, 20, 20), spacing=8)
        t_layout = theme_card.content_layout()
        t_layout.addWidget(make_heading("外观主题"))
        t_layout.addWidget(make_subtitle("当前使用浅色主题"))
        layout.addWidget(theme_card)

        # Data Path card
        path_card = Card(padding=(20, 20, 20, 20), spacing=10)
        p_layout = path_card.content_layout()
        p_layout.addWidget(make_heading("数据存储路径"))
        p_layout.addWidget(make_subtitle("更改后会自动迁移到新路径"))

        path_row = QHBoxLayout()
        path_row.setSpacing(8)

        self.path_entry = QLineEdit()
        self.path_entry.setText(self.app.config.data_path)
        self.path_entry.setFixedHeight(36)
        path_row.addWidget(self.path_entry)

        browse_btn = QPushButton("浏览")
        browse_btn.setFixedSize(70, 36)
        browse_btn.setCursor(Qt.PointingHandCursor)
        browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['primary']};
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-family: {FONT_FAMILY};
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_white']};
            }}
        """)
        browse_btn.clicked.connect(self._browse_path)
        path_row.addWidget(browse_btn)

        p_layout.addLayout(path_row)

        save_path_btn = QPushButton("应用新路径")
        save_path_btn.setFixedSize(130, 36)
        save_path_btn.setCursor(Qt.PointingHandCursor)
        save_path_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_white']};
                border: none;
                border-radius: 10px;
                font-weight: 600;
                font-size: 14px;
                font-family: {FONT_FAMILY};
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
        """)
        save_path_btn.clicked.connect(self._save_path)
        p_layout.addWidget(save_path_btn)

        layout.addWidget(path_card)

        # Import/Export card
        io_card = Card(padding=(20, 20, 20, 20), spacing=10)
        io_layout = io_card.content_layout()
        io_layout.addWidget(make_heading("导入 & 导出"))

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        for text, handler in [
            ("导出 CSV", lambda: export_csv_dialog(self.app)),
            ("导入 CSV", lambda: import_csv_dialog(self.app)),
            ("导出 JSON 备份", lambda: export_json_dialog(self.app)),
            ("导入 JSON 备份", lambda: import_json_dialog(self.app)),
        ]:
            btn = QPushButton(text)
            btn.setFixedHeight(36)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['primary_light']};
                    color: {COLORS['primary']};
                    border: none;
                    border-radius: 10px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-family: {FONT_FAMILY};
                }}
                QPushButton:hover {{
                    background-color: {COLORS['primary']};
                    color: {COLORS['text_white']};
                }}
            """)
            btn.clicked.connect(handler)
            btn_row.addWidget(btn)

        btn_row.addStretch()
        io_layout.addLayout(btn_row)
        layout.addWidget(io_card)

        # Danger zone
        danger_card = Card(danger=True, spacing=8)
        d_layout = danger_card.content_layout()

        danger_title = QLabel("危险操作")
        danger_title.setStyleSheet(f"color: {COLORS['danger']}; font-size: 15px; font-weight: bold; font-family: {FONT_FAMILY};")
        d_layout.addWidget(danger_title)

        d_layout.addWidget(make_subtitle("清空所有账单数据，此操作不可撤销"))

        clear_btn = QPushButton("清空所有数据")
        clear_btn.setFixedSize(130, 36)
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger']};
                color: {COLORS['text_white']};
                border: none;
                border-radius: 10px;
                font-weight: 600;
                font-size: 14px;
                font-family: {FONT_FAMILY};
            }}
            QPushButton:hover {{
                background-color: #E0302A;
            }}
        """)
        clear_btn.clicked.connect(self._clear_all)
        d_layout.addWidget(clear_btn)

        layout.addWidget(danger_card)
        layout.addStretch()

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择数据存储目录")
        if path:
            self.path_entry.setText(path)

    def _save_path(self):
        raw_path = self.path_entry.text().strip()
        if not raw_path:
            return

        p = Path(raw_path)
        if p.is_dir() or p.suffix != ".db":
            p = p / "bill_data.db"
        new_path = str(p.resolve())

        old_path = self.app.config.data_path
        if new_path == old_path:
            return

        src_path = old_path
        if not os.path.exists(src_path) or os.path.getsize(src_path) == 0:
            default_db = str(Path(__file__).parent.parent.parent / "bill_data.db")
            if os.path.exists(default_db) and os.path.getsize(default_db) > 0:
                src_path = default_db

        os.makedirs(p.parent, exist_ok=True)

        if os.path.exists(src_path) and os.path.getsize(src_path) > 0:
            try:
                shutil.copy2(src_path, new_path)
            except Exception as e:
                show_error(self, "错误", f"复制数据库失败:\n{e}")
                return

        self.app.config.data_path = new_path
        self.app.reload_database()

        count = self.app.db.get_bill_count()
        self.path_entry.setText(new_path)
        show_info(self, "成功", f"数据路径已更改到:\n{new_path}\n\n当前账单数: {count} 条")

    def _clear_all(self):
        reply = show_question(
            self, "确认清空",
            "确定要清空所有账单数据吗？\n此操作不可撤销！"
        )
        if reply == QMessageBox.Yes:
            self.app.db.delete_all_bills()
            show_info(self, "成功", "所有账单数据已清空")
            self.app.main_window.refresh_all()

    def on_show(self):
        self.path_entry.setText(self.app.config.data_path)

    def refresh(self):
        pass
