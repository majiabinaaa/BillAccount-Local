"""Financial health scoring and consumer profile analysis."""
from datetime import date, timedelta


def calculate_health_score(db) -> dict:
    """
    Returns:
        {
            'score': int 0-100,
            'label': '优秀'|'良好'|'一般'|'需要注意',
            'color': '#4CAF50'|'#2196F3'|'#FF9800'|'#F44336',
            'breakdown': {
                'savings':    {'score': int, 'max': 40, 'label': '储蓄率'},
                'coverage':   {'score': int, 'max': 20, 'label': '收支覆盖'},
                'consistency':{'score': int, 'max': 20, 'label': '记账坚持'},
                'diversity':  {'score': int, 'max': 20, 'label': '消费多样性'},
            }
        }
    """
    today = date.today()
    month_start = today.replace(day=1)

    # 1. Savings rate (40 pts)
    ms = db.get_summary(month_start, today)
    income = ms.total_income
    expense = ms.total_expense
    if income > 0:
        savings_rate = max(0, (income - expense) / income)
    else:
        savings_rate = 0
    savings_score = round(min(savings_rate, 1.0) * 40)

    # 2. Income coverage (20 pts)
    if expense == 0:
        coverage_score = 20 if income > 0 else 0
    elif income >= expense:
        coverage_score = 20
    else:
        coverage_score = round(min(income / expense, 1.0) * 20)

    # 3. Recording consistency (20 pts): weeks with >= 1 bill in last 4 weeks
    weeks_with_data = 0
    for w in range(4):
        ws = today - timedelta(days=today.weekday() + w * 7)
        we = ws + timedelta(days=6)
        count = db.get_bill_count(start_date=ws, end_date=we)
        if count > 0:
            weeks_with_data += 1
    consistency_score = round(weeks_with_data / 4 * 20)

    # 4. Spending diversity (20 pts): 1 - Herfindahl index
    cat_data = db.get_category_summary(month_start, today, "expense")
    total_exp = sum(v for _, v in cat_data)
    if total_exp > 0:
        herfindahl = sum((v / total_exp) ** 2 for _, v in cat_data)
        diversity = max(0, 1 - herfindahl)
    else:
        diversity = 0
    diversity_score = round(diversity * 20)

    total = savings_score + coverage_score + consistency_score + diversity_score
    total = max(0, min(100, total))

    if total >= 80:
        label, color = "优秀", "#4CAF50"
    elif total >= 60:
        label, color = "良好", "#2196F3"
    elif total >= 40:
        label, color = "一般", "#FF9800"
    else:
        label, color = "需要注意", "#F44336"

    return {
        "score": total,
        "label": label,
        "color": color,
        "breakdown": {
            "savings":     {"score": savings_score,     "max": 40, "label": "储蓄率"},
            "coverage":    {"score": coverage_score,     "max": 20, "label": "收支覆盖"},
            "consistency": {"score": consistency_score,  "max": 20, "label": "记账坚持"},
            "diversity":   {"score": diversity_score,    "max": 20, "label": "消费多样性"},
        },
    }


