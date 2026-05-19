"""Beautiful personalized PDF reports with local assets — weekly / monthly / yearly."""
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
                                 TableStyle, Image, PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.graphics.shapes import Drawing, Rect, Circle, Line, String
from reportlab.lib.colors import HexColor

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from core.analytics import get_consumer_profile
from core.report_generator import generate_weekly_report

# ==================== Asset Paths ====================
_ASSETS = Path(__file__).parent.parent / "assets"


def _asset(name: str) -> str:
    """Get full path to an asset file, or return empty string if missing."""
    p = _ASSETS / name
    return str(p) if p.exists() else ""


# ==================== Font Setup (fixed: no more squares) ====================

_FONT_OK = False


def _setup_fonts():
    global _FONT_OK
    if _FONT_OK:
        return

    # Find a CJK font file
    font_path = None
    for fp in ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf",
               "C:/Windows/Fonts/simsun.ttc", "C:/Windows/Fonts/msyhbd.ttc"]:
        if os.path.exists(fp):
            font_path = fp
            break

    if font_path is None:
        return

    try:
        pdfmetrics.registerFont(TTFont("CJK", font_path))
        # Register bold variant too — try subfont 1 for .ttc, or same file
        try:
            pdfmetrics.registerFont(TTFont("CJKB", font_path, subfontIndex=1)
                                    if font_path.endswith(".ttc")
                                    else TTFont("CJKB", font_path))
        except Exception:
            pdfmetrics.registerFont(TTFont("CJKB", font_path))  # fallback: same as regular

        # CRITICAL: map all style variants to CJK fonts to prevent squares from <b>/<i>
        registerFontFamily("CJK", normal="CJK", bold="CJKB", italic="CJK", boldItalic="CJKB")
        _FONT_OK = True
    except Exception:
        pass


_setup_fonts()
F = "CJK" if _FONT_OK else "Helvetica"
FB = "CJKB" if _FONT_OK else "Helvetica-Bold"

# ==================== Colors ====================

# Weekly — warm peach/coral
W_MAIN = HexColor("#FF7043")
W_LIGHT = HexColor("#FFF3E0")
W_BG = HexColor("#FFF9F5")
W_DARK = HexColor("#BF360C")

# Monthly — fresh green
M_MAIN = HexColor("#43A047")
M_LIGHT = HexColor("#E8F5E9")
M_BG = HexColor("#F5FBF5")
M_DARK = HexColor("#1B5E20")

# Yearly — dreamy blue
Y_MAIN = HexColor("#1E88E5")
Y_LIGHT = HexColor("#E3F2FD")
Y_BG = HexColor("#F5F9FD")
Y_DARK = HexColor("#0D47A1")

# ==================== Chart Helpers ====================

def _pie_chart_png(data: list, size=(5, 4)) -> io.BytesIO:
    """Generate a styled pie chart as PNG bytes."""
    matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    matplotlib.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=size, dpi=150)
    labels = [d[0] for d in data]
    values = [d[1] for d in data]
    pie_colors = ["#EF5350", "#FF7043", "#FFA726", "#FFCA28", "#66BB6A",
                  "#26C6DA", "#42A5F5", "#7E57C2", "#EC407A", "#8D6E63"]

    wedges, _, autotexts = ax.pie(
        values, labels=None, autopct="%1.1f%%",
        colors=pie_colors[:len(data)],
        startangle=140, pctdistance=0.62,
        textprops={"fontsize": 13, "color": "white", "fontweight": "bold"},
        wedgeprops={"linewidth": 2, "edgecolor": "white"},
    )
    ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
              fontsize=11, title="支出分类", title_fontsize=13, framealpha=0.5)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf


