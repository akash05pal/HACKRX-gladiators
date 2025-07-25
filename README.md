# HackRx 6.0 LLM API

## Features
- FastAPI backend
- PDF/DOCX parsing
- Semantic search (FAISS)
- OpenAI GPT-4 answer generation
- Bearer token authentication

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

## Deployment
### Railway/Heroku/Render
- Deploy from GitHub
- Set `OPENAI_API_KEY` and `API_BEARER_TOKEN` in the platform's environment variables
- For Heroku/Render, ensure `Procfile` is present

## Example Request (curl)
```bash
curl -X POST "https://your-app-url/hackrx/run" \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: application/json" \
  -d '{"documents": "downloads/yourfile.pdf", "questions": ["What is covered?"]}'
``` 