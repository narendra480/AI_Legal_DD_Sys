import re
from typing import List, Dict

def chunk_text(
    pages: List[Dict],
    doc_name: str,
    max_chars: int = 800,
    overlap: int = 150
) -> List[Dict]:
    """
    Chunk text while preserving metadata
    pages = [{"page": 1, "text": "..."}]
    """

    chunks = []
    chunk_id = 0

    for page in pages:
        page_num = page["page"]
        text = page["text"]

        sentences = re.split(r'(?<=[.!?])\s+', text)
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_chars:
                current_chunk += " " + sentence
            else:
                chunks.append({
                    "chunk_id": chunk_id,
                    "doc_name": doc_name,   # ✅ NEW
                    "page": page_num,
                    "text": current_chunk.strip()
                })
                chunk_id += 1
                current_chunk = current_chunk[-overlap:] + " " + sentence

        if current_chunk.strip():
            chunks.append({
                "chunk_id": chunk_id,
                "doc_name": doc_name,   # ✅ NEW
                "page": page_num,
                "text": current_chunk.strip()
            })
            chunk_id += 1

    return chunks
