# risk_detector.py

from risk_rules import RISK_RULES
import re

def extract_clean_sentence(text: str, keyword: str) -> str:
    """
    Extracts a clean, complete sentence containing the keyword.
    Falls back gracefully if sentence boundaries are unclear.
    """

    # Normalize spacing
    clean_text = re.sub(r"\s+", " ", text).strip()

    # Split into sentences using punctuation
    sentences = re.split(r'(?<=[.!?])\s+', clean_text)

    # Try to find the sentence containing the keyword
    for sentence in sentences:
        if keyword.lower() in sentence.lower():
            return sentence.strip()

    # Fallback: return first 250 chars (safe cut)
    return clean_text[:250].rsplit(" ", 1)[0]


def detect_risks(chunks: list) -> list:
    """
    Detect risks from text chunks using keyword-based rules.
    Returns structured risk objects (schema unchanged).
    """

    detected = []

    for chunk in chunks:
        text = chunk["text"]

        for rule in RISK_RULES:
            for kw in rule["keywords"]:
                if kw.lower() in text.lower():

                    # 🔥 CLEAN SENTENCE EXTRACTION
                    snippet = extract_clean_sentence(text, kw)

                    detected.append({
                        "risk_type": rule["risk_type"],
                        "severity": rule["severity"],
                        "page": chunk.get("page"),
                        "snippet": snippet
                    })
                    break  # avoid duplicate risks per rule

    return detected
