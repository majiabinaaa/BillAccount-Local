import sqlite3
import csv
import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

from core.models import Bill, Category, PeriodSummary
from utils.date_utils import get_date_range_label

DEFAULT_CATEGORIES = [
    # income
    ("工资", "income", 1),
    ("奖金", "income", 2),
    ("理财", "income", 3),
    ("兼职", "income", 4),
    ("其他收入", "income", 5),
    # expense
    ("餐饮", "expense", 1),
    ("交通", "expense", 2),
    ("购物", "expense", 3),
    ("住房", "expense", 4),
    ("娱乐", "expense", 5),
    ("医疗", "expense", 6),
    ("教育", "expense", 7),
    ("通讯", "expense", 8),
    ("其他支出", "expense", 9),
]


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn = None
        self.init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, timeout=30)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
            self._conn.execute("PRAGMA journal_mode = WAL")
            self._conn.execute("PRAGMA busy_timeout = 5000")
        return self._conn

    def _connect(self) -> sqlite3.Connection:
        """Create a standalone connection (for one-off use like init_db or export)."""
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA busy_timeout = 5000")
        return conn

    def close(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def init_db(self):
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                    sort_order INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS bills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL CHECK(amount > 0),
                    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                    category_id INTEGER,
                    description TEXT DEFAULT '',
                    bill_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                );

                CREATE INDEX IF NOT EXISTS idx_bills_date ON bills(bill_date);
                CREATE INDEX IF NOT EXISTS idx_bills_type ON bills(type);
            """)
            # insert default categories if table is empty
            count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
            if count == 0:
                for name, cat_type, sort_order in DEFAULT_CATEGORIES:
                    conn.execute(
                        "INSERT INTO categories (name, type, sort_order) VALUES (?, ?, ?)",
                        (name, cat_type, sort_order),
                    )

    # ---- Categories ----

    def get_categories(self, cat_type: str = None) -> List[Category]:
        conn = self._get_conn()
        if cat_type:
            rows = conn.execute(
                "SELECT * FROM categories WHERE type = ? ORDER BY sort_order",
                (cat_type,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM categories ORDER BY type, sort_order"
            ).fetchall()
        return [Category(**dict(r)) for r in rows]

    def add_category(self, name: str, cat_type: str, sort_order: int = 99) -> Category:
        conn = self._get_conn()
        cur = conn.execute(
            "INSERT INTO categories (name, type, sort_order) VALUES (?, ?, ?)",
            (name, cat_type, sort_order),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM categories WHERE id = ?", (cur.lastrowid,)).fetchone()
        return Category(**dict(row))

    def delete_category(self, category_id: int) -> bool:
        conn = self._get_conn()
        conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        return conn.total_changes > 0

    # ---- Bills ----

    def _build_bill_filters(
        self,
        start_date: date = None,
        end_date: date = None,
        bill_type: str = None,
        category_id: int = None,
        keyword: str = "",
        prefix: str = "",
    ) -> tuple[str, list]:
        """Build WHERE clause and params for bill queries. prefix for table alias (e.g. 'b.')."""
        conditions = []
        params = []
        if start_date:
            conditions.append(f"{prefix}bill_date >= ?")
            params.append(start_date.isoformat())
        if end_date:
            conditions.append(f"{prefix}bill_date <= ?")
            params.append(end_date.isoformat())
        if bill_type:
            conditions.append(f"{prefix}type = ?")
            params.append(bill_type)
        if category_id:
            conditions.append(f"{prefix}category_id = ?")
            params.append(category_id)
        if keyword:
            conditions.append(f"{prefix}description LIKE ?")
            params.append(f"%{keyword}%")
        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        return where, params

    def add_bill(self, bill: Bill) -> Bill:
        conn = self._get_conn()
        cur = conn.execute(
            """INSERT INTO bills (amount, type, category_id, description, bill_date)
               VALUES (?, ?, ?, ?, ?)""",
            (bill.amount, bill.type, bill.category_id, bill.description, bill.bill_date.isoformat()),
        )
        conn.commit()
        row = conn.execute(
            """SELECT b.*, c.name as category_name FROM bills b
               LEFT JOIN categories c ON b.category_id = c.id
               WHERE b.id = ?""",
            (cur.lastrowid,),
        ).fetchone()
        return Bill(**dict(row))

    def update_bill(self, bill: Bill) -> bool:
        conn = self._get_conn()
        conn.execute(
            """UPDATE bills SET amount=?, type=?, category_id=?, description=?, bill_date=?
               WHERE id=?""",
            (bill.amount, bill.type, bill.category_id, bill.description,
             bill.bill_date.isoformat(), bill.id),
        )
        conn.commit()
        return conn.total_changes > 0

    def delete_bill(self, bill_id: int) -> bool:
        conn = self._get_conn()
        conn.execute("DELETE FROM bills WHERE id = ?", (bill_id,))
        conn.commit()
        return conn.total_changes > 0

    def get_bill(self, bill_id: int) -> Optional[Bill]:
        conn = self._get_conn()
        row = conn.execute(
            """SELECT b.*, c.name as category_name FROM bills b
               LEFT JOIN categories c ON b.category_id = c.id
               WHERE b.id = ?""",
            (bill_id,),
        ).fetchone()
        return Bill(**dict(row)) if row else None

    def get_bills(
        self,
        start_date: date = None,
        end_date: date = None,
        bill_type: str = None,
        category_id: int = None,
        keyword: str = "",
        limit: int = 200,
        offset: int = 0,
    ) -> List[Bill]:
        where, params = self._build_bill_filters(
            start_date, end_date, bill_type, category_id, keyword, prefix="b.",
        )
        query = f"""SELECT b.*, c.name as category_name FROM bills b
                    LEFT JOIN categories c ON b.category_id = c.id
                    {where}
                    ORDER BY b.bill_date DESC, b.created_at DESC
                    LIMIT ? OFFSET ?"""
        params.extend([limit, offset])
        conn = self._get_conn()
        rows = conn.execute(query, params).fetchall()
        return [Bill(**dict(r)) for r in rows]

    def get_bill_count(
        self,
        start_date: date = None,
        end_date: date = None,
        bill_type: str = None,
        category_id: int = None,
        keyword: str = "",
    ) -> int:
        where, params = self._build_bill_filters(
            start_date, end_date, bill_type, category_id, keyword,
        )
        conn = self._get_conn()
        row = conn.execute(f"SELECT COUNT(*) FROM bills {where}", params).fetchone()
        return row[0]

    # ---- Summaries ----

    def get_summary(self, start_date: date, end_date: date) -> PeriodSummary:
        conn = self._get_conn()
        row = conn.execute(
            """SELECT
                 COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) as total_income,
                 COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) as total_expense
               FROM bills WHERE bill_date BETWEEN ? AND ?""",
            (start_date.isoformat(), end_date.isoformat()),
        ).fetchone()
        income = row["total_income"]
        expense = row["total_expense"]
        return PeriodSummary(
            period=f"{start_date}~{end_date}",
            total_income=income,
            total_expense=expense,
            balance=income - expense,
        )

    def get_period_summary(self, period: str) -> PeriodSummary:
        start, end = get_date_range_label(period)
        s = self.get_summary(start, end)
        s.period = period
        return s

    def get_category_summary(self, start_date: date, end_date: date, bill_type: str) -> list:
        """Return list of (category_name, total_amount) for pie chart."""
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT c.name, SUM(b.amount) as total
               FROM bills b JOIN categories c ON b.category_id = c.id
               WHERE b.type = ? AND b.bill_date BETWEEN ? AND ?
               GROUP BY b.category_id
               ORDER BY total DESC""",
            (bill_type, start_date.isoformat(), end_date.isoformat()),
        ).fetchall()
        return [(r["name"], r["total"]) for r in rows]

    def get_days_with_bills(self, start_date: date, end_date: date) -> set[str]:
        """Return set of date strings that have at least one bill."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT DISTINCT bill_date FROM bills WHERE bill_date BETWEEN ? AND ?",
            (start_date.isoformat(), end_date.isoformat()),
        ).fetchall()
        return {r["bill_date"] for r in rows}

    def get_daily_trend(self, start_date: date, end_date: date) -> list:
        """Return list of (date, income, expense) for trend chart."""
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT bill_date,
                 COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) as income,
                 COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) as expense
               FROM bills WHERE bill_date BETWEEN ? AND ?
               GROUP BY bill_date ORDER BY bill_date""",
            (start_date.isoformat(), end_date.isoformat()),
        ).fetchall()
        return [(r["bill_date"], r["income"], r["expense"]) for r in rows]

    # ---- Export / Import ----

    def export_to_csv(self, filepath: str):
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT b.id, b.amount, b.type, c.name as category, b.description,
                      b.bill_date, b.created_at
               FROM bills b LEFT JOIN categories c ON b.category_id = c.id
               ORDER BY b.bill_date DESC"""
        ).fetchall()
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "金额", "类型", "分类", "描述", "日期", "创建时间"])
            for r in rows:
                writer.writerow([
                    r["id"], r["amount"],
                    "收入" if r["type"] == "income" else "支出",
                    r["category"], r["description"], r["bill_date"], r["created_at"],
                ])

    def import_from_csv(self, filepath: str) -> tuple[int, list[str]]:
        count = 0
        errors = []
        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            with self._connect() as conn:
                for i, row in enumerate(reader, start=2):
                    raw_amount = row.get("金额", "0")
                    try:
                        amount = float(raw_amount)
                    except (ValueError, TypeError):
                        errors.append(f"第{i}行: 金额无效 '{raw_amount}'")
                        continue
                    if amount <= 0:
                        errors.append(f"第{i}行: 金额必须大于 0 (当前: {amount})")
                        continue
                    bill_type = "income" if row.get("类型", "") == "收入" else "expense"
                    category_name = row.get("分类", "")
                    description = row.get("描述", "")
                    bill_date = row.get("日期", "")
                    if not bill_date:
                        errors.append(f"第{i}行: 缺少日期")
                        continue
                    try:
                        cat_row = conn.execute(
                            "SELECT id FROM categories WHERE name = ? AND type = ?",
                            (category_name, bill_type),
                        ).fetchone()
                        if cat_row:
                            cat_id = cat_row["id"]
                        else:
                            cur = conn.execute(
                                "INSERT INTO categories (name, type, sort_order) VALUES (?, ?, 99)",
                                (category_name, bill_type),
                            )
                            cat_id = cur.lastrowid
                        conn.execute(
                            """INSERT INTO bills (amount, type, category_id, description, bill_date)
                               VALUES (?, ?, ?, ?, ?)""",
                            (amount, bill_type, cat_id, description, bill_date),
                        )
                    except sqlite3.IntegrityError as e:
                        errors.append(f"第{i}行: 数据库错误 ({e})")
                        continue
                    count += 1
        return count, errors

    def export_to_json(self, filepath: str):
        conn = self._get_conn()
        bills = conn.execute(
            """SELECT b.*, c.name as category_name FROM bills b
               LEFT JOIN categories c ON b.category_id = c.id
               ORDER BY b.bill_date DESC"""
        ).fetchall()
        categories = conn.execute("SELECT * FROM categories ORDER BY type, sort_order").fetchall()
        data = {
            "bills": [dict(r) for r in bills],
            "categories": [dict(r) for r in categories],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    def import_from_json(self, filepath: str) -> int:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        with self._connect() as conn:
            # import categories first
            name_to_id = {}
            for cat in data.get("categories", []):
                row = conn.execute(
                    "SELECT id FROM categories WHERE name = ? AND type = ?",
                    (cat["name"], cat["type"]),
                ).fetchone()
                if row:
                    name_to_id[(cat["name"], cat["type"])] = row["id"]
                else:
                    cur = conn.execute(
                        "INSERT INTO categories (name, type, sort_order) VALUES (?, ?, ?)",
                        (cat["name"], cat["type"], cat.get("sort_order", 99)),
                    )
                    name_to_id[(cat["name"], cat["type"])] = cur.lastrowid
            # import bills
            for bill in data.get("bills", []):
                cat_key = (bill.get("category_name", ""), bill.get("type", "expense"))
                cat_id = name_to_id.get(cat_key)
                if cat_id is None and bill.get("category_id"):
                    cat_id = bill["category_id"]
                conn.execute(
                    """INSERT INTO bills (amount, type, category_id, description, bill_date)
                       VALUES (?, ?, ?, ?, ?)""",
                    (bill["amount"], bill["type"], cat_id, bill.get("description", ""), bill["bill_date"]),
                )
                count += 1
        return count

    def delete_all_bills(self):
        conn = self._get_conn()
        conn.execute("DELETE FROM bills")
        conn.commit()
