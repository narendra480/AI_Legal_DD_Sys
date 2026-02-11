import re

def clean_text(text: str) -> str:
    if not text:
        return ""

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    # Remove non-readable junk characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    # Strip leading/trailing spaces
    return text.strip()
