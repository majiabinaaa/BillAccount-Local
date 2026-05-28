"""Add bill page - centered form layout."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QScrollArea
from PySide6.QtCore import Qt

from ui.components.bill_form import BillForm
from ui.components.card import Card
from ui.utils import make_title, make_subtitle
from ui.dialogs import show_info


class AddBillPage(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setAlignment(Qt.AlignHCenter)
        content_layout.setContentsMargins(36, 24, 36, 24)
        content_layout.setSpacing(24)

        # Header
        content_layout.addWidget(make_title("记一笔"))
        content_layout.addWidget(make_subtitle("快速记录一笔收入或支出"))

        # Centered form card
        form_container = QWidget()
        form_container.setMaximumWidth(500)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)

        card = Card(padding=(28, 28, 28, 28), spacing=20)
        self.form = BillForm(self.app, on_save=self._on_saved)
        card.content_layout().addWidget(self.form)
        form_layout.addWidget(card)

        content_layout.addWidget(form_container)
        content_layout.addStretch()

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _on_saved(self):
        show_info(self, "成功", "账单已保存！")
        self.form.clear()

    def on_show(self):
        pass

    def refresh(self):
        pass
