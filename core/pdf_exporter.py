"""Beautiful personalized PDF reports: weekly / monthly / yearly."""
import io
import os
from datetime import date, timedelta
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, Image, PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from core.analytics import calculate_health_score, get_consumer_profile
from core.report_generator import generate_weekly_report

# ==================== Font Setup ====================

_FONT_REGISTERED = False


def _register_fonts():
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont("CJK", fp))
                pdfmetrics.registerFont(TTFont("CJKBold", fp, subfontIndex=1)
                                        if fp.endswith(".ttc") else TTFont("CJKBold", fp))
                _FONT_REGISTERED = True
                return
            except Exception:
                continue
    # fallback: use Helvetica (no CJK but won't crash)
    _FONT_REGISTERED = True


# ==================== Color Schemes ====================

WEEKLY_COLORS = {
    "bg": colors.HexColor("#FFF8E1"),
    "header": colors.HexColor("#FF6F00"),
    "accent": colors.HexColor("#FFB300"),
    "text": colors.HexColor("#3E2723"),
    "card": colors.HexColor("#FFFFFF"),
    "light": colors.HexColor("#FFECB3"),
}

MONTHLY_COLORS = {
    "bg": colors.HexColor("#E8F5E9"),
    "header": colors.HexColor("#2E7D32"),
    "accent": colors.HexColor("#66BB6A"),
    "text": colors.HexColor("#1B5E20"),
    "card": colors.HexColor("#FFFFFF"),
    "light": colors.HexColor("#C8E6C9"),
}

YEARLY_COLORS = {
    "bg": colors.HexColor("#E3F2FD"),
    "header": colors.HexColor("#1565C0"),
    "accent": colors.HexColor("#42A5F5"),
    "text": colors.HexColor("#0D47A1"),
    "card": colors.HexColor("#FFFFFF"),
    "light": colors.HexColor("#BBDEFB"),
}

_QUOTES = [
    "每一笔记账，都是对未来的投资。",
    "管住钱，就是管住人生。",
    "你不理财，财不理你。",
    "记账不是限制，是自由。",
    "清楚每一分钱的去向，才能掌控生活的方向。",
    "小账本，大智慧。",
    "财富积累，从记录开始。",
    "今天的节约，是明天的底气。",
]

_KEYWORDS_POOL = [
    "精致", "极简", "烟火气", "自律", "旅行", "成长",
    "品质", "探索", "温暖", "充实", "专注", "平衡",
    "积累", "突破", "从容", "热情", "理性", "自由",
]


# ==================== Chart Helpers ====================

