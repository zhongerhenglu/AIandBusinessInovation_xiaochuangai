from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StructuredWiki:
    def __init__(self):
        self.pages: Dict[str, Dict[str, Any]] = {}
        self.page_types = ['entity', 'topic', 'comparison', 'decision', 'index', 'log']
    
    def add_entry(self, entry: Dict[str, Any]):
        entry_type = entry.get('type', 'topic')
        if entry_type not in self.page_types:
            raise ValueError(f"Unknown page type: {entry_type}")
        
        page_id = entry.get('id', str(hash(str(entry))))
        self.pages[page_id] = {
            'id': page_id,
            'type': entry_type,
            'content': entry.get('content', ''),
            'metadata': entry.get('metadata', {}),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        logger.info(f"Wiki entry added: {page_id} ({entry_type})")
    
    def update_entry(self, page_id: str, content: str):
        if page_id in self.pages:
            self.pages[page_id]['content'] = content
            self.pages[page_id]['updated_at'] = datetime.now().isoformat()
            logger.info(f"Wiki entry updated: {page_id}")
    
    def search(self, query: str, context_type: str = 'general') -> List[Dict[str, Any]]:
        results = []
        for page_id, page in self.pages.items():
            if (query.lower() in page['content'].lower() or 
                query.lower() in str(page.get('metadata', {})).lower()):
                if context_type == 'general' or page['type'] == context_type:
                    results.append(page)
        return results
    
    def get_page(self, page_id: str) -> Optional[Dict[str, Any]]:
        return self.pages.get(page_id)
    
    def get_pages_by_type(self, page_type: str) -> List[Dict[str, Any]]:
        return [page for page in self.pages.values() if page['type'] == page_type]