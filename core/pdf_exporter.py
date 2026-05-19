"""Kawaii-style personalized PDF reports — weekly / monthly / yearly."""
import io
import os
import random
from datetime import date, timedelta
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, Image, PageBreak)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, Circle, Line, String, Group
from reportlab.graphics import renderPDF
from reportlab.lib.colors import Color, HexColor

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from core.analytics import get_consumer_profile
from core.report_generator import generate_weekly_report

# ==================== Fonts ====================

_FONT_OK = False


def _setup_fonts():
    global _FONT_OK
    if _FONT_OK:
        return True
    for fp in ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf"]:
        if os.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont("CJK", fp))
                pdfmetrics.registerFont(TTFont("CJKB", fp, subfontIndex=1)
                                        if fp.endswith(".ttc") else TTFont("CJKB", fp))
                _FONT_OK = True
                return True
            except Exception:
                continue
    return False


_FONT_OK = _setup_fonts()
F = "CJK" if _FONT_OK else "Helvetica"
FB = "CJKB" if _FONT_OK else "Helvetica-Bold"

# ==================== Color Palettes ====================

# Weekly — warm peach/coral
W_HDR_TOP = HexColor("#FF8A65")
W_HDR_BOT = HexColor("#FFAB91")
W_BG = HexColor("#FFF9F5")
W_CARD = HexColor("#FFFFFF")
W_ACCENT = HexColor("#FF7043")
W_TEXT = HexColor("#4E342E")
W_SUB = HexColor("#8D6E63")

# Monthly — fresh green/mint
M_HDR_TOP = HexColor("#66BB6A")
M_HDR_BOT = HexColor("#A5D6A7")
M_BG = HexColor("#F5FBF5")
M_CARD = HexColor("#FFFFFF")
M_ACCENT = HexColor("#43A047")
M_TEXT = HexColor("#2E3B2E")
M_SUB = HexColor("#6B8E6B")

# Yearly — dreamy blue/sky
Y_HDR_TOP = HexColor("#42A5F5")
Y_HDR_BOT = HexColor("#90CAF9")
Y_BG = HexColor("#F5F9FD")
Y_CARD = HexColor("#FFFFFF")
Y_ACCENT = HexColor("#1E88E5")
Y_TEXT = HexColor("#1A2B3C")
Y_SUB = HexColor("#607D8B")

# Category colors for progress bars
CAT_COLORS = [
    HexColor("#EF5350"), HexColor("#FF7043"), HexColor("#FFA726"),
    HexColor("#FFCA28"), HexColor("#66BB6A"), HexColor("#26C6DA"),
    HexColor("#42A5F5"), HexColor("#7E57C2"), HexColor("#EC407A"),
    HexColor("#8D6E63"),
]

# ==================== Drawing Helpers ====================

def _round_rect(d: Drawing, x, y, w, h, r, fill, stroke=None):
    """Draw a rounded rectangle."""
    d.add(Rect(x + r, y, w - 2 * r, h, fillColor=fill, strokeColor=None))
    d.add(Rect(x, y + r, w, h - 2 * r, fillColor=fill, strokeColor=None))
    d.add(Circle(x + r, y + r, r, fillColor=fill, strokeColor=None))
    d.add(Circle(x + w - r, y + r, r, fillColor=fill, strokeColor=None))
    d.add(Circle(x + r, y + h - r, r, fillColor=fill, strokeColor=None))
    d.add(Circle(x + w - r, y + h - r, r, fillColor=fill, strokeColor=None))
    if stroke:
        d.add(Line(x + r, y, x + w - r, y, strokeColor=stroke, strokeWidth=1))
        d.add(Line(x + r, y + h, x + w - r, y + h, strokeColor=stroke, strokeWidth=1))
        d.add(Line(x, y + r, x, y + h - r, strokeColor=stroke, strokeWidth=1))
        d.add(Line(x + w, y + r, x + w, y + h - r, strokeColor=stroke, strokeWidth=1))


def _dot_pattern(d: Drawing, x, y, w, h, spacing, color, radius=1.5):
    """Draw a dot grid pattern."""
    cx = x
    while cx < x + w:
        cy = y
        while cy < y + h:
            d.add(Circle(cx, cy, radius, fillColor=color, strokeColor=None))
            cy += spacing
        cx += spacing


