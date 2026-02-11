# risk_rules.py

RISK_RULES = [
    {
        "risk_type": "Termination",
        "severity": "High",
        "keywords": ["terminate", "termination", "exit"],
    },
    {
        "risk_type": "Penalty",
        "severity": "Medium",
        "keywords": ["penalty", "liquidated damages", "fine"],
    },
    {
        "risk_type": "Indemnity",
        "severity": "High",
        "keywords": ["indemnify", "indemnification"],
    },
    {
        "risk_type": "Governing Law",
        "severity": "Low",
        "keywords": ["governing law", "jurisdiction"],
    },
]
