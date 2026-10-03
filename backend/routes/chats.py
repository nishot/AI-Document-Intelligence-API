from fastapi import APIRouter
from pydantic import BaseModel

from services.embedding_service import generate_embedd
from services.vector_services import search
from services.llm_services import generate_answer

from routes.documents import documents


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    document_id: str
    question: str


@router.post("")
async def chat(request: ChatRequest):

    document = documents.get(request.document_id)

    if document is None:
        return {
            "error": "Document not found"
        }

    index = document["index"]
    chunks = document["chunks"]

    # Convert question to embedding
    query_embedding = generate_embedd(request.question)

    # Retrieve relevant chunks
    results = search(
        index,
        query_embedding,
        chunks,
        top_k=3
    )

    # Generate answer
    answer = generate_answer(
        request.question,
        results
    )

    sources = [
        {
            "page": result["chunk"]["page_no"],
            "distance": result["distance"]
        }
        for result in results
    ]

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources
    }