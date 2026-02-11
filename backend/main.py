from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
from io import BytesIO
from pydantic import BaseModel

import PyPDF2
import pytesseract
from pdf2image import convert_from_bytes

from dd_report_generator import generate_dd_report

# ==========================
# Internal modules
# ==========================
from text_cleaner import clean_text
from text_chunker import chunk_text
from text_embedder import embed_chunks, model
from semantic_search import search_chunks
from answer_generator import generate_answer
from document_classifier import classify_document
from risk_detector import detect_risks
from risk_aggregator import aggregate_risks

# =====================================================
# 🚀 App Init
# =====================================================
app = FastAPI(title="AI Legal Due Diligence Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

POPPLER_PATH = r"C:\Users\narik\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin"

# =====================================================
# 🧠 GLOBAL STATE (IN-MEMORY)
# =====================================================
VECTOR_INDEX = None
ALL_CHUNKS = []
DOC_COUNTER = 0

DOCUMENTS = {}
DOCUMENT_RISKS = {}

# ✅ SINGLE SOURCE OF TRUTH FOR REPORT
DD_SUMMARY_CACHE = None

# =====================================================
# 📤 Upload & Index PDF
# =====================================================
@app.post("/extract_pdf_text/")
async def extract_pdf_text(
    file: UploadFile = File(...),
    use_ocr: Optional[bool] = False,
    reset: bool = Query(False)
):
    global VECTOR_INDEX, ALL_CHUNKS, DOC_COUNTER
    global DOCUMENTS, DOCUMENT_RISKS, DD_SUMMARY_CACHE

    if reset:
        VECTOR_INDEX = None
        ALL_CHUNKS = []
        DOCUMENTS = {}
        DOCUMENT_RISKS = {}
        DD_SUMMARY_CACHE = None
        DOC_COUNTER = 0

    DOC_COUNTER += 1
    doc_id = DOC_COUNTER
    doc_name = file.filename

    contents = await file.read()
    pages = []
    ocr_used = False

    try:
        reader = PyPDF2.PdfReader(BytesIO(contents))
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages.append({"page": i + 1, "text": clean_text(text)})
    except:
        pass

    if not pages or use_ocr:
        images = convert_from_bytes(contents, dpi=300, poppler_path=POPPLER_PATH)
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image)
            if text.strip():
                pages.append({"page": i + 1, "text": clean_text(text)})
                ocr_used = True

    if not pages:
        return {"error": "No readable text found"}

    doc_profile = classify_document(doc_name, pages)

    chunks = chunk_text(pages, doc_name)
    for c in chunks:
        c["doc_id"] = doc_id
        c["doc_type"] = doc_profile["doc_type"]

    risks = detect_risks(chunks)

    DOCUMENTS[doc_id] = {
        "doc_id": doc_id,
        "doc_name": doc_name,
        "doc_type": doc_profile["doc_type"],
        "classification_confidence": doc_profile["confidence"]
    }

    DOCUMENT_RISKS[doc_id] = risks

    ALL_CHUNKS.extend(chunks)
    texts = [c["text"] for c in ALL_CHUNKS]
    VECTOR_INDEX, _ = embed_chunks(texts)

    return {"status": "indexed", "doc_name": doc_name}

# =====================================================
# ❓ Ask Question
# =====================================================
class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask(payload: QuestionRequest):
    retrieved = search_chunks(payload.question, model, VECTOR_INDEX, ALL_CHUNKS)
    answer = generate_answer(payload.question, retrieved[:5])
    return {"answer": answer}

# =====================================================
# 📊 Due Diligence Summary
# =====================================================
@app.get("/due-diligence/summary")
def due_diligence_summary():
    global DD_SUMMARY_CACHE

    if not DOCUMENTS:
        return {"status": "empty", "documents": {}}

    aggregated = aggregate_risks(DOCUMENT_RISKS, DOCUMENTS)

    # ✅ ALWAYS refresh cache here
    DD_SUMMARY_CACHE = {
        "documents": aggregated["documents"],
        "heat_map": aggregated["heat_map"]
    }

    return {
        "status": "success",
        "documents": aggregated["documents"],
        "heat_map": aggregated["heat_map"]
    }

# =====================================================
# 📄 Download DD Report (FIXED)
# =====================================================
@app.get("/due-diligence/report")
def download_dd_report():
    global DD_SUMMARY_CACHE

    # 🔥 SAFETY NET: auto-generate if cache missing
    if not DD_SUMMARY_CACHE:
        if not DOCUMENTS:
            return JSONResponse(
                status_code=400,
                content={"error": "No documents uploaded"}
            )

        aggregated = aggregate_risks(DOCUMENT_RISKS, DOCUMENTS)
        DD_SUMMARY_CACHE = {
            "documents": aggregated["documents"],
            "heat_map": aggregated["heat_map"]
        }

    output_file = "Due_Diligence_Report.docx"
    generate_dd_report(DD_SUMMARY_CACHE, output_file)

    return FileResponse(
        path=output_file,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=output_file
    )
