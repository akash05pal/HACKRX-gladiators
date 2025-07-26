import faiss
import numpy as np
from typing import List, Tuple
import os

def build_faiss_index(embeddings: List[list]) -> faiss.IndexFlatL2:
    """
    Build a FAISS index from a list of embedding vectors.
    """
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    np_embeddings = np.array(embeddings).astype('float32')
    index.add(np_embeddings)
    return index

def search_faiss_index(index: faiss.IndexFlatL2, query_embedding: list, top_k: int = 3) -> Tuple[List[int], List[float]]:
    """
    Search the FAISS index for the top_k most similar embeddings.
    Returns indices and distances.
    """
    query = np.array([query_embedding]).astype('float32')
    distances, indices = index.search(query, top_k)
    return indices[0].tolist(), distances[0].tolist()

# Optional Pinecone support
def build_pinecone_index(embeddings: List[list], index_name: str = "hackrx-index"):
    """
    Build a Pinecone index (requires PINECONE_API_KEY environment variable).
    """
    try:
        import pinecone
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        if not pinecone_api_key:
            raise Exception("PINECONE_API_KEY not set")
        
        pinecone.init(api_key=pinecone_api_key, environment="us-west1-gcp")
        
        # Create index if it doesn't exist
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=len(embeddings[0]),
                metric="cosine"
            )
        
        index = pinecone.Index(index_name)
        
        # Upsert embeddings
        vectors = [(f"chunk_{i}", embedding) for i, embedding in enumerate(embeddings)]
        index.upsert(vectors=vectors)
        
        return index
    except ImportError:
        raise Exception("pinecone-client not installed. Use FAISS instead.")

def search_pinecone_index(index, query_embedding: list, top_k: int = 3):
    """
    Search Pinecone index for similar embeddings.
    """
    try:
        results = index.query(vector=query_embedding, top_k=top_k, include_metadata=False)
        indices = [int(result.id.split('_')[1]) for result in results.matches]
        scores = [result.score for result in results.matches]
        return indices, scores
    except Exception as e:
        raise Exception(f"Pinecone search error: {str(e)}") 