"""Upload router — handles PDF upload and ingestion."""

import os
import uuid
import fitz
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import get_settings
from app.models.schemas import UploadResponse
from app.ingestion.pdf_parser import parse_pdf
from app.ingestion.chunker import chunk_document
from app.ingestion.metadata import extract_metadata
from app.retrieval.embeddings import embed_texts
from app.retrieval.vector_store import VectorStore

router = APIRouter(tags=["Upload"])


@router.post("/upload-paper", response_model=UploadResponse)
async def upload_paper(file: UploadFile = File(...)):
    """Upload a PDF research paper for analysis.

    Runs the full ingestion pipeline:
    1. Save PDF
    2. Parse text & detect sections
    3. Semantic chunking
    4. Generate embeddings
    5. Build FAISS index
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    settings = get_settings()
    paper_id = str(uuid.uuid4())[:8]

    # 1. Save PDF
    pdf_path = os.path.join(settings.upload_dir, f"{paper_id}.pdf")
    content = await file.read()
    with open(pdf_path, "wb") as f:
        f.write(content)

    try:
        # Get page count
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        doc.close()

        # 2. Parse PDF into sections
        sections = parse_pdf(pdf_path)

        if not sections:
            raise HTTPException(status_code=422, detail="Could not extract text from PDF")

        # 3. Chunk sections
        chunks = chunk_document(sections, paper_id)

        if not chunks:
            raise HTTPException(status_code=422, detail="No chunks generated from PDF")

        # 4. Generate embeddings
        chunk_texts = [c.text for c in chunks]
        embeddings = embed_texts(chunk_texts)

        # 5. Build FAISS index
        store = VectorStore(paper_id)
        store.build(chunks, embeddings)

        # 6. Extract metadata
        metadata = extract_metadata(sections, paper_id, file.filename, total_pages)

        return UploadResponse(
            paper_id=paper_id,
            metadata=metadata,
            num_chunks=len(chunks),
        )

    except HTTPException:
        raise
    except Exception as e:
        # Clean up on failure
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