def _make_pie_chart(data: list, size=(5, 4)) -> io.BytesIO:
    """Generate a pie chart image, return BytesIO."""
    matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    matplotlib.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=size, dpi=120)
    labels = [d[0] for d in data]
    values = [d[1] for d in data]
    pie_colors = ["#EF5350", "#FF7043", "#FFA726", "#FFCA28", "#66BB6A",
                  "#26C6DA", "#42A5F5", "#7E57C2"]

    wedges, _, autotexts = ax.pie(
        values, labels=None, autopct="%1.1f%%",
        colors=pie_colors[:len(data)],
        startangle=90, pctdistance=0.6,
        textprops={"fontsize": 12, "color": "white", "fontweight": "bold"},
    )
    ax.legend(wedges, [f"{l} ¥{v:,.0f}" for l, v in zip(labels, values)],
              loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10,
              title="支出分类", title_fontsize=11)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def _make_line_chart(months: list, incomes: list, expenses: list, size=(8, 3.5)) -> io.BytesIO:
    matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    matplotlib.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=size, dpi=120)
    ax.plot(months, incomes, "o-", color="#4CAF50", label="收入", linewidth=2, markersize=6)
    ax.plot(months, expenses, "o-", color="#F44336", label="支出", linewidth=2, markersize=6)
    ax.fill_between(range(len(months)), incomes, alpha=0.08, color="#4CAF50")
    ax.fill_between(range(len(months)), expenses, alpha=0.08, color="#F44336")
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(months, fontsize=10, rotation=30)
    ax.legend(fontsize=11, loc="upper left")
    ax.set_ylabel("金额 (元)", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


# ==================== Style Helpers ====================

def _get_styles():
    styles = getSampleStyleSheet()
    _register_fonts()
    font_name = "CJK" if _FONT_REGISTERED else "Helvetica"
    bold_name = "CJKBold" if _FONT_REGISTERED else "Helvetica-Bold"

    styles.add(ParagraphStyle(
        "CTitle", fontName=bold_name, fontSize=24, leading=32,
        alignment=TA_CENTER, textColor=colors.white,
    ))
    styles.add(ParagraphStyle(
        "CSubtitle", fontName=font_name, fontSize=11, leading=16,
        alignment=TA_CENTER, textColor=colors.white,
    ))
    styles.add(ParagraphStyle(
        "CSection", fontName=bold_name, fontSize=15, leading=22,
        textColor=colors.HexColor("#333333"), spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "CBody", fontName=font_name, fontSize=11, leading=18,
        textColor=colors.HexColor("#444444"),
    ))
    styles.add(ParagraphStyle(
        "CBig", fontName=bold_name, fontSize=28, leading=36,
        textColor=colors.HexColor("#333333"),
    ))
    styles.add(ParagraphStyle(
        "CNote", fontName=font_name, fontSize=10, leading=15,
        textColor=colors.HexColor("#777777"), alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "CQuote", fontName=font_name, fontSize=11, leading=18,
        textColor=colors.HexColor("#555555"), alignment=TA_CENTER,
    ))
    return styles


def _header_table(title: str, subtitle: str, color_scheme: dict) -> Table:
    """Generate a colored header block."""
    data = [[
        Table([[title]], colWidths=[460], rowHeights=[50]),
    ], [
        Table([[subtitle]], colWidths=[460], rowHeights=[20]),
    ]]
    t = Table(data, colWidths=[480])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color_scheme["header"]),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


def _card(content: str, color_scheme: dict, width: int = 460) -> Table:
    """White card with shadow effect (using border)."""
    styles = _get_styles()
    data = [[Paragraph(content, styles["CBody"])]]
    t = Table(data, colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color_scheme["card"]),
        ("BOX", (0, 0), (-1, -1), 0.5, color_scheme["light"]),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
    ]))
    return t


# ==================================================================
#   WEEKLY PDF — 本周消费手帐
# ==================================================================

