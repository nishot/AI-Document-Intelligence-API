from pdf_service import extract_text_from_pdf
from chunking_service import create_chunk
from embedding_service import (
    generate_embedd,
    embedding_for_chunk
)
from vector_services import create_index, search
from llm_services import generate_answer

PDF_PATH = "D:/chapter_15_literature/Paper_2.pdf"


# 1. Extract
text_data = extract_text_from_pdf(PDF_PATH)

# 2. Chunk
chunks = create_chunk(text_data)

# 3. Embed document chunks
chunks = embedding_for_chunk(chunks)

# 4. Create FAISS index
index = create_index(chunks)

# 5. User question
question = "What is the proposed methodology of the study?"

# 6. Embed question
question_embedding = generate_embedd(question)

# 7. Retrieve
results = search(
    index,
    question_embedding,
    chunks,
    top_k=3
)

answer=generate_answer(question,results)

# 8. Display
print("\nQUESTION:")
print(question)
print(answer)

# for i, result in enumerate(results, start=1):

#     print(f"\n--- RESULT {i} ---")
#     print("Distance:", result["distance"])
#     print("Page:", result["chunk"]["page_no"])
#     print("Tokens:", result["chunk"]["token_count"])
#     print("Text:")
#     print(result["chunk"]["text"])