# DocMind

### AI-Powered Document Intelligence & RAG API

DocMind is a backend system for asking natural-language questions about PDF documents using **Retrieval-Augmented Generation (RAG)**.

Instead of sending an entire document to an LLM, DocMind extracts the document content, divides it into smaller chunks, converts those chunks into vector embeddings, retrieves the most relevant information using FAISS, and provides the retrieved context to Google's Gemini model to generate a grounded answer.

---

## Overview

DocMind allows users to:

- Upload PDF documents
- Extract text while preserving page information
- Split documents into manageable chunks
- Generate semantic embeddings
- Store and search embeddings using FAISS
- Retrieve the most relevant document sections for a question
- Generate answers using Gemini
- Return source page information with the answer
- Access the entire system through a FastAPI REST API

### Core Pipeline

```text
                ┌─────────────────┐
                │   PDF Document  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Text Extraction│
                │    PyMuPDF      │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │     Chunking    │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │    Embeddings   │
                │   MiniLM-L6-v2  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │      FAISS      │
                │  Vector Search  │
                └────────┬────────┘
                         ▲
                         │
                ┌────────┴────────┐
                │     Question    │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Question Vector │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Relevant Chunks │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │      Gemini     │
                │  Answer + Context│
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Answer + Sources│
                └─────────────────┘
```

---

## Features

### PDF Processing

- Upload PDF documents through a REST API
- Extract text using PyMuPDF
- Preserve page numbers for source attribution

### Intelligent Chunking

Documents are divided into smaller text chunks before embedding.

The current implementation uses a practical token-based chunking strategy designed around the embedding model's context limitations.

### Semantic Embeddings

DocMind uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The model generates **384-dimensional embeddings** for document chunks and user questions.

### Vector Search

FAISS is used for efficient similarity search over document embeddings.

The current implementation uses:

```text
FAISS IndexFlatL2
```

The top relevant chunks are retrieved for each question.

### Retrieval-Augmented Generation

The retrieved document context is passed to Gemini rather than sending the entire document.

The LLM is instructed to:

- Answer using the provided document context
- Avoid inventing information
- Indicate when the answer cannot be found
- Reference relevant page numbers

### REST API

The backend exposes endpoints for:

```text
POST /documents/upload
POST /chat
```

FastAPI's Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python |
| API Framework | FastAPI |
| PDF Processing | PyMuPDF |
| Embedding Model | all-MiniLM-L6-v2 |
| Embedding Framework | Sentence Transformers |
| Vector Database/Search | FAISS |
| LLM | Google Gemini API |
| API Documentation | Swagger / OpenAPI |
| Environment | Python virtual environment |

---

## Project Structure

```text
DocMind/
│
├── backend/
│   │
│   ├── main.py
│   │
│   ├── routes/
│   │   ├── documents.py
│   │   └── chat.py
│   │
│   ├── services/
│   │   ├── pdf_service.py
│   │   ├── chunking_service.py
│   │   ├── embedding_service.py
│   │   ├── vector_service.py
│   │   └── llm_services.py
│   │
│   ├── data/
│   │   └── uploads/
│   │
│   └── tests/
│
├── frontend/
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

# How It Works

## 1. Upload a Document

A user sends a PDF to:

```http
POST /documents/upload
```

The API saves the document and begins processing.

---

## 2. Extract Text

PyMuPDF extracts text from each page.

The extracted structure maintains page information:

```python
{
    "page_no": 2,
    "text": "..."
}
```

This allows retrieved information to be traced back to its original page.

---

## 3. Chunk the Document

Large documents are divided into smaller pieces.

Conceptually:

```text
Document
   ↓
Pages
   ↓
Text Blocks
   ↓
Chunks
```

Each chunk contains information such as:

```python
{
    "page_no": 2,
    "text": "...",
    "token_count": 300
}
```

---

## 4. Generate Embeddings

Each chunk is converted into a numerical vector using:

```text
all-MiniLM-L6-v2
```

Example:

```text
Text Chunk
    ↓
Embedding Model
    ↓
[0.023, -0.041, 0.087, ...]
```

The resulting vector contains 384 dimensions.

---

## 5. Build the FAISS Index

The document embeddings are added to a FAISS index.

```text
Chunk 1 → Vector 1
Chunk 2 → Vector 2
Chunk 3 → Vector 3
...
Chunk N → Vector N
```

When a user asks a question, the question is also converted into an embedding.

FAISS then searches for the closest document vectors.

---

## 6. Retrieve Relevant Context

For example:

```text
Question:
"What methodology was used in the study?"
```

The system retrieves the most relevant chunks.

Example:

```text
Page 2:
"The study employs a mixed-methods approach..."
```

Only these relevant chunks are sent to the LLM.

---

## 7. Generate the Answer

Gemini receives:

```text
Document Context
        +