def generate_weekly_pdf(db, filepath: str):
    _register_fonts()
    font_name = "CJK" if _FONT_REGISTERED else "Helvetica"
    bold_name = "CJKBold" if _FONT_REGISTERED else "Helvetica-Bold"
    cs = WEEKLY_COLORS
    styles = _get_styles()
    report = generate_weekly_report(db, 0)

    doc = SimpleDocTemplate(filepath, pagesize=A5,  # 420 x 595 pt
                            leftMargin=20, rightMargin=20,
                            topMargin=15, bottomMargin=15)
    story = []

    # --- Header ---
    week_label = report["week_label"] if report else f"{date.today().month}/{date.today().day}"
    header_data = [[
        Paragraph(f"🌟 MY WEEK IN MONEY", styles["CTitle"]),
    ], [
        Paragraph(week_label, styles["CSubtitle"]),
    ]]
    ht = Table(header_data, colWidths=[380])
    ht.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), cs["header"]),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
    ]))
    story.append(ht)
    story.append(Spacer(1, 12))

    if not report:
        story.append(Paragraph("本周暂无记账数据，快去记一笔吧！", styles["CBody"]))
        doc.build(story)
        return

    # --- Summary cards ---
    summary_html = (
        f"💰 总收入　<b>¥{report['total_income']:,.0f}</b><br/>"
        f"💸 总支出　<b>¥{report['total_expense']:,.0f}</b><br/>"
        f"🏦 结　　余　<b>{'+' if report['balance'] >= 0 else '-'}¥{abs(report['balance']):,.0f}</b><br/>"
        f"📊 储蓄率　<b>{report['savings_rate']:.1f}%</b>"
    )
    story.append(_card(summary_html, cs))
    story.append(Spacer(1, 10))

    # --- Pie chart ---
    cat_data = db.get_category_summary(
        report["week_start"], report["week_end"], "expense")
    if cat_data:
        buf = _make_pie_chart(cat_data, size=(4.5, 3.2))
        img = Image(buf, width=360, height=256)
        story.append(img)
        story.append(Spacer(1, 10))

    # --- Personality ---
    profile = get_consumer_profile(db)
    personality_html = (
        f"🎭 本周人格<br/>"
        f"　　<b>{profile['emoji']} {profile['title']}</b><br/>"
        f"　　{profile['desc'][:80]}..."
    )
    story.append(_card(personality_html, cs))
    story.append(Spacer(1, 10))

    # --- Achievements ---
    achievements = []
    if report["record_days"] == report["checked_days"]:
        achievements.append(f"⭐ 连续记账 {report['record_days']} 天")
    if report["savings_rate"] > 50:
        achievements.append(f"⭐ 储蓄率 > 50%")
    if report["balance"] < 0:
        achievements.append("⚠️ 入不敷出，下周加油")

    for t in report.get("trends", [])[:3]:
        if t["direction"] == "down":
            achievements.append(f"⭐ {t['category']}支出 ↓{t['change_pct']}%")

    if achievements:
        ach_html = "🏆 本周成就<br/>" + "<br/>".join(f"　　{a}" for a in achievements)
        story.append(_card(ach_html, cs))
        story.append(Spacer(1, 10))

    # --- Quote ---
    import random
    quote = random.choice(_QUOTES)
    story.append(_card(f"💬<br/>「{quote}」", cs))
    story.append(Spacer(1, 8))

    # --- Footer ---
    story.append(Paragraph("记账本 · 用心记录每一笔", styles["CNote"]))

    doc.build(story)


# ==================================================================
#   MONTHLY PDF — 月度财务护照
# ==================================================================

