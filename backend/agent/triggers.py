# agent/triggers.py

# Maps keywords found in user messages to ET products to cross-sell
TRIGGER_RULES = [
    {
        "keywords": ["startup", "founder", "co-founder", "building", "fundraising", "pitch", "vc", "angel"],
        "product": "ET Entrepreneur Summit",
        "message": "Since you're in the startup space — have you heard about the ET Entrepreneur Summit? It's one of the best places to meet investors and fellow founders. Shall I tell you more?",
        "url": "https://economictimes.indiatimes.com/small-biz"
    },
    {
        "keywords": ["sip", "mutual fund", "index fund", "direct plan", "elss", "tax saving"],
        "product": "ET Money",
        "message": "Since you mentioned mutual funds — ET Money offers direct plans with 0% commission, which means you keep more of your returns. Worth checking out alongside ET Wealth.",
        "url": "https://www.etmoney.com"
    },
    {
        "keywords": ["tax", "itr", "income tax", "80c", "tax saving", "hra", "deduction"],
        "product": "ET Wealth",
        "message": "Tax planning is one of ET Wealth's strengths — they have step-by-step guides updated for the latest tax slabs. It could save you lakhs if used right.",
        "url": "https://economictimes.indiatimes.com/wealth"
    },
    {
        "keywords": ["cxo", "cfo", "ceo", "cto", "senior", "vp", "director", "leadership", "executive"],
        "product": "ET Masterclass",
        "message": "For someone at your level, ET Masterclass might be interesting — they run exclusive workshops with PwC, KPMG, and IIM faculty on leadership and strategy.",
        "url": "https://etmasterclass.economictimes.com"
    },
    {
        "keywords": ["nifty", "sensex", "stocks", "trading", "demat", "options", "futures", "equity", "f&o"],
        "product": "ET Markets",
        "message": "For active tracking, ET Markets has live prices, a portfolio tracker, and stock screener — all free. Would be a powerful tool for your trading.",
        "url": "https://economictimes.indiatimes.com/markets"
    },
    {
        "keywords": ["retire", "retirement", "pension", "fd", "fixed deposit", "safe", "conservative", "protect"],
        "product": "ET Wealth",
        "message": "For retirement and conservative investing, ET Wealth has excellent guides on FD laddering, senior citizen savings, and NPS. Would that be useful?",
        "url": "https://economictimes.indiatimes.com/wealth"
    },
]


def check_triggers(message: str) -> dict | None:
    """
    Check if a user message contains any cross-sell trigger keywords.
    Returns the first matching trigger, or None.
    """
    message_lower = message.lower()
    for rule in TRIGGER_RULES:
        for keyword in rule["keywords"]:
            if keyword in message_lower:
                return rule
    return None
