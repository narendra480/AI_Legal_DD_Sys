import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def search_chunks(query, model, index, chunks, top_k=5):
    query_embedding = model.encode([query], convert_to_numpy=True)

    distances, indices = index.search(query_embedding, top_k)

    results = []
    max_score = None

    for rank, idx in enumerate(indices[0]):
        if idx == -1:
            continue

        score = 1 - distances[0][rank]  # ✅ convert L2 → similarity

        if max_score is None:
            max_score = score

        chunk = chunks[idx]

        results.append({
            "rank": rank + 1,
            "chunk_id": chunk["chunk_id"],
            "doc_name": chunk["doc_name"],
            "page": chunk["page"],
            "text": chunk["text"],
            "score": round(score, 3),
            "confidence_pct": round(score * 100, 1)  # ✅ UI friendly
        })

    return results
