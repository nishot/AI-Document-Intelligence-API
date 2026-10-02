from fastapi import FastAPI
from routes import chats, documents

app = FastAPI(title="AI Document Intelligence API")

@app.get("/")
def read_root():
    return {"message": "AI Document Intelligence API is running"}