User Question
```

The prompt instructs Gemini to answer using only the supplied document context.

The result is returned to the client along with source information.

---

# API Usage

## Upload Document

### Request

```http
POST /documents/upload
```

Multipart form-data:

```text
file = document.pdf
```

### Example Response

```json
{
    "document_id": "Paper_2.pdf",
    "filename": "Paper_2.pdf",
    "chunks": 42,
    "message": "Document processed successfully"
}
```

---

## Ask a Question

### Request

```http
POST /chat
```

### JSON Body

```json
{
    "document_id": "Paper_2.pdf",
    "question": "What methodology was used in the study?"
}
```

### Example Response

```json
{
    "question": "What methodology was used in the study?",
    "answer": "The study employs a mixed-methods approach...",
    "sources": [
        {
            "page": 2,
            "distance": 1.59
        },
        {
            "page": 3,
            "distance": 1.73
        }
    ]
}
```

---

# Installation

## 1. Clone the Repository

```bash
git clone <your-repository-url>
cd DocumentIntelligenceAPI
```

---

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If you are installing manually:

```bash
pip install fastapi
pip install uvicorn
pip install pymupdf
pip install sentence-transformers
pip install faiss-cpu
pip install google-genai
pip install python-multipart
pip install python-dotenv
```

---

# Environment Variables

Create a `.env` file inside `backend/`:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Do **not** commit this file to Git.

Add it to `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
data/uploads/
```

---

# Running the API

From the `backend` directory:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Running the Frontend

Start the API first, then serve the static frontend from the repository root:

```powershell
python -m http.server 5173 --directory frontend
```

Open `http://127.0.0.1:5173` in a browser. The frontend uses `http://127.0.0.1:8000` by default and supports PDF upload, grounded questions, and source-page citations. If the API runs elsewhere, set `window.DOCMIND_API_URL` before loading `frontend/app.js`.

---

# Example Workflow

### Step 1 — Upload

```text
POST /documents/upload
```

Upload:

```text
research-paper.pdf
```

The backend processes the document and creates the vector index.

### Step 2 — Ask

```text
POST /chat
```

```json
{
    "document_id": "research-paper.pdf",
    "question": "What methodology was used?"
}
```

### Step 3 — Retrieve

FAISS finds the most relevant chunks.

### Step 4 — Generate

Gemini generates an answer using those chunks.

### Step 5 — Return Sources

The API returns the answer together with the relevant document pages.

---

# Design Decisions

## Why RAG?

Sending an entire document directly to an LLM is inefficient and makes it harder to control which information is used.

RAG separates the process into:

```text
Retrieval
    +
Generation
```

This allows the system to first identify relevant information and then generate an answer based on that information.

---

## Why FAISS?

FAISS provides a lightweight local vector-search solution that is suitable for the first version of the project.

It also allows the retrieval pipeline to be developed without immediately introducing a hosted vector database.

---

## Why MiniLM?

`all-MiniLM-L6-v2` is relatively lightweight and produces 384-dimensional embeddings, making it practical for local CPU-based development.

---

## Why Gemini?

Gemini handles the final natural-language generation while the local retrieval system determines which document information is relevant.

This creates a clear separation:

```text
MiniLM → Retrieval
Gemini → Generation
```

---

# Current Limitations

This is currently an MVP.

### Vector Persistence

FAISS indexes are currently kept in memory.

Restarting the API removes the indexes.

### Document Storage

Documents and indexes are not yet backed by a persistent database.

### Chunking

The current chunking strategy is intentionally simple and can be improved for better semantic boundaries.

### Multi-User Support

Authentication and user-specific document isolation are not currently implemented.

### OCR

Image-only/scanned PDFs are not currently processed using OCR.

### Frontend

The repository now includes a dependency-free frontend in `frontend/` for uploading PDFs, asking questions, and viewing grounded page citations.

---

# Future Improvements

Planned improvements include:

- Persistent vector indexes
- PostgreSQL document metadata
- Better semantic chunking
- Hybrid keyword + vector retrieval
- Cosine similarity
- Reranking
- Conversation history
- Streaming LLM responses
- Better source citations
- Document deletion
- Multiple document collections
- Authentication and authorization
- OCR for scanned documents
- Evaluation metrics for retrieval quality
- Automated tests
- Production deployment
- Frontend interface

---

# RAG Architecture

The complete system can be summarized as:

```text
                    DOCUMENT INGESTION

PDF
 │
 ▼
PyMuPDF
 │
 ▼
Text Extraction
 │
 ▼
Chunking
 │
 ▼
MiniLM Embeddings
 │
 ▼
FAISS Index
 │
 ▼
Stored Document Context


                     QUERY PIPELINE

User Question
 │
 ▼
MiniLM Embedding
 │
 ▼
FAISS Similarity Search
 │
 ▼
Top-K Relevant Chunks
 │
 ▼
Gemini
 │
 ▼
Grounded Answer
 │
 ▼
Source Pages
```

---

# Project Status

### Backend MVP

- [x] PDF upload
- [x] PDF text extraction
- [x] Page-aware text processing
- [x] Document chunking
- [x] Embedding generation
- [x] FAISS vector indexing
- [x] Semantic retrieval
- [x] Gemini integration
- [x] RAG question answering
- [x] FastAPI upload endpoint
- [x] FastAPI chat endpoint
- [x] Source page information
- [ ] Persistent storage
- [ ] Authentication
- [ ] Advanced retrieval
- [x] Frontend
- [ ] Production deployment

---

# Learning Outcomes

This project demonstrates practical implementation of:

- Retrieval-Augmented Generation
- Natural Language Processing
- Text embeddings
- Vector similarity search
- FAISS
- Transformer models
- LLM integration
- Prompt engineering
- PDF processing
- FastAPI
- REST API design
- Backend service architecture

---

## License

This project is intended for learning, experimentation, and portfolio development.

Add an appropriate license before distributing the project publicly.