def generate_monthly_pdf(db, filepath: str):
    _register_fonts()
    font_name = "CJK" if _FONT_REGISTERED else "Helvetica"
    bold_name = "CJKBold" if _FONT_REGISTERED else "Helvetica-Bold"
    cs = MONTHLY_COLORS
    styles = _get_styles()

    today = date.today()
    month_start = today.replace(day=1)
    if today.month == 12:
        month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    ms = db.get_summary(month_start, month_end)
    health = calculate_health_score(db)
    profile = get_consumer_profile(db)

    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            leftMargin=25, rightMargin=25,
                            topMargin=20, bottomMargin=20)
    story = []

    # --- Header (passport style) ---
    import locale
    try:
        locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
    except Exception:
        pass
    month_name_en = today.strftime("%B").upper()
    month_name_cn = f"{today.year}年{today.month}月"

    header_data = [[
        Paragraph(f"FINANCIAL PASSPORT", styles["CTitle"]),
    ], [
        Paragraph(f"{month_name_en}  ·  {month_name_cn}", styles["CSubtitle"]),
    ]]
    ht = Table(header_data, colWidths=[545])
    ht.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), cs["header"]),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 22),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 22),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
    ]))
    story.append(ht)
    story.append(Spacer(1, 14))

    # --- Month summary ---
    summary_html = (
        f"📊 月度回顾<br/><br/>"
        f"总收入　<b>¥{ms.total_income:,.0f}</b><br/>"
        f"总支出　<b>¥{ms.total_expense:,.0f}</b><br/>"
        f"结　　余　<b>{'+' if ms.balance >= 0 else '-'}¥{abs(ms.balance):,.0f}</b><br/>"
        f"储蓄率　<b>{(ms.balance / ms.total_income * 100) if ms.total_income > 0 else 0:.1f}%</b>"
    )
    story.append(_card(summary_html, cs))
    story.append(Spacer(1, 10))

    # --- Pie chart ---
    cat_data = db.get_category_summary(month_start, month_end, "expense")
    if cat_data:
        buf = _make_pie_chart(cat_data, size=(5.5, 3.5))
        img = Image(buf, width=430, height=274)
        story.append(img)
        story.append(Spacer(1, 10))

    # --- Personality ---
    personality_html = (
        f"🎭 本月人格<br/>"
        f"　　<b>{profile['emoji']} {profile['title']}</b><br/>"
        f"　　{profile['desc']}"
    )
    story.append(_card(personality_html, cs))
    story.append(Spacer(1, 10))

    # --- Month's best ---
    bills = db.get_bills(start_date=month_start, end_date=month_end, bill_type="expense",
                         limit=200)
    biggest_expense = None
    day_totals = {}
    for b in bills:
        if biggest_expense is None or b.amount > biggest_expense.amount:
            biggest_expense = b
        day_key = b.bill_date.isoformat() if hasattr(b.bill_date, "isoformat") else str(b.bill_date)
        day_totals[day_key] = day_totals.get(day_key, 0) + b.amount

    cheapest_day = min(day_totals.items(), key=lambda x: x[1]) if day_totals else ("-", 0)

    # best category (biggest drop vs target)
    best_html = "🏅 月度之最<br/>"
    if biggest_expense:
        best_html += (
            f"　　🥇 最大开销: {biggest_expense.category_name or '未分类'} "
            f"¥{biggest_expense.amount:,.0f}<br/>"
        )
    if cheapest_day[1] > 0:
        best_html += f"　　🥈 最省日: {cheapest_day[0]} 仅 ¥{cheapest_day[1]:,.0f}<br/>"
    best_html += f"　　🥉 财务健康评分: {health['score']}/100 · {health['label']}"
    story.append(_card(best_html, cs))
    story.append(Spacer(1, 10))

    # --- Projection ---
    daily_avg = ms.total_expense / max((today - month_start).days, 1)
    projected = daily_avg * ((month_end - month_start).days + 1)
    proj_html = (
        f"📈 下月预测<br/><br/>"
        f"按当前日均支出 ¥{daily_avg:,.0f} 推算，<br/>"
        f"下月预计支出 <b>¥{projected:,.0f}</b>"
    )
    story.append(_card(proj_html, cs))
    story.append(Spacer(1, 10))

    # --- Advice ---
    story.append(_card(f"💡 理财小建议<br/><br/>{profile['suggestion']}", cs))
    story.append(Spacer(1, 10))
    story.append(Paragraph("记账本 · 用心记录每一笔", styles["CNote"]))

    doc.build(story)


# ==================================================================
#   YEARLY PDF — 年度财务故事
# ==================================================================

