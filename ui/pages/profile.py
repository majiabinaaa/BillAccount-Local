"""Profile page - consumer personality and health."""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QFrame, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.theme import COLORS, set_css_class, FONT_FAMILY
from ui.utils import make_label, make_title, make_heading, clear_layout
from ui.components.card import Card
from ui.components.progress_bar import ProgressBar
from ui.components.empty_state import EmptyState
from core.analytics import calculate_health_score, get_consumer_profile


class ProfilePage(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.db = app.db
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
        layout.addWidget(make_title("消费画像"))

        # Personality Card
        personality_card = Card(padding=(28, 28, 28, 28), spacing=12)
        p_layout = personality_card.content_layout()
        p_layout.setAlignment(Qt.AlignCenter)

        self.emoji_label = QLabel()
        self.emoji_label.setAlignment(Qt.AlignCenter)
        emoji_font = QFont()
        emoji_font.setPointSize(48)
        self.emoji_label.setFont(emoji_font)
        p_layout.addWidget(self.emoji_label)

        self.personality_title = make_label("", 22, True)
        self.personality_title.setAlignment(Qt.AlignCenter)
        p_layout.addWidget(self.personality_title)

        self.personality_desc = make_label("", 14, color=COLORS['text_secondary'])
        self.personality_desc.setWordWrap(True)
        self.personality_desc.setMinimumHeight(60)
        self.personality_desc.setAlignment(Qt.AlignCenter)
        p_layout.addWidget(self.personality_desc)

        layout.addWidget(personality_card)

        # Savings bar
        self.savings_label = make_label("", 13, color=COLORS['text_tertiary'])
        layout.addWidget(self.savings_label)

        self.savings_bar = ProgressBar("储蓄率", 0, 100, color=COLORS['success'], show_value=True)
        self.savings_bar.set_bar_width(600)
        layout.addWidget(self.savings_bar)

        # Suggestion Card
        suggestion_card = Card(padding=(20, 20, 20, 20), spacing=8)
        s_layout = suggestion_card.content_layout()
        s_layout.addWidget(make_heading("个性化建议"))
        self.suggestion_text = make_label("", 14, color=COLORS['text_secondary'])
        self.suggestion_text.setWordWrap(True)
        s_layout.addWidget(self.suggestion_text)
        layout.addWidget(suggestion_card)

        # Top categories
        cat_section = QVBoxLayout()
        cat_section.setSpacing(8)
        cat_section.addWidget(make_heading("本月支出 Top 5"))
        self.cat_list = QVBoxLayout()
        self.cat_list.setSpacing(8)
        cat_section.addLayout(self.cat_list)
        layout.addLayout(cat_section)

        # Health Card
        health_card = Card(padding=(24, 24, 24, 24), spacing=12)
        h_layout = health_card.content_layout()
        h_layout.addWidget(make_heading("财务健康评分"))

        self.health_total_label = make_label("", 36, True)
        self.health_total_label.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(self.health_total_label)

        self.health_breakdown = QVBoxLayout()
        self.health_breakdown.setSpacing(10)
        h_layout.addLayout(self.health_breakdown)
        layout.addWidget(health_card)

        layout.addStretch()

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def on_show(self):
        self.refresh()

    def refresh(self):
        profile = get_consumer_profile(self.db)
        health = calculate_health_score(self.db)

        # Personality
        self.emoji_label.setText(profile["emoji"])
        self.personality_title.setText(profile["title"])
        self.personality_desc.setText(profile["desc"])

        # Savings bar
        sr = profile["savings_rate"]
        self.savings_label.setText(f"本月储蓄率: {sr}%  ({'收入 > 支出' if profile['balance'] >= 0 else '支出 > 收入'})")
        self.savings_bar.update(min(sr, 100), 100)

        # Suggestion
        self.suggestion_text.setText(profile["suggestion"])

        # Top categories
        clear_layout(self.cat_list)
        top = profile["top_categories"]
        if not top:
            self.cat_list.addWidget(EmptyState("📊", "暂无支出数据"))
        else:
            max_amt = top[0]["amount"] if top else 1
            cat_colors = ["#FF3B30", "#FF9500", "#FFCC00", "#007AFF", "#AF52DE"]
            for i, cat in enumerate(top):
                bar = ProgressBar(
                    f"{cat['name']}  ¥{cat['amount']:,.0f}  {cat['pct']}%",
                    cat['amount'], max_amt,
                    color=cat_colors[i % len(cat_colors)],
                    show_value=False
                )
                bar.set_label_width(200)
                bar.set_bar_width(400)
                self.cat_list.addWidget(bar)

        # Health
        score = health["score"]
        color = health["color"]
        self.health_total_label.setText(f"{score}分 · {health['label']}")
        self.health_total_label.setStyleSheet(f"color: {color};")

        clear_layout(self.health_breakdown)
        bd = health["breakdown"]
        dim_colors = {"savings": COLORS['success'], "coverage": COLORS['info'],
                      "consistency": COLORS['warning'], "diversity": "#AF52DE"}

        for key in ["savings", "coverage", "consistency", "diversity"]:
            item = bd[key]
            bar = ProgressBar(item["label"], item["score"], item["max"],
                              color=dim_colors.get(key, COLORS['primary']), show_value=True)
            bar.set_bar_width(350)
            self.health_breakdown.addWidget(bar)
