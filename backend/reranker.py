from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank_chunks(question: str, retrieved_chunks: list[dict], top_k: int = 3):
    """
    Cross-encoder reranking for precision
    """
    pairs = [(question, item["text"]) for item in retrieved_chunks]
    scores = reranker.predict(pairs)

    for item, score in zip(retrieved_chunks, scores):
        item["rerank_score"] = float(score)

    reranked = sorted(
        retrieved_chunks,
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return reranked[:top_k]
