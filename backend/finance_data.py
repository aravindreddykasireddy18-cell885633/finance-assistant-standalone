"""
Mock financial data layer.

Stands in for a real database + banking API integration (later phases).
Every function here returns plain data — swap the internals for real DB
queries later without touching the NLP/chat logic.
"""

from datetime import date

TRANSACTIONS = [
    {"date": "2026-06-02", "merchant": "Whole Foods", "category": "Groceries", "amount": -84.32},
    {"date": "2026-06-03", "merchant": "Shell Gas", "category": "Transport", "amount": -45.10},
    {"date": "2026-06-05", "merchant": "Netflix", "category": "Subscriptions", "amount": -15.99},
    {"date": "2026-06-07", "merchant": "Paycheck", "category": "Income", "amount": 3200.00},
    {"date": "2026-06-10", "merchant": "Trader Joe's", "category": "Groceries", "amount": -62.18},
    {"date": "2026-06-12", "merchant": "Uber", "category": "Transport", "amount": -22.50},
    {"date": "2026-06-15", "merchant": "Spotify", "category": "Subscriptions", "amount": -9.99},
    {"date": "2026-06-18", "merchant": "Cheesecake Factory", "category": "Dining", "amount": -58.40},
    {"date": "2026-06-20", "merchant": "Amazon", "category": "Shopping", "amount": -120.75},
    {"date": "2026-06-22", "merchant": "Whole Foods", "category": "Groceries", "amount": -91.05},
    {"date": "2026-06-25", "merchant": "Gym Membership", "category": "Health", "amount": -40.00},
    {"date": "2026-06-28", "merchant": "Chipotle", "category": "Dining", "amount": -14.20},
]

BUDGETS = {
    "Groceries": 300,
    "Transport": 150,
    "Subscriptions": 40,
    "Dining": 120,
    "Shopping": 150,
    "Health": 50,
}

CATEGORIES = list(BUDGETS.keys())


def get_spending_summary(category: str | None = None) -> dict:
    txns = [t for t in TRANSACTIONS if t["amount"] < 0]
    if category:
        txns = [t for t in txns if t["category"].lower() == category.lower()]
    total = round(sum(-t["amount"] for t in txns), 2)
    return {
        "category": category or "All categories",
        "total_spent": total,
        "transaction_count": len(txns),
    }


def get_budget_status(category: str | None = None) -> list[dict]:
    cats = [category] if category else BUDGETS.keys()
    result = []
    for cat in cats:
        if cat not in BUDGETS:
            continue
        budget = BUDGETS[cat]
        spent = round(sum(-t["amount"] for t in TRANSACTIONS
                           if t["category"] == cat and t["amount"] < 0), 2)
        result.append({
            "category": cat,
            "budget": budget,
            "spent": spent,
            "remaining": round(budget - spent, 2),
            "over_budget": spent > budget,
        })
    return result


def get_income_vs_expenses() -> dict:
    income = round(sum(t["amount"] for t in TRANSACTIONS if t["amount"] > 0), 2)
    expenses = round(-sum(t["amount"] for t in TRANSACTIONS if t["amount"] < 0), 2)
    return {
        "income": income,
        "expenses": expenses,
        "net_savings": round(income - expenses, 2),
        "as_of": str(date.today()),
    }


def get_top_merchants(limit: int = 3) -> list[dict]:
    totals: dict[str, float] = {}
    for t in TRANSACTIONS:
        if t["amount"] < 0:
            totals[t["merchant"]] = totals.get(t["merchant"], 0) + (-t["amount"])
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    return [{"merchant": m, "total_spent": round(v, 2)} for m, v in ranked]
