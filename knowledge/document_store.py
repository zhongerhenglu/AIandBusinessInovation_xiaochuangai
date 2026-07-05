from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DocumentStore:
    def __init__(self):
        self.documents: Dict[str, Dict[str, Any]] = {}
    
    def add(self, document: Dict[str, Any]):
        doc_id = document.get('id', str(hash(str(document))))
        self.documents[doc_id] = {
            'id': doc_id,
            'content': document.get('content', ''),
            'metadata': document.get('metadata', {}),
            'created_at': document.get('created_at', datetime.now().isoformat())
        }
        logger.info(f"Document added: {doc_id}")
    
    def get(self, doc_id: str) -> Optional[Dict[str, Any]]:
        return self.documents.get(doc_id)
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        results = []
        for doc_id, doc in self.documents.items():
            if query.lower() in doc['content'].lower():
                results.append(doc)
        return results
    
    def delete(self, doc_id: str):
        if doc_id in self.documents:
            del self.documents[doc_id]
            logger.info(f"Document deleted: {doc_id}")
    
    def size(self) -> int:
        return len(self.documents)