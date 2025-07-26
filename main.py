from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from typing import List
import os
import asyncio
import time
from utils.doc_loader import download_document, parse_document
from utils.chunker import chunk_text
from utils.embedder import embed_chunks
from utils.searcher import build_faiss_index, search_faiss_index, build_pinecone_index, search_pinecone_index
from utils.llm import generate_answer
import openai
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="HackRx 6.0 API", description="LLM-powered document Q&A system")

API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN")
USE_PINECONE = os.getenv("USE_PINECONE", "false").lower() == "true"

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
    start_time = time.time()
    
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
        
        # 2. Parse document
        text = parse_document(file_path, filetype)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Document is empty or could not be parsed")
        
        # 3. Chunk text (optimized for speed)
        chunks = chunk_text(text, chunk_size=500, overlap=100)
        if not chunks:
            raise HTTPException(status_code=400, detail="No text chunks could be created")
        
        # 4. Embed chunks
        chunk_embeddings = embed_chunks(chunks, openai_api_key)
        
        # 5. Build search index (FAISS or Pinecone)
        if USE_PINECONE:
            try:
                index = build_pinecone_index(chunk_embeddings)
                search_func = search_pinecone_index
            except Exception as e:
                # Fall back to FAISS if Pinecone fails
                index = build_faiss_index(chunk_embeddings)
                search_func = search_faiss_index
        else:
            index = build_faiss_index(chunk_embeddings)
            search_func = search_faiss_index
        
        # 6. Process questions in parallel with timeout
        answers = []
        tasks = []
        
        for question in req.questions:
            # 6a. Embed question
            q_embedding = embed_chunks([question], openai_api_key)[0]
            
            # 6b. Search for relevant chunks
            top_indices, _ = search_func(index, q_embedding, top_k=2)
            relevant_chunks = [chunks[i] for i in top_indices if i < len(chunks)]
            
            # 6c. Create task for answer generation
            task = generate_answer(question, relevant_chunks, openai_api_key)
            tasks.append(task)
        
        # 6d. Wait for all answers with timeout
        try:
            answers = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=25.0  # 25 second timeout
            )
            # Handle any exceptions
            answers = [str(ans) if isinstance(ans, Exception) else ans for ans in answers]
        except asyncio.TimeoutError:
            answers = ["Error: Request timed out. Please try again."] * len(req.questions)
        except Exception as e:
            answers = [f"Error generating answer: {str(e)}"] * len(req.questions)
        
        # 7. Check response time
        total_time = time.time() - start_time
        if total_time > 30:
            print(f"Warning: Response time {total_time:.2f}s exceeds 30s limit")
        
        return RunResponse(answers=answers)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "HackRx 6.0 API is running", "endpoint": "/hackrx/run"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()} 