from typing import Dict, Any, List, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.vectors: Dict[str, np.ndarray] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
    
    def encode(self, text: str) -> np.ndarray:
        hash_val = hash(text)
        np.random.seed(hash_val % 1000000)
        return np.random.randn(self.dimension).astype(np.float32)
    
    def add(self, doc_id: str, vector: np.ndarray, meta: Optional[Dict[str, Any]] = None):
        self.vectors[doc_id] = vector
        if meta:
            self.metadata[doc_id] = meta
    
    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        results = []
        for doc_id, vector in self.vectors.items():
            similarity = float(np.dot(query_vector, vector) / 
                              (np.linalg.norm(query_vector) * np.linalg.norm(vector)))
            results.append({
                "doc_id": doc_id,
                "similarity": similarity,
                "metadata": self.metadata.get(doc_id, {})
            })
        
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def get(self, doc_id: str) -> Optional[np.ndarray]:
        return self.vectors.get(doc_id)