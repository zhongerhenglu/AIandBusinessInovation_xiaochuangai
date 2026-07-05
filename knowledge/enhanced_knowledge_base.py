from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from .versioned_wiki import VersionedWiki
from .knowledge_graph import KnowledgeGraph
from .document_store import DocumentStore
from .vector_store import ChromaVectorStore
from .knowledge_schema import KnowledgeSchema
from .knowledge_change_logger import KnowledgeChangeLogger

logger = logging.getLogger(__name__)


class EnhancedKnowledgeBase:
    def __init__(self):
        self.wiki = VersionedWiki()
        self.graph = KnowledgeGraph()
        self.document_store = DocumentStore()
        self.vector_store = ChromaVectorStore()
        self.schema = KnowledgeSchema()
        self.change_logger = KnowledgeChangeLogger()
        
        self._initialize_default_pages()
    
    def _initialize_default_pages(self):
        default_pages = [
            ('A股市场分析框架', 'topic', '基于多因子模型和宏观情景分析的A股市场研究框架。包括因子分析、行业轮动、风险评估等核心模块。', ['多因子模型', '宏观情景分析', '风险评估']),
            ('多因子模型', 'topic', '基于动量、估值、质量、波动率、流动性等因子构建的量化选股模型。', ['动量因子', '估值因子', '质量因子']),
        ]
        
        default_factors = [
            ('ROC_5', '5日收益率变化率', 'ROC_5 = (Close - Close_5) / Close_5', 'momentum'),
            ('ROC_20', '20日收益率变化率', 'ROC_20 = (Close - Close_20) / Close_20', 'momentum'),
            ('PB_ratio', '市净率', 'PB = MarketCap / BookValue', 'value'),
            ('ROE', '净资产收益率', 'ROE = NetProfit / ShareholderEquity', 'quality'),
        ]
        
        for name, page_type, content, related in default_pages:
            page_id = name.lower().replace(' ', '_')
            if self.wiki.get_page(page_id) is None:
                self.wiki.create_topic_page(name, content, related)
                self.change_logger.log_wiki_page_create(page_id, page_type, {'related_topics': related})
        
        for name, definition, formula, category in default_factors:
            page_id = f"factor_{name.lower().replace(' ', '_')}"
            if self.wiki.get_page(page_id) is None:
                self.wiki.create_factor_page(name, definition, formula, category)
                self.change_logger.log_wiki_page_create(page_id, 'factor', {'category': category})
                self.graph.build_factor_knowledge(name, category, definition)
                self.change_logger.log_graph_node_add(name.lower(), 'factor', {'name': name, 'category': category})
    
    def ingest_document(self, document: Dict[str, Any]):
        doc_id = document.get('id', str(hash(str(document))))
        doc_title = document.get('title', doc_id)
        doc_type = document.get('type', 'document')
        
        self.document_store.add(document)
        
        content = document.get('content', '')
        extracted_entities = 0
        extracted_relations = 0
        
        if content:
            embedding = self.vector_store.encode(content)
            self.vector_store.add(doc_id, embedding)
        
        extracted_entities, extracted_relations = self._extract_and_store_knowledge(document)
        
        self.change_logger.log_knowledge_ingest(
            doc_title, doc_type, extracted_entities, extracted_relations
        )
        
        logger.info(f"Ingested document: {doc_id}")
    
    def _extract_and_store_knowledge(self, doc: Dict[str, Any]) -> tuple:
        content = doc.get('content', '')
        metadata = doc.get('metadata', {})
        extracted_entities = 0
        extracted_relations = 0
        
        if 'stock_code' in metadata and 'stock_name' in metadata:
            page_id = metadata['stock_name'].lower().replace(' ', '_')
            if self.wiki.get_page(page_id) is None:
                self.wiki.create_entity_page(
                    metadata['stock_name'],
                    content[:200],
                    metadata
                )
                self.change_logger.log_wiki_page_create(page_id, 'entity', metadata)
                extracted_entities += 1
            
            self.graph.build_stock_knowledge(
                metadata['stock_code'],
                metadata['stock_name'],
                metadata.get('industry', 'unknown'),
                metadata.get('sector', 'unknown'),
                metadata.get('market_cap', 0),
                metadata.get('factors', [])
            )
            self.change_logger.log_graph_node_add(
                metadata['stock_name'].lower(), 'stock', metadata
            )
            extracted_entities += 1
            
            factors = metadata.get('factors', [])
            for factor in factors:
                self.change_logger.log_graph_edge_add(
                    metadata['stock_name'].lower(), factor.lower(), 'related_to'
                )
                extracted_relations += 1
        
        elif 'factor_name' in metadata:
            page_id = f"factor_{metadata['factor_name'].lower().replace(' ', '_')}"
            if self.wiki.get_page(page_id) is None:
                self.wiki.create_factor_page(
                    metadata['factor_name'],
                    content[:200],
                    metadata.get('formula', ''),
                    metadata.get('category', 'other'),
                    metadata.get('ic_value')
                )
                self.change_logger.log_wiki_page_create(page_id, 'factor', metadata)
                extracted_entities += 1
            
            self.graph.build_factor_knowledge(
                metadata['factor_name'],
                metadata.get('category', 'other'),
                content[:200],
                metadata.get('related_factors')
            )
            self.change_logger.log_graph_node_add(
                metadata['factor_name'].lower(), 'factor', metadata
            )
            extracted_entities += 1
            
            related_factors = metadata.get('related_factors', [])
            for rf in related_factors:
                self.change_logger.log_graph_edge_add(
                    metadata['factor_name'].lower(), rf.lower(), 'related_to'
                )
                extracted_relations += 1
        
        return extracted_entities, extracted_relations
    
    def update_wiki_page(self, page_id: str, content: str, commit_message: str = ""):
        page = self.wiki.get_page(page_id)
        if page:
            old_version = page.version
            self.wiki.update_page(page_id, content, commit_message)
            self.change_logger.log_wiki_page_update(
                page_id, page.page_type, page.version, commit_message
            )
            logger.info(f"Updated wiki page: {page_id} (v{old_version} -> v{page.version})")
    
    def delete_wiki_page(self, page_id: str):
        page = self.wiki.get_page(page_id)
        if page:
            page_type = page.page_type
            self.wiki.delete_page(page_id)
            self.change_logger.log_wiki_page_delete(page_id, page_type)
            logger.info(f"Deleted wiki page: {page_id}")
    
    def create_analysis_report(self, report_name: str, content: str, date: str = None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        page_id = f"analysis_{date}_{report_name.lower().replace(' ', '_')}"
        
        if self.wiki.get_page(page_id) is None:
            self.wiki.create_analysis_page(report_name, content, date)
            self.change_logger.log_wiki_page_create(page_id, 'analysis', {'date': date})
            
            self.graph.add_node(page_id, 'analysis', {'name': report_name, 'date': date})
            self.change_logger.log_graph_node_add(page_id, 'analysis', {'name': report_name, 'date': date})
    
    def update_factor_data(self, factor_name: str, ic_value: float = None, 
                          ir_value: float = None, category: str = None):
        self.change_logger.log_factor_update(factor_name, ic_value, ir_value, category)
        
        page_id = f"factor_{factor_name.lower().replace(' ', '_')}"
        page = self.wiki.get_page(page_id)
        if page:
            new_content = page.content
            if ic_value is not None:
                new_content = new_content.replace(
                    '## IC Value\n', 
                    f'## IC Value\n{ic_value:.4f}\n'
                )
            self.update_wiki_page(page_id, new_content, f"Update {factor_name} IC/IR values")
    
    def query(self, query_text: str, top_k: int = 5) -> Dict[str, Any]:
        query_vector = self.vector_store.encode(query_text)
        similar_docs = self.vector_store.search(query_vector, top_k=top_k)
        
        wiki_results = self.wiki.search(query_text)
        graph_results = self.graph.search(query_text)
        
        return {
            'similar_documents': similar_docs[:top_k],
            'wiki_pages': [p.to_dict() for p in wiki_results[:top_k]],
            'graph_nodes': [{'id': nid, 'node': node} for nid, node in graph_results[:top_k]],
            'summary': self._generate_summary(query_text, similar_docs, wiki_results, graph_results)
        }
    
    def _generate_summary(self, query: str, docs, wiki_pages, graph_nodes) -> str:
        parts = []
        
        if wiki_pages:
            parts.append(f"## Wiki相关内容 ({len(wiki_pages)}条)")
            for page in wiki_pages[:3]:
                parts.append(f"- **[{page.page_id}]** ({page.page_type}): {page.content[:100]}...")
        
        if docs:
            parts.append(f"\n## 文档匹配 ({len(docs)}条)")
            for doc in docs[:3]:
                stored_doc = self.document_store.get(doc['doc_id'])
                if stored_doc:
                    parts.append(f"- {stored_doc.get('content', '')[:100]}...")
        
        if graph_nodes:
            parts.append(f"\n## 知识图谱 ({len(graph_nodes)}条)")
            for nid, node in graph_nodes[:3]:
                parts.append(f"- **{nid}**: {node.get('properties', {}).get('name', node.get('type', ''))}")
        
        return "\n".join(parts) if parts else "未找到相关知识"
    
    def get_stats(self) -> Dict[str, Any]:
        wiki_stats = self.wiki.get_stats()
        graph_stats = self.graph.get_stats()
        change_summary = self.change_logger.get_change_summary(24)
        
        return {
            'wiki': wiki_stats,
            'graph': graph_stats,
            'documents': self.document_store.size(),
            'total_knowledge_items': wiki_stats['total_pages'] + graph_stats['total_nodes'] + self.document_store.size(),
            'updated_at': datetime.now().isoformat(),
            'total_pages': wiki_stats['total_pages'],
            'total_nodes': graph_stats['total_nodes'],
            'today_updates': wiki_stats['today_updates'],
            'today_changes': change_summary['total_changes']
        }
    
    def get_recent_updates(self, hours: int = 24) -> Dict[str, Any]:
        wiki_updates = self.wiki.get_recent_updates(hours)
        change_log = self.wiki.get_change_log(hours)
        recent_changes = self.change_logger.get_recent_changes(hours)
        
        return {
            'wiki_updates': [p.to_dict() for p in wiki_updates],
            'change_log': change_log,
            'recent_changes': recent_changes,
            'update_count': len(wiki_updates),
            'change_count': len(recent_changes)
        }
    
    def get_knowledge_summary(self) -> str:
        stats = self.get_stats()
        change_report = self.change_logger.generate_change_report(24)
        
        summary = []
        summary.append("## 📚 知识体系概览")
        summary.append(f"- **总知识条目**: {stats['total_knowledge_items']}")
        summary.append(f"- **Wiki页面**: {stats['wiki']['total_pages']}")
        summary.append(f"- **图谱节点**: {stats['graph']['total_nodes']}")
        summary.append(f"- **图谱边**: {stats['graph']['total_edges']}")
        summary.append(f"- **文档数量**: {stats['documents']}")
        
        if stats['wiki']['pages_by_type']:
            summary.append("\n### 📁 Wiki页面分类")
            for page_type, count in stats['wiki']['pages_by_type'].items():
                summary.append(f"- {page_type}: {count}页")
        
        if stats['graph']['nodes_by_type']:
            summary.append("\n### 🔗 图谱节点分类")
            for node_type, count in stats['graph']['nodes_by_type'].items():
                summary.append(f"- {node_type}: {count}个节点")
        
        summary.append(f"\n{change_report}")
        
        return "\n".join(summary)
    
    def get_change_report(self, hours: int = 24) -> str:
        return self.change_logger.generate_change_report(hours)
    
    def search_knowledge(self, query: str) -> Dict[str, Any]:
        wiki_results = self.wiki.search(query)
        graph_results = self.graph.search(query)
        doc_results = self.document_store.search(query)
        
        return {
            'query': query,
            'wiki_results': [p.to_dict() for p in wiki_results],
            'graph_results': [{'id': nid, 'node': node} for nid, node in graph_results],
            'document_results': doc_results,
            'total_results': len(wiki_results) + len(graph_results) + len(doc_results)
        }