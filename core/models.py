from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Category:
    id: Optional[int]
    name: str
    type: str  # 'income' or 'expense'
    sort_order: int = 0


@dataclass
class Bill:
    id: Optional[int]
    amount: float
    type: str  # 'income' or 'expense'
    category_id: Optional[int]
    category_name: str = ""
    description: str = ""
    bill_date: date = None
    created_at: str = ""

    def __post_init__(self):
        if self.bill_date is None:
            self.bill_date = date.today()
        if isinstance(self.bill_date, str):
            from datetime import datetime
            self.bill_date = datetime.strptime(self.bill_date, "%Y-%m-%d").date()


@dataclass
class PeriodSummary:
    period: str
    total_income: float = 0.0
    total_expense: float = 0.0
    balance: float = 0.0
