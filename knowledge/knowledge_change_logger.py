from typing import Dict, Any, List
from datetime import datetime, timedelta
import json
import os
import logging

logger = logging.getLogger(__name__)


class KnowledgeChangeLogger:
    def __init__(self, log_dir: str = None):
        self.log_dir = log_dir or os.path.join(os.path.dirname(__file__), 'change_logs')
        os.makedirs(self.log_dir, exist_ok=True)
        self.change_history: List[Dict[str, Any]] = []
        self._load_history()
    
    def log_change(self, change_type: str, entity_type: str, entity_id: str, 
                   details: Dict[str, Any] = None, commit_message: str = ""):
        change_entry = {
            'timestamp': datetime.now().isoformat(),
            'change_type': change_type,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'details': details or {},
            'commit_message': commit_message
        }
        
        self.change_history.append(change_entry)
        
        log_file = os.path.join(self.log_dir, f"changes_{datetime.now().strftime('%Y-%m-%d')}.json")
        
        try:
            existing_logs = []
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    existing_logs = json.load(f)
            
            existing_logs.append(change_entry)
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(existing_logs, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Knowledge change logged: [{change_type}] {entity_type}:{entity_id}")
            
        except Exception as e:
            logger.error(f"Failed to log knowledge change: {str(e)}")
    
    def log_wiki_page_create(self, page_id: str, page_type: str, metadata: Dict[str, Any] = None):
        self.log_change(
            change_type='CREATE',
            entity_type='wiki_page',
            entity_id=page_id,
            details={
                'page_type': page_type,
                'metadata': metadata or {}
            },
            commit_message=f"Create {page_type} page: {page_id}"
        )
    
    def log_wiki_page_update(self, page_id: str, page_type: str, version: int, 
                            commit_message: str = ""):
        self.log_change(
            change_type='UPDATE',
            entity_type='wiki_page',
            entity_id=page_id,
            details={
                'page_type': page_type,
                'version': version
            },
            commit_message=commit_message or f"Update {page_type} page: {page_id} (v{version})"
        )
    
    def log_wiki_page_delete(self, page_id: str, page_type: str):
        self.log_change(
            change_type='DELETE',
            entity_type='wiki_page',
            entity_id=page_id,
            details={
                'page_type': page_type
            },
            commit_message=f"Delete {page_type} page: {page_id}"
        )
    
    def log_graph_node_add(self, node_id: str, node_type: str, properties: Dict[str, Any] = None):
        self.log_change(
            change_type='ADD',
            entity_type='graph_node',
            entity_id=node_id,
            details={
                'node_type': node_type,
                'properties': properties or {}
            },
            commit_message=f"Add graph node: {node_id} ({node_type})"
        )
    
    def log_graph_node_update(self, node_id: str, node_type: str, changes: Dict[str, Any] = None):
        self.log_change(
            change_type='UPDATE',
            entity_type='graph_node',
            entity_id=node_id,
            details={
                'node_type': node_type,
                'changes': changes or {}
            },
            commit_message=f"Update graph node: {node_id} ({node_type})"
        )
    
    def log_graph_edge_add(self, source: str, target: str, relation_type: str):
        self.log_change(
            change_type='ADD',
            entity_type='graph_edge',
            entity_id=f"{source}-{relation_type}->{target}",
            details={
                'source': source,
                'target': target,
                'relation_type': relation_type
            },
            commit_message=f"Add edge: {source} -{relation_type}-> {target}"
        )
    
    def log_factor_update(self, factor_name: str, ic_value: float = None, 
                         ir_value: float = None, category: str = None):
        details = {}
        if ic_value is not None:
            details['ic_value'] = ic_value
        if ir_value is not None:
            details['ir_value'] = ir_value
        if category:
            details['category'] = category
        
        self.log_change(
            change_type='UPDATE',
            entity_type='factor',
            entity_id=factor_name,
            details=details,
            commit_message=f"Update factor data: {factor_name}"
        )
    
    def log_knowledge_ingest(self, document_title: str, document_type: str, 
                            extracted_entities: int = 0, extracted_relations: int = 0):
        self.log_change(
            change_type='INGEST',
            entity_type='document',
            entity_id=document_title,
            details={
                'document_type': document_type,
                'extracted_entities': extracted_entities,
                'extracted_relations': extracted_relations
            },
            commit_message=f"Ingest document: {document_title}"
        )
    
    def get_recent_changes(self, hours: int = 24) -> List[Dict[str, Any]]:
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_changes = [
            change for change in self.change_history
            if datetime.fromisoformat(change['timestamp']) > cutoff
        ]
        recent_changes.sort(key=lambda c: c['timestamp'], reverse=True)
        return recent_changes
    
    def get_today_changes(self) -> List[Dict[str, Any]]:
        today = datetime.now().date()
        today_changes = [
            change for change in self.change_history
            if datetime.fromisoformat(change['timestamp']).date() == today
        ]
        today_changes.sort(key=lambda c: c['timestamp'], reverse=True)
        return today_changes
    
    def get_changes_by_type(self, change_type: str = None, entity_type: str = None) -> List[Dict[str, Any]]:
        filtered = self.change_history
        
        if change_type:
            filtered = [c for c in filtered if c['change_type'] == change_type]
        
        if entity_type:
            filtered = [c for c in filtered if c['entity_type'] == entity_type]
        
        filtered.sort(key=lambda c: c['timestamp'], reverse=True)
        return filtered
    
    def get_change_summary(self, hours: int = 24) -> Dict[str, Any]:
        recent_changes = self.get_recent_changes(hours)
        
        summary = {
            'total_changes': len(recent_changes),
            'by_change_type': {},
            'by_entity_type': {},
            'changes': recent_changes[:20]
        }
        
        for change in recent_changes:
            summary['by_change_type'][change['change_type']] = \
                summary['by_change_type'].get(change['change_type'], 0) + 1
            
            summary['by_entity_type'][change['entity_type']] = \
                summary['by_entity_type'].get(change['entity_type'], 0) + 1
        
        return summary
    
    def generate_change_report(self, hours: int = 24) -> str:
        summary = self.get_change_summary(hours)
        
        sections = []
        sections.append(f"## 📝 知识库更改记录 ({hours}小时内)")
        sections.append(f"**总更改数**: {summary['total_changes']}")
        
        if summary['by_change_type']:
            sections.append("\n### 更改类型分布")
            for change_type, count in summary['by_change_type'].items():
                icon = {
                    'CREATE': '🆕',
                    'ADD': '➕',
                    'UPDATE': '🔄',
                    'DELETE': '🗑️',
                    'INGEST': '📥'
                }.get(change_type, '📋')
                sections.append(f"- {icon} **{change_type}**: {count} 次")
        
        if summary['by_entity_type']:
            sections.append("\n### 实体类型分布")
            for entity_type, count in summary['by_entity_type'].items():
                sections.append(f"- **{entity_type}**: {count} 次")
        
        if summary['changes']:
            sections.append("\n### 详细更改记录")
            for i, change in enumerate(summary['changes'][:10], 1):
                timestamp = datetime.fromisoformat(change['timestamp'])
                time_str = timestamp.strftime('%H:%M:%S')
                icon = {
                    'CREATE': '🆕',
                    'ADD': '➕',
                    'UPDATE': '🔄',
                    'DELETE': '🗑️',
                    'INGEST': '📥'
                }.get(change['change_type'], '📋')
                
                commit_msg = change.get('commit_message', '')
                if commit_msg:
                    sections.append(f"{i}. {icon} {time_str} | {commit_msg}")
                else:
                    sections.append(f"{i}. {icon} {time_str} | {change['entity_type']}: {change['entity_id']}")
        
        if summary['total_changes'] == 0:
            sections.append("\n暂无更改记录")
        
        return '\n\n'.join(sections)
    
    def _load_history(self):
        try:
            for filename in os.listdir(self.log_dir):
                if filename.startswith('changes_') and filename.endswith('.json'):
                    filepath = os.path.join(self.log_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            changes = json.load(f)
                            self.change_history.extend(changes)
                    except Exception as e:
                        logger.warning(f"Failed to load change log {filename}: {str(e)}")
            
            self.change_history.sort(key=lambda c: c['timestamp'], reverse=True)
            logger.info(f"Loaded {len(self.change_history)} change records")
            
        except Exception as e:
            logger.error(f"Failed to load change history: {str(e)}")