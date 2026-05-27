"""Character-driven storybook PNG reports — weekly / monthly / yearly.

Thin wrapper around core.report_renderer. Preserves the original API
(generate_weekly_pdf, generate_monthly_pdf, generate_yearly_pdf) for
backward compatibility with export_page.py.
"""
from core.report_renderer import (
    generate_weekly_report_png,
    generate_monthly_report_png,
    generate_yearly_report_png,
)


def generate_weekly_pdf(db, filepath: str, folder=None):
    """Generate weekly spending diary PNG. folder: 'starrail01'|'ww01'|'ww02'|None=random"""
    return generate_weekly_report_png(db, filepath, folder=folder)


def generate_monthly_pdf(db, filepath: str, folder=None):
    """Generate monthly life report PNG (2 pages stacked)."""
    return generate_monthly_report_png(db, filepath, folder=folder)


def generate_yearly_pdf(db, filepath: str, folder=None):
    """Generate yearly memoir PNG (3 pages stacked)."""
    return generate_yearly_report_png(db, filepath, folder=folder)
