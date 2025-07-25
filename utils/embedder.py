import openai
from typing import List

def embed_chunks(chunks: List[str], openai_api_key: str) -> List[list]:
    client = openai.OpenAI(api_key=openai_api_key)
    embeddings = []
    for chunk in chunks:
        response = client.embeddings.create(
            input=chunk,
            model="text-embedding-ada-002"
        )
        embeddings.append(response.data[0].embedding)
    return embeddings 