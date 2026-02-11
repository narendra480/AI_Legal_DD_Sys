from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load model once (good practice – keep this)
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_chunks(chunks: list[str]):
    """
    Converts text chunks into embeddings and stores them in FAISS.

    FIXES:
    - Skips empty / whitespace-only chunks
    - Filters NaN embeddings (prevents cosine_similarity crash)
    - Handles OCR noise safely
    """

    # ✅ 1. Clean + filter chunks BEFORE embedding
    clean_chunks = []
    valid_indices = []

    for i, text in enumerate(chunks):
        if isinstance(text, str) and text.strip():
            clean_chunks.append(text.strip())
            valid_indices.append(i)

    # ❌ Nothing valid to embed
    if not clean_chunks:
        raise ValueError("No valid text chunks to embed")

    # ✅ 2. Generate embeddings
    embeddings = model.encode(
        clean_chunks,
        convert_to_numpy=True,
        normalize_embeddings=True  # 🔥 improves cosine similarity stability
    )

    # ✅ 3. Remove NaN / Inf embeddings (very important)
    mask = np.isfinite(embeddings).all(axis=1)
    embeddings = embeddings[mask]

    if embeddings.shape[0] == 0:
        raise ValueError("All embeddings contained NaN or Inf")

    # ✅ 4. Build FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # IP + normalized = cosine similarity
    index.add(embeddings)

    return index, embeddings
