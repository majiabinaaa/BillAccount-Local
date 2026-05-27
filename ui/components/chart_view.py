"""Chart view component using matplotlib with PySide6."""
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib

from ui.theme import COLORS, FONT_FAMILY

# Chinese font setup
matplotlib.rcParams["font.sans-serif"] = [
    "MXNLSZ", "851tegakizatsu", "ZCOOL KuaiLe", "Microsoft YaHei", "SimHei",
    "Noto Sans CJK SC", "WenQuanYi Micro Hei", "DejaVu Sans",
]
matplotlib.rcParams["axes.unicode_minus"] = False

# Apple-inspired color palettes
PIE_COLORS = [
    "#007AFF", "#FF9500", "#34C759", "#FF3B30", "#AF52DE",
    "#5AC8FA", "#FF2D55", "#FFCC00", "#30B0C7", "#FF6482",
    "#32ADE6", "#00C7BE",
]

INCOME_COLOR = "#34C759"
EXPENSE_COLOR = "#FF3B30"


class ChartView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 3.8), dpi=100)
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def _apply_theme(self, ax):
        fg = COLORS['text_primary']
        grid = COLORS['border']

        self.figure.patch.set_facecolor("none")
        ax.set_facecolor("none")
        ax.tick_params(colors=fg, labelsize=9)
        ax.xaxis.label.set_color(fg)
        ax.yaxis.label.set_color(fg)
        for spine in ax.spines.values():
            spine.set_edgecolor(grid)
        ax.title.set_color(fg)
        if ax.get_legend() is not None:
            for text in ax.get_legend().get_texts():
                text.set_color(fg)

    def draw(self):
        self.canvas.draw()

    def pie_chart(self, data, title="", show_inner_labels=True):
        self.figure.clear()
        fg = COLORS['text_primary']

        if not data or all(v == 0 for _, v in data):
            ax = self.figure.add_subplot(111)
            self._apply_theme(ax)
            ax.text(0.5, 0.5, "暂无数据", ha="center", va="center",
                    fontsize=16, color=fg, alpha=0.5,
                    transform=ax.transAxes)
            ax.set_title(title, fontsize=15, fontweight="bold", color=fg)
            self.draw()
            return

        ax = self.figure.add_subplot(111)
        self._apply_theme(ax)

        labels = [d[0] for d in data]
        values = [d[1] for d in data]
        colors = PIE_COLORS[:len(data)]

        wedges, texts, autotexts = ax.pie(
            values, labels=None, autopct="%1.1f%%",
            colors=colors, startangle=90,
            pctdistance=0.6,
            textprops={"fontsize": 11, "color": "white"},
        )

        for at in autotexts:
            at.set_fontweight("bold")

        ax.set_title(title, fontsize=15, fontweight="bold", color=fg)
        ax.legend(wedges, [f"{l}  ¥{v:,.2f}" for l, v in zip(labels, values)],
                  title="分类", loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10,
                  title_fontsize=11)

        self.figure.tight_layout()
        self.draw()

    def bar_chart(self, labels, income_values, expense_values, title=""):
        self.figure.clear()
        fg = COLORS['text_primary']
        grid = COLORS['border']

        if not labels:
            ax = self.figure.add_subplot(111)
            self._apply_theme(ax)
            ax.text(0.5, 0.5, "暂无数据", ha="center", va="center",
                    fontsize=16, color=fg, alpha=0.5,
                    transform=ax.transAxes)
            ax.set_title(title, fontsize=15, fontweight="bold", color=fg)
            self.draw()
            return

        ax = self.figure.add_subplot(111)
        self._apply_theme(ax)

        x = range(len(labels))
        width = 0.32
        bars_in = ax.bar([i - width / 2 for i in x], income_values, width,
                         label="收入", color=INCOME_COLOR, alpha=0.9)
        bars_ex = ax.bar([i + width / 2 for i in x], expense_values, width,
                         label="支出", color=EXPENSE_COLOR, alpha=0.9)

        for bar, val in zip(bars_in, income_values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                        f"¥{val:,.0f}", ha="center", va="bottom",
                        fontsize=8, color=fg, fontweight="bold")
        for bar, val in zip(bars_ex, expense_values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                        f"¥{val:,.0f}", ha="center", va="bottom",
                        fontsize=8, color=fg, fontweight="bold")

        # Adjust label rotation based on count
        n = len(labels)
        if n > 15:
            rotation = 60
            ha_align = "right"
            font_size = 7
        elif n > 8:
            rotation = 45
            ha_align = "right"
            font_size = 8
        else:
            rotation = 0
            ha_align = "center"
            font_size = 9

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=font_size, rotation=rotation, ha=ha_align)
        ax.set_title(title, fontsize=14, fontweight="bold", color=fg)
        ax.legend(fontsize=9, facecolor="none", edgecolor=grid, labelcolor=fg)
        ax.set_ylabel("金额 (元)", fontsize=9, color=fg)
        ax.grid(axis="y", alpha=0.2, color=grid)

        self.figure.tight_layout()
        self.draw()
