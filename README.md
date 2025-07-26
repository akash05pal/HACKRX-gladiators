# HackRx 6.0 LLM API

## Features
- FastAPI backend with async processing
- PDF/DOCX parsing with robust error handling
- Semantic search (FAISS or Pinecone)
- OpenAI GPT-4 with fallback to GPT-3.5-turbo
- Bearer token authentication
- Parallel question processing
- Response time optimization (<30s)
- Health check endpoints

## Tech Stack
- **Backend:** FastAPI
- **Vector DB:** FAISS (default) or Pinecone (optional)
- **LLM:** OpenAI GPT-4/3.5-turbo with automatic fallback
- **Document Processing:** pdfplumber, python-docx
- **Deployment:** Render/Heroku/Railway

## Setup
1. Clone the repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add a `.env` file:
   ```
   OPENAI_API_KEY=sk-...
   API_BEARER_TOKEN=your-secret-token
   USE_PINECONE=false  # Set to true for Pinecone
   PINECONE_API_KEY=your-pinecone-key  # Optional
   ```
4. Place your PDFs in the `downloads/` folder (for local testing)

## Running Locally
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Usage
- **POST** `/hackrx/run`
- **Headers:**
  - `Authorization: Bearer <api_key>`
- **Body:**
  ```json
  {
    "documents": "downloads/yourfile.pdf",
    "questions": ["Question 1", "Question 2"]
  }
  ```

## Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |
| `API_BEARER_TOKEN` | Yes | Secret token for authentication |
| `USE_PINECONE` | No | Set to "true" to use Pinecone instead of FAISS |
| `PINECONE_API_KEY` | No | Required if USE_PINECONE=true |

## Deployment
### Render/Heroku/Railway
- Deploy from GitHub
- Set environment variables in the platform's dashboard
- For Heroku/Render, ensure `Procfile` is present

## Example Request (curl)
```bash
curl -X POST "https://your-app-url/hackrx/run" \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: application/json" \
  -d '{"documents": "downloads/yourfile.pdf", "questions": ["What is covered?"]}'
```

## Health Check
- **GET** `/` - API status
- **GET** `/health` - Health check endpoint

## Performance
- Optimized for <30s response time
- Parallel question processing
- Automatic model fallback (GPT-4 → GPT-3.5-turbo)
- Efficient chunking and embedding 