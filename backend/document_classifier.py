# document_classifier.py
# -------------------------------------------------
# Classifies document type using keyword scoring
# -------------------------------------------------

from typing import List

DOCUMENT_RULES = {
    "MOA": [
        "memorandum of association",
        "objects clause",
        "capital clause"
    ],
    "AOA": [
        "articles of association",
        "board of directors",
        "voting rights"
    ],
    "LOAN_AGREEMENT": [
        "loan agreement",
        "interest rate",
        "repayment",
        "security"
    ],
    "SHAREHOLDING": [
        "shareholding",
        "shareholders",
        "equity shares"
    ],
    "IP": [
        "intellectual property",
        "patent",
        "trademark",
        "copyright"
    ]
}


def classify_document(doc_name: str, pages: List[dict]) -> dict:
    """
    Returns:
    {
        "doc_type": "MOA",
        "confidence": 0.72
    }
    """

    text = " ".join(p["text"].lower() for p in pages[:3])

    scores = {}
    for doc_type, keywords in DOCUMENT_RULES.items():
        scores[doc_type] = sum(1 for k in keywords if k in text)

    best_match = max(scores, key=scores.get)
    max_score = scores[best_match]

    confidence = min(1.0, max_score / 4)

    return {
        "doc_type": best_match if max_score > 0 else "UNKNOWN",
        "confidence": round(confidence, 2)
    }
