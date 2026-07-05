from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import os
import logging

logger = logging.getLogger(__name__)


class WikiPage:
    def __init__(self, page_id: str, page_type: str, content: str, metadata: Dict[str, Any] = None):
        self.page_id = page_id
        self.page_type = page_type
        self.content = content
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.version = 1
        self.history: List[Dict[str, Any]] = []
    
    def update(self, new_content: str, commit_message: str = ""):
        self.history.append({
            'version': self.version,
            'content': self.content,
            'timestamp': self.updated_at.isoformat(),
            'commit_message': commit_message
        })
        self.content = new_content
        self.version += 1
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'page_id': self.page_id,
            'page_type': self.page_type,
            'content': self.content,
            'metadata': self.metadata,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'history_count': len(self.history)
        }


class VersionedWiki:
    def __init__(self, storage_path: str = None):
        self.pages: Dict[str, WikiPage] = {}
        self.page_types = ['entity', 'topic', 'comparison', 'decision', 'index', 'log', 'factor', 'strategy', 'analysis']
        self.storage_path = storage_path or os.path.join(os.path.dirname(__file__), 'wiki_storage')
        self._init_storage()
        self.load_from_storage()
    
    def _init_storage(self):
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, 'pages'), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, 'history'), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, 'index'), exist_ok=True)
    
    def add_page(self, page_id: str, page_type: str, content: str, metadata: Dict[str, Any] = None):
        if page_type not in self.page_types:
            raise ValueError(f"Unknown page type: {page_type}. Available types: {self.page_types}")
        
        if page_id in self.pages:
            self.update_page(page_id, content, f"Initial commit: {page_type} page")
            return
        
        page = WikiPage(page_id, page_type, content, metadata)
        self.pages[page_id] = page
        self._save_page(page)
        logger.info(f"Wiki page created: {page_id} ({page_type})")
    
    def update_page(self, page_id: str, content: str, commit_message: str = ""):
        if page_id not in self.pages:
            raise ValueError(f"Page not found: {page_id}")
        
        self.pages[page_id].update(content, commit_message)
        self._save_page(self.pages[page_id])
        logger.info(f"Wiki page updated: {page_id} (v{self.pages[page_id].version})")
    
    def get_page(self, page_id: str) -> Optional[WikiPage]:
        return self.pages.get(page_id)
    
    def get_page_content(self, page_id: str) -> Optional[str]:
        page = self.pages.get(page_id)
        return page.content if page else None
    
    def delete_page(self, page_id: str):
        if page_id in self.pages:
            page = self.pages.pop(page_id)
            self._delete_page_files(page_id)
            logger.info(f"Wiki page deleted: {page_id}")
    
    def search(self, query: str, page_type: str = None) -> List[WikiPage]:
        results = []
        for page in self.pages.values():
            match = (query.lower() in page.content.lower() or
                     query.lower() in page.page_id.lower() or
                     any(query.lower() in str(v).lower() for v in page.metadata.values()))
            
            if match and (page_type is None or page.page_type == page_type):
                results.append(page)
        
        results.sort(key=lambda p: p.updated_at, reverse=True)
        return results
    
    def get_pages_by_type(self, page_type: str) -> List[WikiPage]:
        return sorted(
            [p for p in self.pages.values() if p.page_type == page_type],
            key=lambda p: p.updated_at,
            reverse=True
        )
    
    def get_recent_updates(self, hours: int = 24) -> List[WikiPage]:
        cutoff = datetime.now() - timedelta(hours=hours)
        return sorted(
            [p for p in self.pages.values() if p.updated_at > cutoff],
            key=lambda p: p.updated_at,
            reverse=True
        )
    
    def get_stats(self) -> Dict[str, Any]:
        type_counts = {}
        for page in self.pages.values():
            type_counts[page.page_type] = type_counts.get(page.page_type, 0) + 1
        
        total_versions = sum(len(p.history) + 1 for p in self.pages.values())
        
        recent_updates = self.get_recent_updates(24)
        today_updates = sum(1 for p in self.pages.values() if p.updated_at.date() == datetime.now().date())
        
        return {
            'total_pages': len(self.pages),
            'total_versions': total_versions,
            'pages_by_type': type_counts,
            'recent_updates_24h': len(recent_updates),
            'today_updates': today_updates,
            'storage_path': self.storage_path
        }
    
    def get_change_log(self, hours: int = 24) -> List[Dict[str, Any]]:
        changes = []
        cutoff = datetime.now() - timedelta(hours=hours)
        
        for page in self.pages.values():
            if page.updated_at > cutoff:
                changes.append({
                    'page_id': page.page_id,
                    'page_type': page.page_type,
                    'version': page.version,
                    'updated_at': page.updated_at.isoformat(),
                    'metadata': page.metadata
                })
        
        changes.sort(key=lambda c: c['updated_at'], reverse=True)
        return changes
    
    def _save_page(self, page: WikiPage):
        page_data = page.to_dict()
        
        with open(os.path.join(self.storage_path, 'pages', f"{page.page_id}.json"), 'w', encoding='utf-8') as f:
            json.dump(page_data, f, ensure_ascii=False, indent=2)
        
        if page.history:
            history_path = os.path.join(self.storage_path, 'history', f"{page.page_id}_history.json")
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(page.history, f, ensure_ascii=False, indent=2)
        
        self._update_index()
    
    def _delete_page_files(self, page_id: str):
        files_to_delete = [
            os.path.join(self.storage_path, 'pages', f"{page_id}.json"),
            os.path.join(self.storage_path, 'history', f"{page_id}_history.json")
        ]
        
        for file_path in files_to_delete:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        self._update_index()
    
    def _update_index(self):
        index_data = {
            'pages': [p.page_id for p in self.pages.values()],
            'types': self.page_types,
            'updated_at': datetime.now().isoformat()
        }
        
        with open(os.path.join(self.storage_path, 'index', 'index.json'), 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    def load_from_storage(self):
        pages_dir = os.path.join(self.storage_path, 'pages')
        if not os.path.exists(pages_dir):
            return
        
        for filename in os.listdir(pages_dir):
            if filename.endswith('.json'):
                page_id = filename[:-5]
                try:
                    with open(os.path.join(pages_dir, filename), 'r', encoding='utf-8') as f:
                        page_data = json.load(f)
                    
                    page = WikiPage(
                        page_id=page_data['page_id'],
                        page_type=page_data['page_type'],
                        content=page_data['content'],
                        metadata=page_data.get('metadata', {})
                    )
                    page.version = page_data.get('version', 1)
                    page.created_at = datetime.fromisoformat(page_data['created_at'])
                    page.updated_at = datetime.fromisoformat(page_data['updated_at'])
                    
                    history_path = os.path.join(self.storage_path, 'history', f"{page_id}_history.json")
                    if os.path.exists(history_path):
                        with open(history_path, 'r', encoding='utf-8') as f:
                            page.history = json.load(f)
                    
                    self.pages[page_id] = page
                    logger.info(f"Loaded wiki page: {page_id}")
                except Exception as e:
                    logger.error(f"Failed to load page {page_id}: {str(e)}")
    
    def create_entity_page(self, entity_name: str, description: str, attributes: Dict[str, Any] = None):
        content = f"# {entity_name}\n\n## Description\n{description}\n\n## Attributes\n"
        if attributes:
            for key, value in attributes.items():
                content += f"- {key}: {value}\n"
        
        self.add_page(entity_name.lower().replace(' ', '_'), 'entity', content, {
            'entity_name': entity_name,
            'attributes': attributes or {}
        })
    
    def create_topic_page(self, topic_name: str, content: str, related_topics: List[str] = None):
        full_content = f"# {topic_name}\n\n{content}\n"
        if related_topics:
            full_content += f"\n## Related Topics\n"
            for topic in related_topics:
                full_content += f"- [[{topic}]]\n"
        
        self.add_page(topic_name.lower().replace(' ', '_'), 'topic', full_content, {
            'related_topics': related_topics or []
        })
    
    def create_factor_page(self, factor_name: str, definition: str, formula: str, 
                          category: str, ic_value: float = None):
        content = f"# {factor_name}\n\n## Definition\n{definition}\n\n## Formula\n```\n{formula}\n```\n\n## Category\n{category}\n"
        if ic_value is not None:
            content += f"\n## IC Value\n{ic_value:.4f}\n"
        
        self.add_page(f"factor_{factor_name.lower().replace(' ', '_')}", 'factor', content, {
            'factor_name': factor_name,
            'category': category,
            'ic_value': ic_value
        })
    
    def create_strategy_page(self, strategy_name: str, description: str, rules: List[str], 
                            parameters: Dict[str, Any] = None):
        content = f"# {strategy_name}\n\n## Description\n{description}\n\n## Rules\n"
        for i, rule in enumerate(rules, 1):
            content += f"{i}. {rule}\n"
        
        if parameters:
            content += "\n## Parameters\n"
            for key, value in parameters.items():
                content += f"- {key}: {value}\n"
        
        self.add_page(f"strategy_{strategy_name.lower().replace(' ', '_')}", 'strategy', content, {
            'strategy_name': strategy_name,
            'parameters': parameters or {}
        })
    
    def create_analysis_page(self, analysis_name: str, content: str, date: str = None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        page_content = f"# {analysis_name}\n\n## Date\n{date}\n\n## Content\n{content}"
        
        page_id = f"analysis_{date}_{analysis_name.lower().replace(' ', '_')}"
        self.add_page(page_id, 'analysis', page_content, {
            'analysis_name': analysis_name,
            'date': date
        })
    
    def create_decision_page(self, decision_id: str, context: str, outcome: str, 
                            timestamp: str = None):
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        content = f"# Decision: {decision_id}\n\n## Context\n{context}\n\n## Outcome\n{outcome}\n\n## Timestamp\n{timestamp}"
        
        self.add_page(f"decision_{decision_id.lower().replace(' ', '_')}", 'decision', content, {
            'decision_id': decision_id,
            'timestamp': timestamp
        })