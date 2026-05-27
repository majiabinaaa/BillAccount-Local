"""记账本 - 个人财务管理应用"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _run_export():
    """Minimal subprocess entry for report export. Called via:
       python main.py --export <weekly|monthly|yearly> <output.png> <db_path> [date_params...]

    Date parameters:
       weekly: [target_date] (YYYY-MM-DD, defaults to today)
       monthly: [year] [month] (defaults to current year/month)
       yearly: [year] (defaults to current year)
    """
    import matplotlib
    matplotlib.use("Agg")

    if len(sys.argv) < 5:
        sys.exit(3)

    report_type = sys.argv[2]
    output_path = sys.argv[3]
    db_path = sys.argv[4]

    from datetime import date as date_cls
    from core.database import Database
    from core.report_renderer import (
        generate_weekly_report_png,
        generate_monthly_report_png,
        generate_yearly_report_png,
    )

    db = Database(db_path)

    try:
        if report_type == "weekly":
            target_date = None
            if len(sys.argv) >= 6:
                target_date = date_cls.fromisoformat(sys.argv[5])
            generate_weekly_report_png(db, output_path, folder=None, target_date=target_date)

        elif report_type == "monthly":
            year, month = None, None
            if len(sys.argv) >= 7:
                year = int(sys.argv[5])
                month = int(sys.argv[6])
            elif len(sys.argv) >= 6:
                year = int(sys.argv[5])
            generate_monthly_report_png(db, output_path, folder=None, year=year, month=month)

        elif report_type == "yearly":
            year = None
            if len(sys.argv) >= 6:
                year = int(sys.argv[5])
            generate_yearly_report_png(db, output_path, folder=None, year=year)

        else:
            sys.exit(3)
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(2)
    finally:
        import matplotlib.pyplot as plt
        plt.close("all")
        db.close()
        # Force garbage collection to release PIL/matplotlib objects before exit
        import gc
        gc.collect()

    sys.exit(0)


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--export":
        _run_export()
        return

    from PySide6.QtWidgets import QApplication
    from ui.app import App

    qt_app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(qt_app.exec())


if __name__ == "__main__":
    main()