def _star_rating(count, max_count, x, y, size, fill, empty):
    """Return a Group of star circles."""
    g = Group()
    for i in range(max_count):
        sx = x + i * (size + 4)
        c = fill if i < count else empty
        g.add(Circle(sx, y, size / 2, fillColor=c, strokeColor=None))
    return g


def _gradient_header(d: Drawing, w, h, top_color, bot_color):
    """Add a colored header background with dot decorations."""
    d.add(Rect(0, 0, w, h, fillColor=top_color, strokeColor=None))
    # bottom decorative strip in lighter color
    d.add(Rect(0, 0, w, 6, fillColor=bot_color, strokeColor=None))


def _make_chart_image(fig, width, height) -> Image:
    """Convert matplotlib figure to reportlab Image."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return Image(buf, width=width, height=height)


# ==================== Chart Generators ====================

def _cute_pie_chart(data: list, title: str, size=(5.5, 4)):
    matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    matplotlib.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=size, dpi=140)
    labels = [d[0] for d in data]
    values = [d[1] for d in data]
    pie_colors = ["#EF5350", "#FF7043", "#FFA726", "#FFCA28", "#66BB6A",
                  "#26C6DA", "#42A5F5", "#7E57C2", "#EC407A", "#8D6E63"]

    wedges, _, autotexts = ax.pie(
        values, labels=None, autopct="%1.1f%%",
        colors=pie_colors[:len(data)],
        startangle=140, pctdistance=0.65,
        textprops={"fontsize": 11, "color": "white", "fontweight": "bold"},
    )
    ax.legend(wedges, [f"{l}" for l in labels],
              loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10,
              title=title, title_fontsize=12)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    fig.tight_layout()
    return fig


def _cute_line_chart(months, incomes, expenses, size=(9, 3.5)):
    matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    matplotlib.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=size, dpi=140)
    x = range(len(months))
    ax.plot(x, incomes, "o-", color="#66BB6A", label="收入", linewidth=2.5, markersize=7)
    ax.plot(x, expenses, "o-", color="#EF5350", label="支出", linewidth=2.5, markersize=7)
    for i in x:
        if incomes[i] > 0:
            ax.text(i, incomes[i] + max(incomes) * 0.03, f"¥{incomes[i]:,.0f}",
                    ha="center", fontsize=8, color="#388E3C", fontweight="bold")
        if expenses[i] > 0:
            ax.text(i, expenses[i] + max(expenses) * 0.03, f"¥{expenses[i]:,.0f}",
                    ha="center", fontsize=8, color="#D32F2F", fontweight="bold")
    ax.fill_between(x, incomes, alpha=0.06, color="#66BB6A")
    ax.fill_between(x, expenses, alpha=0.06, color="#EF5350")
    ax.set_xticks(x)
    ax.set_xticklabels(months, fontsize=10, rotation=0)
    ax.legend(fontsize=12, loc="upper left", framealpha=0.8)
    ax.grid(axis="y", alpha=0.2, color="#BDBDBD")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    fig.tight_layout()
    return fig


# ==================== Styles ====================

def _ss():
    """Get fresh styles each time (some are mutated)."""
    from reportlab.lib.styles import getSampleStyleSheet
    base = getSampleStyleSheet()
    base.add(ParagraphStyle("H1", fontName=FB, fontSize=22, leading=28,
                            textColor=colors.white, alignment=TA_CENTER))
    base.add(ParagraphStyle("H2", fontName=FB, fontSize=16, leading=22,
                            textColor=colors.HexColor("#333333")))
    base.add(ParagraphStyle("H3", fontName=FB, fontSize=13, leading=18,
                            textColor=colors.HexColor("#444444")))
    base.add(ParagraphStyle("BODY", fontName=F, fontSize=11, leading=18,
                            textColor=colors.HexColor("#555555")))
    base.add(ParagraphStyle("SMALL", fontName=F, fontSize=8, leading=12,
                            textColor=colors.HexColor("#999999"), alignment=TA_CENTER))
    base.add(ParagraphStyle("QUOTE", fontName=F, fontSize=12, leading=20,
                            textColor=colors.HexColor("#777777"), alignment=TA_CENTER))
    base.add(ParagraphStyle("RIGHT", fontName=F, fontSize=10, leading=14,
                            textColor=colors.HexColor("#999999"), alignment=TA_RIGHT))
    return base


def _card_table(html: str, accent: HexColor, width: int) -> Table:
    ss = _ss()
    t = Table([[Paragraph(html, ss["BODY"])]], colWidths=[width - 32])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
        ("BOX", (0, 0), (-1, -1), 1, accent),
    ]))
    return t


def _dots_divider(width: int, color) -> Drawing:
    d = Drawing(width, 12)
    for i in range(0, width, 8):
        d.add(Circle(i + 4, 6, 1.5, fillColor=color, strokeColor=None))
    return d


# ==================================================================
#   WEEKLY — 正方形社交卡 500×500pt
# ==================================================================

def generate_weekly_pdf(db, filepath: str):
    _setup_fonts()
    ss = _ss()
    report = generate_weekly_report(db, 0)

    W, H = 500, 500
    doc = SimpleDocTemplate(filepath, pagesize=(W, H),
                            leftMargin=24, rightMargin=24,
                            topMargin=24, bottomMargin=24)
    story = []

    # --- Header with gradient ---
    hdr = Drawing(W - 48, 72)
    _gradient_header(hdr, W - 48, 72, W_HDR_TOP, W_HDR_BOT)
    # decorative dots in header
    _dot_pattern(hdr, 10, 55, W - 68, 12, 14, HexColor("#FFFFFF44"), 2)
    # emoji
    hdr.add(String((W - 48) / 2 - 90, 42, "🌟 一周消费手帐 🌟",
                   fontName=FB, fontSize=18, fillColor=colors.white,
                   textAnchor="middle"))
    week_label = report["week_label"] if report else date.today().isoformat()
    hdr.add(String((W - 48) / 2, 16, week_label,
                   fontName=F, fontSize=10, fillColor=HexColor("#FFFFFFCC"),
                   textAnchor="middle"))
    story.append(hdr)
    story.append(Spacer(1, 10))

    if not report or (report["total_income"] == 0 and report["total_expense"] == 0):
        story.append(Paragraph("📝 这周还没有记账哦～", ss["BODY"]))
        story.append(Paragraph("开始记录你的第一笔消费吧！", ss["QUOTE"]))
        doc.build(story)
        return

    # --- Summary row ---
    bal = report["balance"]
    summary_html = (
        f"💰 收入 <b>¥{report['total_income']:,.0f}</b>　"
        f"💸 支出 <b>¥{report['total_expense']:,.0f}</b>　"
        f"{'😊' if bal >= 0 else '😰'} 结余 <b>{'+' if bal >= 0 else '-'}¥{abs(bal):,.0f}</b>"
    )
    story.append(_card_table(summary_html, W_ACCENT, W - 48))
    story.append(Spacer(1, 8))

    # --- Pie chart ---
    cat_data = db.get_category_summary(report["week_start"], report["week_end"], "expense")
    if cat_data and sum(v for _, v in cat_data) > 0:
        fig = _cute_pie_chart(cat_data, "钱去哪了？", size=(4.8, 3.2))
        img = _make_chart_image(fig, W - 60, int((W - 60) * 0.65))
        story.append(img)
        story.append(Spacer(1, 8))

    # --- Category bars ---
    if cat_data:
        total_exp = sum(v for _, v in cat_data)
        bars_html = ""
        for i, (name, val) in enumerate(cat_data[:5]):
            pct = val / total_exp * 100 if total_exp > 0 else 0
            bar_len = int(pct / 100 * 30)
            bar = "█" * bar_len + "░" * (30 - bar_len)
            color_icon = ["🍜", "🚗", "🛍", "🏠", "🎬", "💊", "📚", "📱", "✨"][i % 9]
            bars_html += f"{color_icon} {name} {bar} {pct:.0f}%<br/>"
        story.append(_card_table(bars_html, W_ACCENT, W - 48))
        story.append(Spacer(1, 8))

    # --- Personality ---
    profile = get_consumer_profile(db)
    pers_html = (
        f"🎭 这周你是 <b>{profile['emoji']}「{profile['title']}」</b><br/>"
        f"　　{profile['desc'][:70]}..."
    )
    story.append(_card_table(pers_html, W_ACCENT, W - 48))
    story.append(Spacer(1, 8))

    # --- Achievements ---
    ach_list = []
    if report["record_days"] == report["checked_days"]:
        ach_list.append(f"🌟 连续记账 {report['record_days']} 天，太自律了！")
    if report["savings_rate"] > 50:
        ach_list.append(f"💎 储蓄率 {report['savings_rate']:.0f}%，超过 80% 的人")
    if report["savings_rate"] > 30:
        ach_list.append(f"👍 存下了 {report['savings_rate']:.0f}% 的收入")
    for t in report.get("trends", [])[:2]:
        if t["direction"] == "down":
            ach_list.append(f"📉 {t['category']}比上周少了 {t['change_pct']}%，省钱小能手！")
    if report["balance"] < 0:
        ach_list.append(f"⚠️ 这周花超了，下周加油哦～")

    if ach_list:
        ach_html = "🏆 本周成就<br/>" + "<br/>".join(f"　　{a}" for a in ach_list)
        story.append(_card_table(ach_html, W_ACCENT, W - 48))
        story.append(Spacer(1, 8))

    # --- Quote ---
    quotes = [
        "「花得明白，存得踏实」",
        "「今天的节约，是明天的浪漫」",
        "「每一笔记账，都是对未来的温柔」",
        "「钱是用来让生活更好的，不是让生活更累的」",
        "「小账本里藏着大智慧」",
    ]
    story.append(Paragraph(random.choice(quotes), ss["QUOTE"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("记账本 · 用心记录每一笔 💕", ss["SMALL"]))

    doc.build(story)


# ==================================================================
#   MONTHLY — A5 护照风 420×595pt
# ==================================================================

def generate_monthly_pdf(db, filepath: str):
    _setup_fonts()
    ss = _ss()
    today = date.today()
    month_start = today.replace(day=1)
    if today.month == 12:
        month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    ms = db.get_summary(month_start, month_end)
    profile = get_consumer_profile(db)
    month_name = today.strftime("%B").upper()

    W, H = 420, 595
    doc = SimpleDocTemplate(filepath, pagesize=(W, H),
                            leftMargin=20, rightMargin=20,
                            topMargin=18, bottomMargin=18)
    story = []

    # --- Cover header ---
    hdr = Drawing(W - 40, 90)
    _gradient_header(hdr, W - 40, 90, M_HDR_TOP, M_HDR_BOT)
    hdr.add(String((W - 40) / 2, 55, "FINANCIAL PASSPORT",
                   fontName=FB, fontSize=20, fillColor=colors.white,
                   textAnchor="middle"))
    hdr.add(String((W - 40) / 2, 30, f"{month_name}  ·  {today.year}年{today.month}月",
                   fontName=F, fontSize=11, fillColor=HexColor("#FFFFFFDD"),
                   textAnchor="middle"))
    _dot_pattern(hdr, 15, 10, W - 70, 8, 10, HexColor("#FFFFFF33"), 1.5)
    story.append(hdr)
    story.append(Spacer(1, 10))

    # --- Monthly numbers ---
    bal = ms.balance
    sr = (ms.balance / ms.total_income * 100) if ms.total_income > 0 else 0
    star_count = 5 if sr > 60 else 4 if sr > 40 else 3 if sr > 20 else 2 if sr > 0 else 1
    stars = "⭐" * star_count + "☆" * (5 - star_count)

    num_html = (
        f"📊 月度回顾<br/><br/>"
        f"💰 收入 <b>¥{ms.total_income:,.0f}</b>　"
        f"💸 支出 <b>¥{ms.total_expense:,.0f}</b><br/>"
        f"🏦 结余 <b>{'+' if bal >= 0 else '-'}¥{abs(bal):,.0f}</b>　"
        f"📈 储蓄率 <b>{sr:.1f}%</b><br/>"
        f"财务健康 {stars} ({'优秀' if sr > 40 else '良好' if sr > 20 else '加油'})"
    )
    story.append(_card_table(num_html, M_ACCENT, W - 40))
    story.append(Spacer(1, 8))

    # --- Pie chart ---
    cat_data = db.get_category_summary(month_start, month_end, "expense")
    if cat_data and sum(v for _, v in cat_data) > 0:
        fig = _cute_pie_chart(cat_data, f"{today.month}月支出", size=(5, 3.5))
        img = _make_chart_image(fig, W - 50, int((W - 50) * 0.7))
        story.append(img)
        story.append(Spacer(1, 8))

    # --- Personality ---
    pers_html = (
        f"🎭 本月消费人格<br/>"
        f"　　<b>{profile['emoji']} {profile['title']}</b><br/>"
        f"　　{profile['desc']}"
    )
    story.append(_card_table(pers_html, M_ACCENT, W - 40))
    story.append(Spacer(1, 8))

    # --- Month's best ---
    bills = db.get_bills(start_date=month_start, end_date=month_end,
                         bill_type="expense", limit=300)
    biggest = None
    day_spending = {}
    for b in bills:
        if biggest is None or b.amount > biggest.amount:
            biggest = b
        dk = b.bill_date.isoformat() if hasattr(b.bill_date, "isoformat") else str(b.bill_date)
        day_spending[dk] = day_spending.get(dk, 0) + b.amount

    best_html = "🏅 月度之最<br/>"
    if biggest:
        best_html += (
            f"　　🥇 最大开销: {biggest.category_name or '未分类'}"
            f" ¥{biggest.amount:,.0f}<br/>"
        )
    if day_spending:
        cheapest = min(day_spending.items(), key=lambda x: x[1])
        best_html += f"　　🥈 最省日: {cheapest[0]} 仅 ¥{cheapest[1]:,.0f}<br/>"
    # find category that dropped the most vs nothing — just show top saving tip
    if cat_data:
        best_html += f"　　🥉 支出TOP1: {cat_data[0][0]} ¥{cat_data[0][1]:,.0f}"
    story.append(_card_table(best_html, M_ACCENT, W - 40))
    story.append(Spacer(1, 8))

    # --- Projection ---
    days_passed = max((today - month_start).days, 1)
    daily_avg = ms.total_expense / days_passed
    projected = daily_avg * ((month_end - month_start).days + 1)
    proj_html = (
        f"📈 下月预测<br/><br/>"
        f"日均支出 ¥{daily_avg:,.0f}，按此节奏<br/>"
        f"下月预计支出 <b>¥{projected:,.0f}</b>"
    )
    story.append(_card_table(proj_html, M_ACCENT, W - 40))
    story.append(Spacer(1, 8))

    # --- Advice ---
    story.append(_card_table(f"💡 Tips<br/><br/>{profile['suggestion']}", M_ACCENT, W - 40))
    story.append(Spacer(1, 4))
    story.append(Paragraph("记账本 · 用心记录每一笔 💚", ss["SMALL"]))

    doc.build(story)


# ==================================================================
#   YEARLY — A4 画册
# ==================================================================

def generate_yearly_pdf(db, filepath: str):
    _setup_fonts()
    ss = _ss()
    today = date.today()
    year_start = date(today.year, 1, 1)
    year_end = date(today.year, 12, 31)

    ys = db.get_summary(year_start, min(year_end, today))
    profile = get_consumer_profile(db)
    cat_data = db.get_category_summary(year_start, today, "expense")

    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            leftMargin=30, rightMargin=30,
                            topMargin=24, bottomMargin=24)
    story = []

    W = A4[0] - 60  # usable width

    # --- Cover ---
    hdr = Drawing(W, 120)
    _gradient_header(hdr, W, 120, Y_HDR_TOP, Y_HDR_BOT)
    hdr.add(String(W / 2, 80, str(today.year),
                   fontName=FB, fontSize=42, fillColor=colors.white,
                   textAnchor="middle"))
    hdr.add(String(W / 2, 48, "MY MONEY STORY",
                   fontName=FB, fontSize=22, fillColor=colors.white,
                   textAnchor="middle"))
    hdr.add(String(W / 2, 22, "年度财务回忆录 · 记账本荣誉出品",
                   fontName=F, fontSize=10, fillColor=HexColor("#FFFFFFCC"),
                   textAnchor="middle"))
    _dot_pattern(hdr, 30, 100, W - 60, 8, 16, HexColor("#FFFFFF33"), 2)
    story.append(hdr)
    story.append(Spacer(1, 16))

    # --- Year in Numbers ---
    months_passed = today.month
    sr = (ys.balance / ys.total_income * 100) if ys.total_income > 0 else 0
    monthly_avg = ys.total_expense / max(months_passed, 1)

    num_html = (
        f"📊 {today.year} · 年度数据<br/><br/>"
        f"💰 总收入 <b>¥{ys.total_income:,.0f}</b><br/>"
        f"💸 总支出 <b>¥{ys.total_expense:,.0f}</b><br/>"
        f"🏦 净储蓄 <b>¥{ys.balance:,.0f}</b><br/>"
        f"📈 储蓄率 <b>{sr:.1f}%</b> · 月均支出 <b>¥{monthly_avg:,.0f}</b>"
    )
    story.append(_card_table(num_html, Y_ACCENT, W))
    story.append(Spacer(1, 12))

    # --- Monthly trend ---
    months_labels, incomes, expenses = [], [], []
    for m in range(1, today.month + 1):
        ms = date(today.year, m, 1)
        me = (date(today.year, m + 1, 1) - timedelta(days=1) if m < 12
              else date(today.year, 12, 31))
        s = db.get_summary(ms, me)
        months_labels.append(f"{m}月")
        incomes.append(s.total_income)
        expenses.append(s.total_expense)

    if months_labels and any(v > 0 for v in incomes + expenses):
        fig = _cute_line_chart(months_labels, incomes, expenses, size=(9.5, 3.8))
        img = _make_chart_image(fig, W - 10, int((W - 10) * 0.4))
        story.append(img)
        story.append(Spacer(1, 12))

    # --- Year personality ---
    pers_html = (
        f"🎭 年度消费人格<br/><br/>"
        f"　　{profile['emoji']} <b>{profile['title']}</b><br/>"
        f"　　{profile['desc']}<br/>"
        f"　　储蓄率 {sr:.1f}%，{'超过' if sr > 20 else '略低于'}全国平均水平"
    )
    story.append(_card_table(pers_html, Y_ACCENT, W))
    story.append(Spacer(1, 12))

    # --- Year ranking ---
    medals = ["🥇", "🥈", "🥉", "④", "⑤"]
    rank_html = "🏆 年度消费榜单<br/><br/>"
    for i, (name, val) in enumerate(cat_data[:5]):
        rank_html += f"　　{medals[i]} {name}: <b>¥{val:,.0f}</b><br/>"

    # biggest spending day
    bills = db.get_bills(start_date=year_start, end_date=today,
                         bill_type="expense", limit=500)
    day_total = {}
    for b in bills:
        dk = b.bill_date.isoformat() if hasattr(b.bill_date, "isoformat") else str(b.bill_date)
        day_total[dk] = day_total.get(dk, 0) + b.amount
    if day_total:
        max_day = max(day_total, key=day_total.get)
        rank_html += f"<br/>　　📅 年度最贵单日: {max_day}<br/>"
        rank_html += f"　　　　那天花了 <b>¥{day_total[max_day]:,.0f}</b> 😱"
    story.append(_card_table(rank_html, Y_ACCENT, W))
    story.append(Spacer(1, 12))

    # --- Fun facts ---
    facts = []
    if cat_data:
        top_cat = cat_data[0]
        if top_cat[0] == "餐饮" and top_cat[1] > 5000:
            meals = int(top_cat[1] / 35)
            facts.append(f"🍜 你今年吃掉了约 {meals} 顿饭，平均 ¥35/顿")
        if top_cat[0] == "交通" and top_cat[1] > 3000:
            facts.append(f"🚗 交通花了 ¥{top_cat[1]:,.0f}，够绕地球好几圈了")
        if monthly_avg > 1000:
            facts.append(f"💡 月均支出 ¥{monthly_avg:,.0f}，每天约 ¥{monthly_avg / 30:,.0f}")

    facts.append(f"📝 你已经坚持记账 {months_passed} 个月，真了不起！")

    if facts:
        story.append(_card_table("🎲 趣味数据<br/><br/>" + "<br/>".join(f"　　{f}" for f in facts),
                                 Y_ACCENT, W))
        story.append(Spacer(1, 12))

    # --- Keywords ---
    kw_pool = ["精致", "自律", "烟火气", "成长", "从容", "热情", "自由",
               "积累", "探索", "温暖", "突破", "理性", "平衡", "极简"]
    kws = random.sample(kw_pool, min(3, len(kw_pool)))
    kw_html = f"💎 {today.year} 年度关键词<br/><br/>　　「{'」  「'.join(kws)}」"
    story.append(_card_table(kw_html, Y_ACCENT, W))
    story.append(Spacer(1, 12))

    # --- New year advice ---
    advice = profile["suggestion"]
    top_cat = cat_data[0] if cat_data else ("未分类", 0)
    total_exp = sum(v for _, v in cat_data) if cat_data else 0
    top_pct = round(top_cat[1] / total_exp * 100) if total_exp > 0 else 0
    if top_pct > 35:
        advice += f"\n\n{top_cat[0]}占比达 {top_pct}%，可以适当控制一下哦～"
    story.append(_card_table(f"📝 新年理财Tips<br/><br/>{advice}", Y_ACCENT, W))
    story.append(Spacer(1, 8))
    story.append(Paragraph("记账本 · 用心记录你的每一年 💙", ss["SMALL"]))

    doc.build(story)