def generate_yearly_pdf(db, filepath: str):
    _register_fonts()
    font_name = "CJK" if _FONT_REGISTERED else "Helvetica"
    bold_name = "CJKBold" if _FONT_REGISTERED else "Helvetica-Bold"
    cs = YEARLY_COLORS
    styles = _get_styles()

    today = date.today()
    year_start = date(today.year, 1, 1)
    year_end = date(today.year, 12, 31)

    ys = db.get_summary(year_start, min(year_end, today))
    health = calculate_health_score(db)
    profile = get_consumer_profile(db)

    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            leftMargin=25, rightMargin=25,
                            topMargin=20, bottomMargin=20)
    story = []

    # --- Hero cover ---
    cover_data = [[
        Paragraph(f"{today.year}", styles["CBig"]),
    ], [
        Paragraph("MY MONEY STORY", styles["CTitle"]),
    ], [
        Paragraph("记账本 荣誉出品", styles["CSubtitle"]),
    ]]
    ct = Table(cover_data, colWidths=[545])
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), cs["header"]),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 30),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 30),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
    ]))
    story.append(ct)
    story.append(Spacer(1, 14))

    # --- Year stats ---
    months_passed = today.month
    monthly_avg = ys.total_expense / max(months_passed, 1)
    stats_html = (
        f"📊 年度数据<br/><br/>"
        f"总收入　<b>¥{ys.total_income:,.0f}</b><br/>"
        f"总支出　<b>¥{ys.total_expense:,.0f}</b><br/>"
        f"净储蓄　<b>¥{ys.balance:,.0f}</b><br/>"
        f"月均支出 <b>¥{monthly_avg:,.0f}</b>"
    )
    story.append(_card(stats_html, cs))
    story.append(Spacer(1, 10))

    # --- Monthly trend chart ---
    months_labels, incomes, expenses = [], [], []
    for m in range(1, today.month + 1):
        ms = date(today.year, m, 1)
        if m == 12:
            me = date(today.year, 12, 31)
        else:
            me = date(today.year, m + 1, 1) - timedelta(days=1)
        s = db.get_summary(ms, me)
        months_labels.append(f"{m}月")
        incomes.append(s.total_income)
        expenses.append(s.total_expense)

    if months_labels:
        buf = _make_line_chart(months_labels, incomes, expenses)
        img = Image(buf, width=480, height=210)
        story.append(img)
        story.append(Spacer(1, 10))

    # --- Year personality ---
    personality_html = (
        f"🎭 年度消费人格<br/>"
        f"　　<b>{profile['emoji']} {profile['title']}</b><br/>"
        f"　　{profile['desc']}<br/>"
        f"　　储蓄率 {profile['savings_rate']}%，"
        f"{'超过' if profile['savings_rate'] > 20 else '低于'}全国平均"
    )
    story.append(_card(personality_html, cs))
    story.append(Spacer(1, 10))

    # --- Year ranking ---
    cat_data = db.get_category_summary(year_start, today, "expense")
    ranking_html = "🏆 年度榜单<br/>"
    medals = ["🥇", "🥈", "🥉"]
    for i, (name, val) in enumerate(cat_data[:3]):
        ranking_html += f"　　{medals[i]} {name}: ¥{val:,.0f}<br/>"

    # find biggest spending day
    bills = db.get_bills(start_date=year_start, end_date=today, bill_type="expense",
                         limit=500)
    day_total = {}
    for b in bills:
        dk = b.bill_date.isoformat() if hasattr(b.bill_date, "isoformat") else str(b.bill_date)
        day_total[dk] = day_total.get(dk, 0) + b.amount
    if day_total:
        max_day = max(day_total, key=day_total.get)
        ranking_html += f"　　📅 最贵单日: {max_day} (¥{day_total[max_day]:,.0f})"
    story.append(_card(ranking_html, cs))
    story.append(Spacer(1, 10))

    # --- Keywords ---
    import random
    keywords = random.sample(_KEYWORDS_POOL, 3)
    kw_html = f"💎 年度关键词<br/><br/>　　「{'」  「'.join(keywords)}」"
    story.append(_card(kw_html, cs))
    story.append(Spacer(1, 10))

    # --- New year advice ---
    top_cat = cat_data[0] if cat_data else ("未分类", 0)
    total_exp = sum(v for _, v in cat_data)
    top_pct = round(top_cat[1] / total_exp * 100) if total_exp > 0 else 0
    advice = profile["suggestion"]
    if top_pct > 30:
        advice += f"\n\n{top_cat[0]}占比达 {top_pct}%，略高。建议设定月预算 ¥{top_cat[1] / max(months_passed, 1) * 0.8:,.0f}。"
    story.append(_card(f"📝 新年理财建议<br/><br/>{advice}", cs))
    story.append(Spacer(1, 10))

    story.append(Paragraph("记账本 · 用心记录每一笔", styles["CNote"]))

    doc.build(story)
