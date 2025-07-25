import faiss
import numpy as np
from typing import List, Tuple

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