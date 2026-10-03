from fastapi import APIRouter, UploadFile, File
import os
import shutil

from services.pdf_service import extract_text_from_pdf
from services.chunking_service import create_chunk
from services.embedding_service import embedding_for_chunk
from services.vector_services import create_index


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


# Temporary in-memory storage
documents = {}

from pathlib import Path

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    file_path = f"{UPLOAD_DIR }/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 1. Extract text
    text_data = extract_text_from_pdf(file_path)

    # 2. Create chunks
    chunks = create_chunk(text_data)

    # 3. Generate embeddings
    chunks = embedding_for_chunk(chunks)

    # 4. Create FAISS index
    index = create_index(chunks)

    # 5. Generate document ID
    document_id = file.filename

    # 6. Store temporarily in memory
    documents[document_id] = {
        "index": index,
        "chunks": chunks
    }

    return {
        "document_id": document_id,
        "filename": file.filename,
        "chunks": len(chunks),
        "message": "Document processed successfully"
    }