def _line_chart_png(months, incomes, expenses, size=(9, 3.5)) -> io.BytesIO:
    matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    matplotlib.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=size, dpi=150)
    x = range(len(months))
    ax.plot(x, incomes, "o-", color="#66BB6A", label="收入", linewidth=2.5, markersize=8,
            markeredgecolor="white", markeredgewidth=1.5)
    ax.plot(x, expenses, "o-", color="#EF5350", label="支出", linewidth=2.5, markersize=8,
            markeredgecolor="white", markeredgewidth=1.5)
    ax.fill_between(x, incomes, alpha=0.06, color="#66BB6A")
    ax.fill_between(x, expenses, alpha=0.06, color="#EF5350")
    ax.set_xticks(x)
    ax.set_xticklabels(months, fontsize=11, rotation=0)
    ax.legend(fontsize=13, loc="upper left", framealpha=0.8)
    ax.grid(axis="y", alpha=0.2, color="#BDBDBD")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf


def _mini_image(name: str, w: int, h: int) -> Image | Spacer:
    """Return an Image or Spacer if asset not found."""
    path = _asset(name)
    if path:
        return Image(path, width=w, height=h)
    return Spacer(w, h)


# ==================== Style Helpers ====================

def _styles():
    from reportlab.lib.styles import getSampleStyleSheet
    base = getSampleStyleSheet()

    base.add(ParagraphStyle("hero", fontName=FB, fontSize=36, leading=44,
                            textColor=colors.white, alignment=TA_CENTER))
    base.add(ParagraphStyle("hero_sub", fontName=F, fontSize=14, leading=20,
                            textColor=HexColor("#FFFFFFBB"), alignment=TA_CENTER))
    base.add(ParagraphStyle("section_title", fontName=FB, fontSize=18, leading=26,
                            textColor=colors.HexColor("#333333")))
    base.add(ParagraphStyle("big_number", fontName=FB, fontSize=32, leading=40,
                            textColor=colors.HexColor("#333333"), alignment=TA_CENTER))
    base.add(ParagraphStyle("body_text", fontName=F, fontSize=12, leading=20,
                            textColor=colors.HexColor("#444444")))
    base.add(ParagraphStyle("body_center", fontName=F, fontSize=12, leading=20,
                            textColor=colors.HexColor("#444444"), alignment=TA_CENTER))
    base.add(ParagraphStyle("caption", fontName=F, fontSize=9, leading=14,
                            textColor=colors.HexColor("#999999"), alignment=TA_CENTER))
    base.add(ParagraphStyle("footer", fontName=F, fontSize=8, leading=12,
                            textColor=colors.HexColor("#BBBBBB"), alignment=TA_CENTER))
    base.add(ParagraphStyle("tag", fontName=FB, fontSize=10, leading=14,
                            textColor=colors.white))
    return base


def _colored_section(content: list, bg_color, width: int, padding: int = 20) -> Table:
    """Wrap a list of flowables in a full-width colored background section."""
    # content is a list of Paragraph/Image/Spacer
    data = [[c] for c in content]
    t = Table(data, colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg_color),
        ("LEFTPADDING", (0, 0), (-1, -1), padding),
        ("RIGHTPADDING", (0, 0), (-1, -1), padding),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def _hero_section(text_lines: list, bg_color, accent_color, w: int, h: int = 120) -> Table:
    """Large colored hero/cover section with multiple lines of text."""
    ss = _styles()
    rows = [[Paragraph(line[0], ss[line[1]])] for line in text_lines]
    t = Table(rows, colWidths=[w])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg_color),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 24),
        ("RIGHTPADDING", (0, 0), (-1, -1), 24),
    ]))
    return t


# ==================================================================
#   WEEKLY — 500x500pt social card
# ==================================================================

