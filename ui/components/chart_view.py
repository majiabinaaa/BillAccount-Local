import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use("Agg")

# ---- Chinese font setup ----
matplotlib.rcParams["font.sans-serif"] = [
    "Microsoft YaHei", "SimHei", "Noto Sans CJK SC",
    "WenQuanYi Micro Hei", "DejaVu Sans",
]
matplotlib.rcParams["axes.unicode_minus"] = False

# ---- Color palettes ----
PIE_COLORS = [
    "#EF5350", "#FF7043", "#FFA726", "#FFCA28", "#66BB6A",
    "#26C6DA", "#42A5F5", "#7E57C2", "#EC407A", "#8D6E63",
    "#78909C", "#5C6BC0",
]

INCOME_COLOR = "#4CAF50"
EXPENSE_COLOR = "#F44336"


def _get_theme_colors():
    """Return (bg, fg, grid_color) based on current CTk theme."""
    mode = ctk.get_appearance_mode()
    if mode == "Dark":
        return "#242424", "#e0e0e0", "#424242"
    else:
        return "#f5f5f5", "#212121", "#d0d0d0"


class ChartView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.figure = Figure(figsize=(5, 3.8), dpi=100)
        self.canvas = None
        self._annot = None
        self._hover_data = []

    def _apply_theme(self, ax):
        bg, fg, grid = _get_theme_colors()
        self.figure.patch.set_facecolor(bg)
        ax.set_facecolor(bg)
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
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.draw()
        bg, _, _ = _get_theme_colors()
        self.canvas.get_tk_widget().configure(background=bg, highlightbackground=bg)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.mpl_connect("motion_notify_event", self._on_hover)

    def pie_chart(self, data: list, title: str = "", show_inner_labels: bool = True):
        """
        data: list of (label, value) tuples.
        show_inner_labels: if True, show percentage inside; legend shows all labels.
        """
        self.figure.clear()
        self._hover_data = []
        if not data or all(v == 0 for _, v in data):
            # show empty message
            ax = self.figure.add_subplot(111)
            self._apply_theme(ax)
            ax.text(0.5, 0.5, "暂无数据", ha="center", va="center",
                    fontsize=16, color=_get_theme_colors()[1], alpha=0.5,
                    transform=ax.transAxes)
            ax.set_title(title, fontsize=15, fontweight="bold",
                         color=_get_theme_colors()[1])
            self.draw()
            return

        ax = self.figure.add_subplot(111)
        self._apply_theme(ax)

        labels = [d[0] for d in data]
        values = [d[1] for d in data]
        colors = PIE_COLORS[:len(data)]

        # Draw pie with percentages
        wedges, texts, autotexts = ax.pie(
            values, labels=None, autopct="%1.1f%%",
            colors=colors, startangle=90,
            pctdistance=0.6,
            textprops={"fontsize": 11, "color": "white"},
        )

        # Make percentage text bold
        for at in autotexts:
            at.set_fontweight("bold")

        # Build hover data
        for i, w in enumerate(wedges):
            self._hover_data.append({
                "wedge": w,
                "label": labels[i],
                "value": values[i],
                "pct": values[i] / sum(values) * 100 if sum(values) > 0 else 0,
            })

        ax.set_title(title, fontsize=15, fontweight="bold",
                     color=_get_theme_colors()[1])

        # Legend with category names
        ax.legend(wedges, [f"{l}  ¥{v:,.2f}" for l, v in zip(labels, values)],
                  title="分类", loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10,
                  title_fontsize=11)

        self.figure.tight_layout()
        self.draw()

    def bar_chart(self, labels: list, income_values: list, expense_values: list,
                  title: str = ""):
        self.figure.clear()
        self._hover_data = []
        if not labels:
            ax = self.figure.add_subplot(111)
            self._apply_theme(ax)
            ax.text(0.5, 0.5, "暂无数据", ha="center", va="center",
                    fontsize=16, color=_get_theme_colors()[1], alpha=0.5,
                    transform=ax.transAxes)
            ax.set_title(title, fontsize=15, fontweight="bold",
                         color=_get_theme_colors()[1])
            self.draw()
            return

        ax = self.figure.add_subplot(111)
        self._apply_theme(ax)
        bg, fg, grid = _get_theme_colors()

        x = range(len(labels))
        width = 0.32
        bars_in = ax.bar([i - width/2 for i in x], income_values, width,
                         label="收入", color=INCOME_COLOR, alpha=0.9)
        bars_ex = ax.bar([i + width/2 for i in x], expense_values, width,
                         label="支出", color=EXPENSE_COLOR, alpha=0.9)

        # add value labels on top of bars
        for bar, val in zip(bars_in, income_values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                        f"¥{val:,.0f}", ha="center", va="bottom",
                        fontsize=10, color=fg, fontweight="bold")
        for bar, val in zip(bars_ex, expense_values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                        f"¥{val:,.0f}", ha="center", va="bottom",
                        fontsize=10, color=fg, fontweight="bold")

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=10, rotation=0, ha="center")
        ax.set_title(title, fontsize=15, fontweight="bold", color=fg)
        ax.legend(fontsize=10, facecolor=bg, edgecolor=grid,
                  labelcolor=fg)
        ax.set_ylabel("金额 (元)", fontsize=10, color=fg)
        ax.grid(axis="y", alpha=0.2, color=grid)

        # Build hover data
        for i in range(len(labels)):
            self._hover_data.append({
                "bar_in": bars_in[i],
                "bar_ex": bars_ex[i],
                "label": labels[i],
                "income": income_values[i],
                "expense": expense_values[i],
            })

        self.figure.tight_layout()
        self.draw()

    def _on_hover(self, event):
        if event.inaxes is None or not self._hover_data:
            if self._annot:
                self._annot.set_visible(False)
                self.canvas.draw_idle()
            return

        # Check pie wedges
        for item in self._hover_data:
            if "wedge" in item:
                cont, _ = item["wedge"].contains(event)
                if cont:
                    text = f"{item['label']}\n¥{item['value']:,.2f}\n({item['pct']:.1f}%)"
                    self._show_annot(event, text)
                    return
            elif "bar_in" in item:
                in_cont, _ = item["bar_in"].contains(event)
                ex_cont, _ = item["bar_ex"].contains(event)
                if in_cont or ex_cont:
                    text = f"{item['label']}\n收入: ¥{item['income']:,.2f}\n支出: ¥{item['expense']:,.2f}"
                    self._show_annot(event, text)
                    return

        if self._annot:
            self._annot.set_visible(False)
            self.canvas.draw_idle()

    def _show_annot(self, event, text):
        bg, fg, _ = _get_theme_colors()
        if self._annot is None:
            self._annot = event.inaxes.annotate(
                "", xy=(0, 0), xytext=(15, 15),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.4", fc=bg, ec=fg, alpha=0.9),
                fontsize=10, color=fg,
                zorder=100,
            )
        self._annot.set_text(text)
        self._annot.xy = (event.xdata, event.ydata)
        self._annot.set_visible(True)
        self.canvas.draw_idle()
