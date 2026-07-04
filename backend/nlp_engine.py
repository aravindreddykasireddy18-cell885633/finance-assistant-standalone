"""
Standalone NLP engine — no external API, no internet connection required.

Approach: intent classification via keyword/regex scoring + simple entity
extraction (category names, numbers). This is a common, production-viable
pattern for a bounded domain like personal finance, where the set of things
a user can ask about is well-defined. It trades some flexibility for being
fully self-contained, free to run, and instant (no network round trip).

Swap-in path for later: if you outgrow rule-based matching, replace
`classify_intent` with a trained scikit-learn/spaCy text classifier without
changing anything in main.py — the function signature stays the same.
"""

import re
from dataclasses import dataclass

import finance_data as fd

INTENTS = [
    "spending_summary",
    "budget_status",
    "income_vs_expenses",
    "top_merchants",
    "greeting",
    "help",
    "unknown",
]

# Keyword sets per intent. Order matters: first match with the highest score wins.
INTENT_KEYWORDS = {
    "budget_status": [
        "budget", "over budget", "under budget", "overspend", "overspending",
        "on track", "limit",
    ],
    "spending_summary": [
        "spend", "spent", "spending", "cost", "how much did i", "how much have i",
        "expenses on", "paid for",
    ],
    "income_vs_expenses": [
        "income", "net savings", "saving", "savings this month", "earn", "earned",
        "left over", "leftover", "surplus",
    ],
    "top_merchants": [
        "top merchant", "where do i spend", "biggest expense", "most spent",
        "highest spend", "top spending",
    ],
    "greeting": ["hello", "hi", "hey", "good morning", "good afternoon"],
    "help": ["help", "what can you do", "what can i ask"],
}


def _find_category(text: str) -> str | None:
    text_lower = text.lower()
    for cat in fd.CATEGORIES:
        if cat.lower() in text_lower:
            return cat
    return None


def classify_intent(text: str) -> str:
    text_lower = text.lower()
    scores = {intent: 0 for intent in INTENT_KEYWORDS}
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[intent] += len(kw.split())  # longer phrase matches score higher
    best_intent = max(scores, key=scores.get)
    if scores[best_intent] == 0:
        return "unknown"
    return best_intent


@dataclass
class NLPResult:
    intent: str
    category: str | None
    reply: str


def handle_message(text: str) -> NLPResult:
    intent = classify_intent(text)
    category = _find_category(text)

    if intent == "greeting":
        reply = "Hi! I can tell you about your spending, budget status, or savings. Try asking 'How much have I spent on groceries?'"

    elif intent == "help":
        reply = (
            "You can ask me things like:\n"
            "- \"How much have I spent on dining?\"\n"
            "- \"Am I over budget anywhere?\"\n"
            "- \"What's my net savings this month?\"\n"
            "- \"Where do I spend the most?\""
        )

    elif intent == "spending_summary":
        data = fd.get_spending_summary(category)
        if category:
            reply = f"You've spent ${data['total_spent']} on {category} this month, across {data['transaction_count']} transaction(s)."
        else:
            reply = f"You've spent ${data['total_spent']} in total this month, across {data['transaction_count']} transaction(s)."

    elif intent == "budget_status":
        rows = fd.get_budget_status(category)
        if not rows:
            reply = "I don't have a budget set for that category yet."
        elif len(rows) == 1:
            r = rows[0]
            status = "over" if r["over_budget"] else "under"
            reply = (
                f"{r['category']}: you've spent ${r['spent']} of your ${r['budget']} budget "
                f"— you're {status} budget, with ${r['remaining']} remaining."
            )
        else:
            over = [r for r in rows if r["over_budget"]]
            if over:
                lines = [f"- {r['category']}: ${r['spent']} spent of ${r['budget']} (over by ${-r['remaining']})" for r in over]
                reply = "You're over budget in:\n" + "\n".join(lines)
            else:
                reply = "Good news — you're within budget in every category this month!"

    elif intent == "income_vs_expenses":
        data = fd.get_income_vs_expenses()
        reply = (
            f"This month: income ${data['income']}, expenses ${data['expenses']}, "
            f"net savings ${data['net_savings']}."
        )

    elif intent == "top_merchants":
        rows = fd.get_top_merchants()
        lines = [f"{i+1}. {r['merchant']} — ${r['total_spent']}" for i, r in enumerate(rows)]
        reply = "Your top merchants by spend this month:\n" + "\n".join(lines)

    else:
        reply = (
            "I'm not sure I understood that. I can help with spending, budgets, "
            "and savings questions — try asking \"what can you do?\" for examples."
        )

    return NLPResult(intent=intent, category=category, reply=reply)