def generate_weekly_pdf(db, filepath: str):
    _setup_fonts()
    ss = _styles()
    report = generate_weekly_report(db, 0)

    W, H = 500, 500
    doc = SimpleDocTemplate(filepath, pagesize=(W, H),
                            leftMargin=20, rightMargin=20,
                            topMargin=16, bottomMargin=16)
    story = []

    usable_w = W - 40

    # ---- Hero header ----
    week_label = report["week_label"] if report else date.today().isoformat()
    story.append(_hero_section([
        ("🌟 一周消费手帐", "hero"),
        (week_label, "hero_sub"),
    ], W_MAIN, W_LIGHT, usable_w))
    story.append(Spacer(1, 12))

    if not report or (report["total_income"] == 0 and report["total_expense"] == 0):
        story.append(Paragraph("这周还没有记账呢～<br/>打开App记下第一笔吧！", ss["body_center"]))
        story.append(Spacer(1, 16))
        doc.build(story)
        return

    # ---- Big numbers row ----
    bal = report["balance"]
    sr = report["savings_rate"]
    sign = "+" if bal >= 0 else "-"
    body = (
        f"💰 收入 <font color='#2E7D32'><b>¥{report['total_income']:,.0f}</b></font>　　"
        f"💸 支出 <font color='#C62828'><b>¥{report['total_expense']:,.0f}</b></font><br/>"
        f"🏦 结余 <b>{sign}¥{abs(bal):,.0f}</b>　　储蓄率 <b>{sr:.1f}%</b>"
    )
    story.append(Paragraph(body, ss["body_center"]))
    story.append(Spacer(1, 10))

    # ---- Pie chart ----
    cat_data = db.get_category_summary(report["week_start"], report["week_end"], "expense")
    if cat_data and sum(v for _, v in cat_data) > 0:
        buf = _pie_chart_png(cat_data, size=(5, 3.6))
        story.append(Image(buf, width=usable_w - 20, height=int((usable_w - 20) * 0.7)))
        story.append(Spacer(1, 10))

    # ---- Top spending categories ----
    if cat_data:
        total_exp = sum(v for _, v in cat_data)
        lines = ["<b>💰 钱去哪了？</b>"]
        emojis = ["🍜", "🚗", "🛍", "🏠", "🎬", "💊", "📚", "📱", "✨"]
        for i, (name, val) in enumerate(cat_data[:5]):
            pct = val / total_exp * 100 if total_exp > 0 else 0
            bar_w = int(pct / 100 * 22)
            bar = "▌" * bar_w + "·" * (22 - bar_w)
            lines.append(f"{emojis[i % 9]} {name}  {bar}  {pct:.0f}%")
        story.append(Paragraph("<br/>".join(lines), ss["body_text"]))
        story.append(Spacer(1, 10))

    # ---- Personality + achievements ----
    profile = get_consumer_profile(db)
    pers = f"🎭 这周你是 <b>{profile['emoji']}「{profile['title']}」</b><br/>　　{profile['desc'][:72]}..."
    story.append(Paragraph(pers, ss["body_text"]))
    story.append(Spacer(1, 8))

    # achievements
    ach = []
    if report["record_days"] == report["checked_days"]:
        ach.append(f"🌟 连续记账 {report['record_days']} 天")
    if sr > 40:
        ach.append(f"💎 储蓄率超过 80% 的人")
    for t in report.get("trends", [])[:2]:
        if t["direction"] == "down":
            ach.append(f"📉 {t['category']}比上周少 {t['change_pct']}%")
    if ach:
        story.append(Paragraph("　　" + "　".join(ach), ss["body_text"]))
        story.append(Spacer(1, 8))

    # ---- Quote footer ----
    quotes = [
        "「花得明白，存得踏实」",
        "「今天的节约，是明天的浪漫」",
        "「每一笔记账，都是对未来的温柔」",
    ]
    story.append(Paragraph(random.choice(quotes), ss["body_center"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph("记账本 · 用心记录每一笔", ss["caption"]))

    doc.build(story)


# ==================================================================
#   MONTHLY — A5 passport (420x595pt)
# ==================================================================

def generate_monthly_pdf(db, filepath: str):
    _setup_fonts()
    ss = _styles()
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
                            leftMargin=18, rightMargin=18,
                            topMargin=16, bottomMargin=16)
    story = []
    uw = W - 36

    # ---- Cover ----
    story.append(_hero_section([
        ("FINANCIAL PASSPORT", "hero"),
        (f"{month_name} · {today.year}年{today.month}月", "hero_sub"),
    ], M_MAIN, M_LIGHT, uw))
    story.append(Spacer(1, 10))

    # ---- Month numbers ----
    sr = (ms.balance / ms.total_income * 100) if ms.total_income > 0 else 0
    stars = "★★★★★"[:int(sr / 20) + 1] + "☆☆☆☆☆"[int(sr / 20) + 1:]
    body = (
        f"💰 收入 <b>¥{ms.total_income:,.0f}</b>　　"
        f"💸 支出 <b>¥{ms.total_expense:,.0f}</b><br/>"
        f"🏦 结余 <b>{'+' if ms.balance >= 0 else '-'}¥{abs(ms.balance):,.0f}</b><br/>"
        f"📈 储蓄率 <b>{sr:.1f}%</b>　{stars}"
    )
    story.append(Paragraph(body, ss["body_center"]))
    story.append(Spacer(1, 10))

    # ---- Pie chart ----
    cat_data = db.get_category_summary(month_start, month_end, "expense")
    if cat_data and sum(v for _, v in cat_data) > 0:
        buf = _pie_chart_png(cat_data, size=(5, 3.5))
        story.append(Image(buf, width=uw - 10, height=int((uw - 10) * 0.7)))
        story.append(Spacer(1, 10))

    # ---- Personality ----
    pers = f"🎭 本月消费人格<br/>　　<b>{profile['emoji']} {profile['title']}</b><br/>　　{profile['desc']}"
    story.append(Paragraph(pers, ss["body_text"]))
    story.append(Spacer(1, 10))

    # ---- Best of month ----
    bills = db.get_bills(start_date=month_start, end_date=month_end,
                         bill_type="expense", limit=300)
    biggest = None
    day_spend = {}
    for b in bills:
        if biggest is None or b.amount > biggest.amount:
            biggest = b
        dk = b.bill_date.isoformat() if hasattr(b.bill_date, "isoformat") else str(b.bill_date)
        day_spend[dk] = day_spend.get(dk, 0) + b.amount

    best = ["<b>🏅 月度之最</b>"]
    if biggest:
        best.append(f"🥇 最大开销: {biggest.category_name or '未分类'} ¥{biggest.amount:,.0f}")
    if day_spend:
        cheap = min(day_spend.items(), key=lambda x: x[1])
        best.append(f"🥈 最省日: {cheap[0]} 仅 ¥{cheap[1]:,.0f}")
    if cat_data:
        best.append(f"🥉 支出TOP1: {cat_data[0][0]} ¥{cat_data[0][1]:,.0f}")
    story.append(Paragraph("<br/>".join(best), ss["body_text"]))
    story.append(Spacer(1, 10))

    # ---- Projection + advice ----
    days_passed = max((today - month_start).days, 1)
    daily_avg = ms.total_expense / days_passed
    projected = daily_avg * ((month_end - month_start).days + 1)
    story.append(Paragraph(
        f"📈 日均支出 ¥{daily_avg:,.0f}，预计下月 <b>¥{projected:,.0f}</b>", ss["body_text"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"💡 {profile['suggestion']}", ss["body_text"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph("记账本 · 用心记录每一笔", ss["caption"]))

    doc.build(story)


# ==================================================================
#   YEARLY — A4 storybook
# ==================================================================

def generate_yearly_pdf(db, filepath: str):
    _setup_fonts()
    ss = _styles()
    today = date.today()
    year_start = date(today.year, 1, 1)

    ys = db.get_summary(year_start, min(date(today.year, 12, 31), today))
    profile = get_consumer_profile(db)
    cat_data = db.get_category_summary(year_start, today, "expense")

    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            leftMargin=28, rightMargin=28,
                            topMargin=22, bottomMargin=22)
    story = []
    uw = A4[0] - 56

    # ---- Cover ----
    story.append(_hero_section([
        (str(today.year), "hero"),
        ("MY MONEY STORY", "hero"),
        ("年度财务回忆录", "hero_sub"),
    ], Y_MAIN, Y_LIGHT, uw))
    story.append(Spacer(1, 16))

    # ---- Year in numbers ----
    sr = (ys.balance / ys.total_income * 100) if ys.total_income > 0 else 0
    months_passed = today.month
    monthly_avg = ys.total_expense / max(months_passed, 1)

    body = (
        f"💰 总收入 <b>¥{ys.total_income:,.0f}</b>　　"
        f"💸 总支出 <b>¥{ys.total_expense:,.0f}</b><br/>"
        f"🏦 净储蓄 <b>¥{ys.balance:,.0f}</b>　　"
        f"📈 储蓄率 <b>{sr:.1f}%</b><br/>"
        f"📊 月均支出 <b>¥{monthly_avg:,.0f}</b>　已坚持记账 <b>{months_passed}</b> 个月"
    )
    story.append(Paragraph(body, ss["body_center"]))
    story.append(Spacer(1, 14))

    # ---- Monthly trend chart ----
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
        buf = _line_chart_png(months_labels, incomes, expenses, size=(9.5, 3.8))
        story.append(Image(buf, width=uw - 10, height=int((uw - 10) * 0.38)))
        story.append(Spacer(1, 14))

    # ---- Personality ----
    pers = (f"🎭 年度消费人格<br/>　　<b>{profile['emoji']} {profile['title']}</b><br/>"
            f"　　{profile['desc']}<br/>"
            f"　　储蓄率 {sr:.1f}%，{'超过' if sr > 20 else '略低于'}全国平均水平")
    story.append(Paragraph(pers, ss["body_text"]))
    story.append(Spacer(1, 14))

    # ---- Ranking ----
    medals = ["🥇", "🥈", "🥉", "④", "⑤"]
    rank = ["<b>🏆 年度消费榜单</b>"]
    for i, (name, val) in enumerate(cat_data[:5]):
        rank.append(f"{medals[i]} {name}: <b>¥{val:,.0f}</b>")

    bills = db.get_bills(start_date=year_start, end_date=today,
                         bill_type="expense", limit=500)
    day_total = {}
    for b in bills:
        dk = b.bill_date.isoformat() if hasattr(b.bill_date, "isoformat") else str(b.bill_date)
        day_total[dk] = day_total.get(dk, 0) + b.amount
    if day_total:
        max_day = max(day_total, key=day_total.get)
        rank.append(f"📅 年度最贵单日: {max_day} ¥{day_total[max_day]:,.0f}")

    story.append(Paragraph("<br/>".join(rank), ss["body_text"]))
    story.append(Spacer(1, 14))

    # ---- Fun facts ----
    facts = ["<b>🎲 趣味数据</b>"]
    if cat_data:
        tc = cat_data[0]
        if tc[0] == "餐饮" and tc[1] > 3000:
            facts.append(f"🍜 约吃了 {int(tc[1]/35)} 顿饭，平均 ¥35/顿")
        if tc[0] == "交通" and tc[1] > 2000:
            facts.append(f"🚗 交通花了 ¥{tc[1]:,.0f}，够绕城市好几圈")
    facts.append(f"📝 坚持记账 {months_passed} 个月，了不起！")
    story.append(Paragraph("<br/>".join(facts), ss["body_text"]))
    story.append(Spacer(1, 14))

    # ---- Keywords ----
    kw_pool = ["精致", "自律", "烟火气", "成长", "从容", "热情", "自由",
               "积累", "探索", "温暖", "突破", "理性", "平衡", "极简"]
    kws = random.sample(kw_pool, min(3, len(kw_pool)))
    story.append(Paragraph(
        f"💎 {today.year} 年度关键词<br/>　　「{'」  「'.join(kws)}」", ss["body_text"]))
    story.append(Spacer(1, 14))

    # ---- Advice ----
    advice = profile["suggestion"]
    top_cat = cat_data[0] if cat_data else ("", 0)
    total_exp = sum(v for _, v in cat_data) if cat_data else 0
    top_pct = round(top_cat[1] / total_exp * 100) if total_exp > 0 else 0
    if top_pct > 35:
        advice += f"\n{top_cat[0]}占比 {top_pct}%，可适当控制～"
    story.append(Paragraph(f"📝 新年理财Tips<br/>{advice}", ss["body_text"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph("记账本 · 用心记录你的每一年", ss["caption"]))

    doc.build(story)
