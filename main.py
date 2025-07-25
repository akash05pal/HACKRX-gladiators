from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from typing import List
import os
from utils.doc_loader import download_document, parse_document
from utils.chunker import chunk_text
from utils.embedder import embed_chunks
from utils.searcher import build_faiss_index, search_faiss_index
from utils.llm import generate_answer
import openai
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN")

class RunRequest(BaseModel):
    documents: str
    questions: List[str]

class RunResponse(BaseModel):
    answers: List[str]

@app.post("/hackrx/run", response_model=RunResponse)
async def hackrx_run(
    req: RunRequest,
    authorization: str = Header(None)
):
    # Bearer token authentication
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split("Bearer ", 1)[1].strip()
    if not API_BEARER_TOKEN or token != API_BEARER_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not set")
    try:
        # 1. Use local file if path is local, else download
        doc_path = req.documents
        if doc_path.startswith("downloads/") or os.path.isfile(doc_path):
            file_path = doc_path
            ext = file_path.split('.')[-1].lower()
            filetype = ext if ext in ["pdf", "docx"] else "unknown"
        else:
            file_path, filetype = download_document(req.documents)
        text = parse_document(file_path, filetype)
        # 2. Chunk text
        chunks = chunk_text(text)
        # 3. Embed chunks
        chunk_embeddings = embed_chunks(chunks, openai_api_key)
        # 4. Build FAISS index
        index = build_faiss_index(chunk_embeddings)
        answers = []
        for question in req.questions:
            # 5a. Embed question
            q_embedding = embed_chunks([question], openai_api_key)[0]
            # 5b. Search for top 3 relevant chunks
            top_indices, _ = search_faiss_index(index, q_embedding, top_k=3)
            relevant_chunks = [chunks[i] for i in top_indices]
            # 5c. Generate answer with LLM
            try:
                answer = generate_answer(question, relevant_chunks, openai_api_key)
            except Exception as e:
                answer = f"Could not generate answer due to error: {str(e)}"
            answers.append(answer)
        return RunResponse(answers=answers)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}") 