from fastapi import FastAPI
from routes.documents import router as documents_router
from routes.chats import router as chat_router

app = FastAPI(
    title="DocMind API",
    description="AI Document Intelligence and RAG API"
)

app.include_router(documents_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {
        "message": "DocMind API is running"
    }