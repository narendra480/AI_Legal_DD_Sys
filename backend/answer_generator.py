from llm_config import init_gemini
import re
from typing import List
import google.generativeai as genai


# =====================================================
# 🔐 Initialize Gemini ONCE
# =====================================================
init_gemini()   # 🔥 THIS WAS MISSING (critical)


# =====================================================
# 🧹 Clean LLM Output
# =====================================================
def clean_answer(text: str) -> str:
    """
    Cleans LLM output for legal readability
    """
    if not text:
        return "Answer could not be generated from the provided documents."

    text = re.sub(r"\*\*", "", text)          # remove markdown bold
    text = re.sub(r"\*", "", text)            # remove stray asterisks
    text = re.sub(r"\n{3,}", "\n\n", text)    # normalize spacing
    return text.strip()


# =====================================================
# 🧠 Generate Legal Answer
# =====================================================
def generate_answer(question: str, sources: List[dict]) -> str:
    """
    Generates a clean, structured legal answer
    using Gemini with strong safety checks
    """

    if not sources:
        return "Answer not found in the provided documents."

    # -------------------------------------------------
    # 📚 Build context
    # -------------------------------------------------
    #context = "\n\n".join(
       #f"Document: {s['document']} | Page {s['page']}:\n{s['content']}"
       #for s in sources
    #)
    context = "\n\n".join(
    f"Page {s.get('page', '-') }:\n{s.get('content') or s.get('text', '')}"
    for s in sources
)


    prompt = f"""
You are a legal due diligence assistant.

Answer the question strictly based on the provided document excerpts.
If the answer is not found, clearly say so.
If the answer is partially available, explain carefully.

Rules:
- Use clear paragraphs (no bullets or markdown)
- Use formal legal tone
- Do NOT invent facts
- Do NOT use symbols like *, **, -, or numbering

Question:
{question}

Document Excerpts:
{context}
"""

    try:
        # ✅ Use STABLE model
        model = genai.GenerativeModel("gemini-3-flash-preview")

        response = model.generate_content(prompt)

        # -------------------------------------------------
        # 🛡 Safe extraction
        # -------------------------------------------------
        if hasattr(response, "text") and response.text:
            return clean_answer(response.text)

        # Fallback (older SDK response structure)
        if response.candidates:
            parts = response.candidates[0].content.parts
            if parts and hasattr(parts[0], "text"):
                return clean_answer(parts[0].text)

        return "Answer could not be generated from the provided documents."

    except Exception as e:
        # 🚨 NEVER crash FastAPI
        return (
            "The answer could not be generated at this time "
            "due to system limits. Please try again shortly."
        )