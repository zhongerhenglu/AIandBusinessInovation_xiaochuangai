from typing import Dict, Any, List
from .document_store import DocumentStore
from .vector_store import ChromaVectorStore
from .structured_wiki import StructuredWiki
from .knowledge_schema import KnowledgeSchema
import logging

logger = logging.getLogger(__name__)


class KnowledgeBase:
    def __init__(self):
        self.document_store = DocumentStore()
        self.vector_store = ChromaVectorStore()
        self.wiki = StructuredWiki()
        self.schema = KnowledgeSchema()
    
    def ingest(self, documents: List[Dict[str, Any]]):
        for doc in documents:
            self.document_store.add(doc)
            
            embedding = self.vector_store.encode(doc.get('content', ''))
            self.vector_store.add(doc.get('id', str(hash(str(doc)))), embedding)
            
            extracted_knowledge = self._extract_knowledge(doc)
            if self.schema.validate(extracted_knowledge):
                self.wiki.add_entry(extracted_knowledge)
        
        logger.info(f"Ingested {len(documents)} documents")
    
    def query(self, query_text: str, context_type: str = 'general') -> str:
        query_vector = self.vector_store.encode(query_text)
        similar_docs = self.vector_store.search(query_vector, top_k=5)
        
        wiki_entries = self.wiki.search(query_text, context_type)
        
        return self._synthesize_knowledge(similar_docs, wiki_entries)
    
    def update(self, topic: str, content: str):
        wiki_entry = {
            'type': 'decision_page',
            'decision_id': topic,
            'timestamp': '',
            'context': '',
            'outcome': content
        }
        self.wiki.add_entry(wiki_entry)
        logger.info(f"Knowledge base updated: {topic}")
    
    def add_entry(self, entry: Dict[str, Any]):
        if self.schema.validate(entry):
            self.wiki.add_entry(entry)
    
    def _extract_knowledge(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        entry_type = self.schema.infer_type(doc)
        return {
            'type': entry_type,
            'id': doc.get('id', str(hash(str(doc)))),
            'content': doc.get('content', ''),
            'metadata': doc.get('metadata', {})
        }
    
    def _synthesize_knowledge(self, similar_docs: List[Dict[str, Any]], 
                             wiki_entries: List[Dict[str, Any]]) -> str:
        content_parts = []
        
        for doc in similar_docs[:3]:
            doc_content = self.document_store.get(doc['doc_id'])
            if doc_content:
                content_parts.append(doc_content.get('content', '')[:200])
        
        for entry in wiki_entries[:3]:
            content_parts.append(entry.get('content', '')[:200])
        
        return "\n\n".join(content_parts)