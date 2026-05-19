from datetime import date, datetime, timedelta
from typing import Tuple


def get_today_range() -> Tuple[date, date]:
    today = date.today()
    return today, today


def get_week_range() -> Tuple[date, date]:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def get_month_range() -> Tuple[date, date]:
    today = date.today()
    first_day = today.replace(day=1)
    if today.month == 12:
        last_day = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    return first_day, last_day


def get_year_range() -> Tuple[date, date]:
    today = date.today()
    first_day = today.replace(month=1, day=1)
    last_day = today.replace(month=12, day=31)
    return first_day, last_day


def get_date_range_label(period: str) -> Tuple[date, date]:
    periods = {
        "day": get_today_range,
        "week": get_week_range,
        "month": get_month_range,
        "year": get_year_range,
    }
    return periods.get(period, get_month_range)()


def get_weeks_in_month(year: int, month: int) -> list:
    """Return list of (monday, sunday) pairs for each week in a month."""
    first_day = date(year, month, 1)
    last_day = (first_day.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    # find the monday on or before the first day
    current = first_day - timedelta(days=first_day.weekday())
    weeks = []
    while current <= last_day:
        week_end = current + timedelta(days=6)
        weeks.append((max(current, first_day), min(week_end, last_day)))
        current += timedelta(days=7)
    return weeks


def get_months_in_year(year: int) -> list:
    """Return list of (first_day, last_day) pairs for each month in a year."""
    months = []
    for month in range(1, 13):
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year, 12, 31)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        months.append((first_day, last_day))
    return months


def format_date(d: date, fmt: str = "%Y-%m-%d") -> str:
    return d.strftime(fmt)


def format_period_label(period: str) -> str:
    today = date.today()
    if period == "day":
        return f"{today} (今日)"
    elif period == "week":
        monday, sunday = get_week_range()
        return f"{monday} ~ {sunday} (本周)"
    elif period == "month":
        return f"{today.year}年{today.month}月"
    elif period == "year":
        return f"{today.year}年"
    return ""
