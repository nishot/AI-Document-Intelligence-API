from sentence_transformers import SentenceTransformer
from .chunking_service import create_chunk
from .pdf_service import extract_text_from_pdf

model=SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def generate_embedd(text):
    embedd=model.encode(text)
    return embedd.tolist()

def embedding_for_chunk(chunks):
    text=[chunk['text'] for chunk in chunks]
    embeddings=generate_embedd(text)

    for chunk , embedding in zip(chunks,embeddings):
        chunk['embedding']=embedding

    return chunks

if __name__ == "__main__":

    text_data = extract_text_from_pdf(
        "D:/chapter_15_literature/Paper_2.pdf"
    )

    chunks = create_chunk(text_data)

    chunks = embedding_for_chunk(chunks)

    print("Number of chunks:", len(chunks))
    print("Embedding size:", len(chunks[0]["embedding"]))
    print("First 5 values:", chunks[0]["embedding"][:5])