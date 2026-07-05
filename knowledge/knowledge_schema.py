from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class KnowledgeSchema:
    def __init__(self):
        self.schemas = {
            'entity_page': {
                'required': ['entity_id', 'name', 'type', 'attributes', 'sources'],
                'optional': ['related_entities', 'historical_data', 'analysis']
            },
            'topic_page': {
                'required': ['topic_id', 'name', 'description', 'subtopics'],
                'optional': ['related_topics', 'best_practices', 'case_studies']
            },
            'decision_page': {
                'required': ['decision_id', 'timestamp', 'context', 'outcome'],
                'optional': ['review_comments', 'lessons_learned', 'improvements']
            },
            'comparison_page': {
                'required': ['comparison_id', 'items', 'dimensions', 'results'],
                'optional': ['conclusion', 'recommendations']
            }
        }
    
    def validate(self, entry: Dict[str, Any]) -> bool:
        entry_type = entry.get('type')
        if entry_type not in self.schemas:
            return False
        
        schema = self.schemas[entry_type]
        required_fields = schema.get('required', [])
        return all(field in entry for field in required_fields)
    
    def infer_type(self, doc: Dict[str, Any]) -> str:
        content = doc.get('content', '')
        if any(keyword in content.lower() for keyword in ['stock', 'company', 'ticker']):
            return 'entity_page'
        elif any(keyword in content.lower() for keyword in ['strategy', 'method', 'approach']):
            return 'topic_page'
        elif any(keyword in content.lower() for keyword in ['decision', 'action', 'trade']):
            return 'decision_page'
        elif any(keyword in content.lower() for keyword in ['compare', 'vs', 'benchmark']):
            return 'comparison_page'
        return 'topic_page'