PERSONALITIES = [
    {
        "key": "foodie",
        "condition": lambda cats, rate: cats.get("餐饮", 0) > 35,
        "emoji": "🍜",
        "title": "美食家",
        "desc": "你的生活离不开美食探索，餐饮支出占据了显著位置。热爱美食是生活的乐趣，也别忘了平衡其他开支哦。",
        "suggestion": "试试每月设置一个\"美食预算\"上限，周末自己做饭也是不错的选择。",
    },
    {
        "key": "saver",
        "condition": lambda cats, rate: rate > 50,
        "emoji": "💎",
        "title": "稳健理财者",
        "desc": "你的储蓄率相当出色，财务自律令人敬佩。稳健的积累让你有充足的安全感。",
        "suggestion": "可以适当拿出一部分储蓄做稳健投资，让钱为你工作。",
    },
    {
        "key": "shopper",
        "condition": lambda cats, rate: cats.get("购物", 0) > 30,
        "emoji": "🛍️",
        "title": "品质生活家",
        "desc": "你愿意为品质买单，购物是你表达自我的方式。偶尔需要审视一下哪些是真正的\"需要\"。",
        "suggestion": "购物前试试\"24小时冷静期\"规则，延迟满足能减少冲动消费。",
    },
    {
        "key": "learner",
        "condition": lambda cats, rate: cats.get("教育", 0) > 15,
        "emoji": "📚",
        "title": "成长投资人",
        "desc": "你在教育和自我提升上的投入远超常人，最好的投资就是投资自己。",
        "suggestion": "关注学习回报率，学以致用，让知识转化为实际收入增长。",
    },
    {
        "key": "homebody",
        "condition": lambda cats, rate: cats.get("住房", 0) > 40,
        "emoji": "🏠",
        "title": "安居达人",
        "desc": "住房相关支出在你的生活中占主导，你可能已在供房或是租赁市场的主力军。",
        "suggestion": "如果房贷/租金占比过高，考虑是否可以通过合租或换租来降低压力。",
    },
    {
        "key": "entertainer",
        "condition": lambda cats, rate: cats.get("娱乐", 0) > 25,
        "emoji": "🎬",
        "title": "体验派",
        "desc": "娱乐和体验是你生活的调味剂，你相信生活的意义在于丰富的体验。",
        "suggestion": "很多城市有免费的文化活动和展览，享受生活不一定需要高消费。",
    },
    {
        "key": "traveler",
        "condition": lambda cats, rate: cats.get("交通", 0) > 25,
        "emoji": "🚗",
        "title": "行者",
        "desc": "交通是你的主要支出之一，你可能经常出差、通勤距离较远或是热爱自驾出行。",
        "suggestion": "检查一下是否有更经济的交通方案，如公共交通月卡或拼车。",
    },
    {
        "key": "healthcare",
        "condition": lambda cats, rate: cats.get("医疗", 0) > 20,
        "emoji": "💊",
        "title": "健康守护者",
        "desc": "医疗健康方面的支出较高，照顾好自己的身体是头等大事。",
        "suggestion": "考虑配置合适的健康保险，定期体检比生病后再治疗更划算。",
    },
    {
        "key": "balanced",
        "condition": lambda cats, rate: True,  # catch-all default
        "emoji": "⚖️",
        "title": "均衡型",
        "desc": "你的消费结构比较均衡，没有单一类别过度集中，这是很好的理财习惯。",
        "suggestion": "保持当前的消费节奏，可以尝试制定月度预算来进一步优化。",
    },
]


def get_consumer_profile(db) -> dict:
    """Analyze spending and return a personality profile dict."""
    today = date.today()
    month_start = today.replace(day=1)

    ms = db.get_summary(month_start, today)
    income = ms.total_income
    expense = ms.total_expense
    savings_rate = ((income - expense) / income * 100) if income > 0 else 0

    cat_data = db.get_category_summary(month_start, today, "expense")
    total_exp = sum(v for _, v in cat_data) if cat_data else 0

    # category percentage map
    cat_pct = {}
    top_categories = []
    for name, val in cat_data:
        pct = round(val / total_exp * 100, 1) if total_exp > 0 else 0
        cat_pct[name] = pct
        top_categories.append({"name": name, "amount": val, "pct": pct})
    top_categories.sort(key=lambda x: x["amount"], reverse=True)

    # match personality — "balanced" is last (always-True condition), acts as default
    personality = PERSONALITIES[-1]
    for p in PERSONALITIES[:-1]:
        if p["condition"](cat_pct, savings_rate):
            personality = p
            break

    # saver takes priority if savings rate is high
    if personality["key"] != "saver" and savings_rate > 50:
        personality = next(p for p in PERSONALITIES if p["key"] == "saver")

    return {
        "emoji": personality["emoji"],
        "title": personality["title"],
        "desc": personality["desc"],
        "suggestion": personality["suggestion"],
        "savings_rate": round(savings_rate, 1),
        "total_income": income,
        "total_expense": expense,
        "balance": income - expense,
        "top_categories": top_categories[:5],
    }
