"""Export page - export reports as PNG."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame, QScrollArea, QComboBox,
                               QMessageBox, QFileDialog)
from PySide6.QtCore import Qt, QDate, QThread, Signal
from PySide6.QtGui import QFont

from datetime import date, timedelta
from pathlib import Path
import os
import sys
import subprocess

from ui.theme import COLORS, set_css_class, FONT_FAMILY
from ui.utils import make_label, make_title, make_subtitle, make_heading
from ui.components.card import Card


class ExportWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, cmd, timeout):
        super().__init__()
        self.cmd = cmd
        self.timeout = timeout

    def run(self):
        try:
            popen_kw = {"stdin": subprocess.DEVNULL, "stdout": subprocess.PIPE,
                        "stderr": subprocess.PIPE, "text": True}
            if sys.platform == "win32":
                popen_kw["creationflags"] = subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS

            proc = subprocess.Popen(self.cmd, **popen_kw)
            out, err = proc.communicate(timeout=self.timeout)

            if proc.returncode == 0:
                self.finished.emit(True, "")
            else:
                detail = err.strip() if err else ""
                msg = f"导出失败 (code={proc.returncode})"
                if detail:
                    msg += f"\n\n{detail[-800:]}"
                self.finished.emit(False, msg)
        except subprocess.TimeoutExpired:
            proc.kill()
            self.finished.emit(False, f"导出超时（{self.timeout}秒）")
        except Exception as e:
            self.finished.emit(False, f"导出异常：{str(e)}")


class ExportPage(QWidget):
    _TIMEOUTS = {"weekly": 180, "monthly": 300, "yearly": 480}

    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.db = app.db
        self._last_path = None
        self._worker = None
        self._week_offset = 0
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(20)

        # Header
        layout.addWidget(make_title("导出报告"))
        layout.addWidget(make_subtitle("生成精美 PNG 报告，支持导出任意时间段"))

        # Report types - 3 cards in a row
        layout.addWidget(make_heading("报告类型"))

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        cards = [
            ("周报", "#FF2D55", "一页式·手帐风格", "weekly", "导出周报"),
            ("月报", "#AF52DE", "双页报告·全景回顾", "monthly", "导出月报"),
            ("年报", "#34C759", "三页画册·年度总结", "yearly", "导出年报"),
        ]

        for title, color, desc, report_type, btn_text in cards:
            card = Card(padding=(20, 20, 20, 20), spacing=10)
            card_layout = card.content_layout()

            card_layout.addWidget(make_label(title, 18, True))
            card_layout.addWidget(make_label(desc, 12, color=COLORS['text_tertiary']))

            btn = QPushButton(btn_text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(38)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 19px;
                    font-weight: 600;
                    font-size: 14px;
                    font-family: {FONT_FAMILY};
                }}
                QPushButton:hover {{ opacity: 0.9; }}
            """)
            btn.clicked.connect(lambda checked, rt=report_type: self._ask_and_export(rt))
            card_layout.addWidget(btn)

            cards_layout.addWidget(card)

        layout.addLayout(cards_layout)

        # Date selection - all in one card
        date_card = Card(padding=(20, 20, 20, 20), spacing=14)
        date_layout = date_card.content_layout()
        date_layout.addWidget(make_heading("选择日期范围"))

        # Weekly
        weekly_row = QHBoxLayout()
        weekly_row.setSpacing(8)
        weekly_row.addWidget(make_label("周报", 13, color=COLORS['text_secondary']))
        self.week_label = make_label("", 13)
        self.week_label.setMinimumWidth(220)
        weekly_row.addWidget(self.week_label)

        prev_btn = QPushButton("◀")
        prev_btn.setFixedSize(32, 32)
        prev_btn.setCursor(Qt.PointingHandCursor)
        set_css_class(prev_btn, "nav-arrow")
        prev_btn.clicked.connect(lambda: self._nav_week(-1))
        weekly_row.addWidget(prev_btn)

        next_btn = QPushButton("▶")
        next_btn.setFixedSize(32, 32)
        next_btn.setCursor(Qt.PointingHandCursor)
        set_css_class(next_btn, "nav-arrow")
        next_btn.clicked.connect(lambda: self._nav_week(1))
        weekly_row.addWidget(next_btn)

        today_btn = QPushButton("今天")
        today_btn.setCursor(Qt.PointingHandCursor)
        set_css_class(today_btn, "ghost-btn")
        today_btn.clicked.connect(lambda: self._nav_week(0, absolute=True))
        weekly_row.addWidget(today_btn)

        weekly_row.addStretch()
        date_layout.addLayout(weekly_row)

        # Monthly
        monthly_row = QHBoxLayout()
        monthly_row.setSpacing(8)
        monthly_row.addWidget(make_label("月报", 13, color=COLORS['text_secondary']))

        self.month_year_combo = QComboBox()
        self.month_year_combo.setFixedWidth(80)
        self.month_year_combo.addItems([str(y) for y in range(2020, 2031)])
        self.month_year_combo.setCurrentText(str(date.today().year))
        monthly_row.addWidget(self.month_year_combo)
        monthly_row.addWidget(make_label("年", 13))

        self.month_combo = QComboBox()
        self.month_combo.setFixedWidth(60)
        self.month_combo.addItems([str(m) for m in range(1, 13)])
        self.month_combo.setCurrentText(str(date.today().month))
        monthly_row.addWidget(self.month_combo)
        monthly_row.addWidget(make_label("月", 13))

        monthly_row.addStretch()
        date_layout.addLayout(monthly_row)

        # Yearly
        yearly_row = QHBoxLayout()
        yearly_row.setSpacing(8)
        yearly_row.addWidget(make_label("年报", 13, color=COLORS['text_secondary']))

        self.year_combo = QComboBox()
        self.year_combo.setFixedWidth(80)
        self.year_combo.addItems([str(y) for y in range(2020, 2031)])
        self.year_combo.setCurrentText(str(date.today().year))
        yearly_row.addWidget(self.year_combo)
        yearly_row.addWidget(make_label("年", 13))

        yearly_row.addStretch()
        date_layout.addLayout(yearly_row)

        layout.addWidget(date_card)

        # Status
        self.status_label = make_label("", 12, color=COLORS['text_tertiary'])
        layout.addWidget(self.status_label)

        self._update_week_label()

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _nav_week(self, delta, absolute=False):
        if absolute:
            self._week_offset = 0
        else:
            self._week_offset += delta
            if self._week_offset > 0:
                self._week_offset = 0
        self._update_week_label()

    def _update_week_label(self):
        today = date.today()
        monday = today - timedelta(days=today.weekday()) + timedelta(weeks=self._week_offset)
        sunday = monday + timedelta(days=6)
        prefix = "本周" if self._week_offset == 0 else ("上周" if self._week_offset == -1 else f"{abs(self._week_offset)}周前")
        self.week_label.setText(f"{prefix}: {monday.isoformat()} ~ {sunday.isoformat()}")

    def _ask_and_export(self, report_type):
        if self._worker and self._worker.isRunning():
            QMessageBox.warning(self, "请稍候", "正在生成报告，请等待完成后再试。")
            return

        titles = {"weekly": "周报", "monthly": "月报", "yearly": "年报"}
        default_name = self._get_default_filename(report_type)

        path, _ = QFileDialog.getSaveFileName(self, "导出" + titles.get(report_type, "报告"),
                                              default_name, "PNG 图片 (*.png)")
        if not path:
            return

        self._last_path = path
        self.status_label.setText("正在生成报告，请稍候...")

        frozen = getattr(sys, "frozen", False)
        resolved_root = str(Path(__file__).resolve().parent.parent.parent)
        main_script = os.path.join(resolved_root, "main.py")
        db_path = os.path.abspath(self.app.config.data_path)

        if frozen:
            cmd = [sys.executable, "--export", report_type, path, db_path]
        else:
            cmd = [sys.executable, "-u", main_script, "--export", report_type, path, db_path]

        if report_type == "weekly":
            today = date.today()
            monday = today - timedelta(days=today.weekday()) + timedelta(weeks=self._week_offset)
            cmd.append(monday.isoformat())
        elif report_type == "monthly":
            cmd.extend([self.month_year_combo.currentText(), self.month_combo.currentText()])
        elif report_type == "yearly":
            cmd.append(self.year_combo.currentText())

        timeout = self._TIMEOUTS.get(report_type, 300)
        self._worker = ExportWorker(cmd, timeout)
        self._worker.finished.connect(self._on_result)
        self._worker.start()

    def _get_default_filename(self, report_type):
        if report_type == "weekly":
            today = date.today()
            monday = today - timedelta(days=today.weekday()) + timedelta(weeks=self._week_offset)
            return f"周报_{monday.isoformat()}.png"
        elif report_type == "monthly":
            return f"月报_{self.month_year_combo.currentText()}{self.month_combo.currentText().zfill(2)}.png"
        elif report_type == "yearly":
            return f"年报_{self.year_combo.currentText()}.png"
        return f"报告_{date.today().isoformat()}.png"

    def _on_result(self, ok, err):
        self.status_label.setText("")
        if ok:
            reply = QMessageBox.information(self, "导出成功",
                                            f"报告已生成！\n\n{self._last_path}\n\n是否打开查看？",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                self._ask_open(self._last_path)
        else:
            QMessageBox.critical(self, "导出失败", err)

    def _ask_open(self, path):
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
        self.status_label.setText("")

    def on_hide(self):
        if self._worker and self._worker.isRunning():
            self._worker.terminate()

    def refresh(self):
        pass
