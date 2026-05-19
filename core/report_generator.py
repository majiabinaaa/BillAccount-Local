"""Natural-language weekly financial report generation."""
from datetime import date, timedelta


def generate_weekly_report(db, week_offset: int = 0) -> dict | None:
    """
    Generate a weekly financial report.

    week_offset: 0 = current week, -1 = last week, -2 = two weeks ago, etc.

    Returns None if no data exists for the target week.
    """
    today = date.today()
    # Monday of the target week
    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    sunday = monday + timedelta(days=6)

    week_summary = db.get_summary(monday, sunday)
    if week_summary.total_income == 0 and week_summary.total_expense == 0:
        return None

    # ---- previous week for comparison ----
    prev_monday = monday - timedelta(days=7)
    prev_sunday = monday - timedelta(days=1)
    prev_summary = db.get_summary(prev_monday, prev_sunday)
    has_prev = not (prev_summary.total_income == 0 and prev_summary.total_expense == 0)

    # ---- savings rate ----
    income = week_summary.total_income
    expense = week_summary.total_expense
    balance = income - expense
    savings_rate = (balance / income * 100) if income > 0 else 0
    prev_savings_rate = ((prev_summary.total_income - prev_summary.total_expense)
                         / prev_summary.total_income * 100) if prev_summary.total_income > 0 else 0

    # ---- top category ----
    cat_data = db.get_category_summary(monday, sunday, "expense")
    top_cat = cat_data[0] if cat_data else ("未分类", 0)
    total_expense = sum(v for _, v in cat_data) if cat_data else 0
    top_cat_pct = round(top_cat[1] / total_expense * 100) if total_expense > 0 else 0

    # second top category
    second_cat = cat_data[1] if len(cat_data) > 1 else None
    second_cat_pct = (round(second_cat[1] / total_expense * 100)
                      if second_cat and total_expense > 0 else 0)

    # ---- biggest single bill ----
    bills = db.get_bills(start_date=monday, end_date=sunday, limit=200)
    biggest = None
    for b in bills:
        if b.type == "expense" and (biggest is None or b.amount > biggest.amount):
            biggest = b

    # ---- recording days ----
    record_days = 0
    for d in range(7):
        day = monday + timedelta(days=d)
        if day > today:
            break
        count = db.get_bill_count(start_date=day, end_date=day)
        if count > 0:
            record_days += 1
    checked_days = min(7, (today - monday).days + 1)

    # ---- trends vs last week ----
    trends = []
    if has_prev:
        prev_cat_data = db.get_category_summary(prev_monday, prev_sunday, "expense")
        prev_cat_map = {name: val for name, val in prev_cat_data}
        for name, val in cat_data:
            prev_val = prev_cat_map.get(name, 0)
            if prev_val > 0 and val > 50:  # both weeks have meaningful amounts
                change = round((val - prev_val) / prev_val * 100)
                if abs(change) > 15:
                    direction = "up" if change > 0 else "down"
                    trends.append({
                        "category": name,
                        "change_pct": abs(change),
                        "direction": direction,
                    })

    # ---- generate text ----
    report_text = _build_report_text(
        monday, sunday, income, expense, balance, savings_rate,
        prev_savings_rate, has_prev, top_cat, top_cat_pct,
        second_cat, second_cat_pct, biggest, trends,
        record_days, checked_days,
    )

    # ---- sentiment ----
    sentiment = "positive"
    if savings_rate < 0:
        sentiment = "warning"
    elif savings_rate < 15:
        sentiment = "neutral"
    elif trend_count := sum(1 for t in trends if t["direction"] == "up"):
        if trend_count >= 3:
            sentiment = "neutral"

    return {
        "week_start": monday,
        "week_end": min(sunday, today),
        "week_label": f"{monday.month}/{monday.day} - {min(sunday, today).month}/{min(sunday, today).day}",
        "report_text": report_text,
        "sentiment": sentiment,
        "total_income": income,
        "total_expense": expense,
        "balance": balance,
        "savings_rate": round(savings_rate, 1),
        "top_category": (top_cat[0], top_cat_pct),
        "biggest_bill": biggest,
        "record_days": record_days,
        "checked_days": checked_days,
        "trends": trends,
        "has_prev": has_prev,
    }


def _build_report_text(monday, sunday, income, expense, balance, savings_rate,
                       prev_sr, has_prev, top_cat, top_pct,
                       second_cat, second_pct, biggest, trends,
                       record_days, checked_days) -> str:
    lines = []
    lines.append(f"📅 本周财务周报（{monday.month}/{monday.day} - {sunday.month}/{sunday.day}）")
    lines.append("")

    # overview
    lines.append(f"总收入 ¥{income:,.0f}，支出 ¥{expense:,.0f}，结余 "
                 f"{'¥' + f'{balance:,.0f}' if balance >= 0 else '-¥' + f'{abs(balance):,.0f}'}。"
                 f"储蓄率 {savings_rate:.1f}%"
                 + (f"，比上周{'提升' if savings_rate > prev_sr else '下降'}了 {abs(savings_rate - prev_sr):.1f}%"
                    if has_prev else "")
                 + "。")
    lines.append("")

    # top categories
    if expense > 0:
        lines.append(f"支出中{top_cat[0]}占比最高({top_pct}%，¥{top_cat[1]:,.0f})"
                     + (f"，其次是{second_cat[0]}({second_pct}%，¥{second_cat[1]:,.0f})"
                        if second_cat and second_pct > 0 else "")
                     + "。"
                     + (f"最大一笔是{_weekday_name(biggest.bill_date)}的\"{biggest.description or biggest.category_name}\" ¥{biggest.amount:,.0f}。"
                        if biggest else "")
                     )
        lines.append("")

    # trends
    if trends:
        up_trends = [t for t in trends if t["direction"] == "up"]
        down_trends = [t for t in trends if t["direction"] == "down"]
        for t in up_trends:
            lines.append(f"{t['category']}支出比上周多了 {t['change_pct']}%，可以留意一下。")
        for t in down_trends[:3]:
            lines.append(f"{t['category']}支出比上周少了 {t['change_pct']}%，继续保持！")
        if up_trends or down_trends:
            lines.append("")

    # recording streak
    if checked_days > 0:
        if record_days == checked_days:
            lines.append(f"本周连续记账 {record_days} 天，满分！🏆")
        elif record_days >= 4:
            lines.append(f"本周记录了 {record_days}/{checked_days} 天，还不错。争取下周全勤！")
        else:
            lines.append(f"本周只记录了 {record_days}/{checked_days} 天，下周记得多加记录哦。")

    # advice
    if savings_rate < 0:
        lines.append("支出超过了收入，注意控制不必要的开支。")
    elif savings_rate > 60 and income > 0:
        lines.append("储蓄率非常优秀，可以考虑适当投资让钱生钱。")

    return "\n".join(lines)


_WEEKDAY_NAMES = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def _weekday_name(d: date) -> str:
    if isinstance(d, str):
        from datetime import datetime
        d = datetime.strptime(d[:10], "%Y-%m-%d").date()
    return _WEEKDAY_NAMES[d.weekday()]
