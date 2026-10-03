from google import genai
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL_NAME="gemini-3.7-flash"

def generate_answer(question:str,retrived_chunk:list[dict]):
    context="\n\n".join(
        f"[page {result['chunk']['page_no']}] {result['chunk']['text']} "for result in retrived_chunk
    )
    prompt = f"""
    You are a document question-answering assistant.

    Answer the question using ONLY the provided document context.

    Rules:
    - Do not use outside knowledge.
    - Do not invent information.
    - If the answer is not present in the context, say:
    "I could not find the answer in the provided document."
    - Mention the relevant page number when possible.

    DOCUMENT CONTEXT:
    {context}

    QUESTION:
    {question}
    """

    response=client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text


