from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from .versioned_wiki import VersionedWiki
from .knowledge_graph import KnowledgeGraph
from .document_store import DocumentStore
from .vector_store import ChromaVectorStore
from .knowledge_schema import KnowledgeSchema

logger = logging.getLogger(__name__)


class EnhancedKnowledgeBase:
    def __init__(self):
        self.wiki = VersionedWiki()
        self.graph = KnowledgeGraph()
        self.document_store = DocumentStore()
        self.vector_store = ChromaVectorStore()
        self.schema = KnowledgeSchema()
        
        self._initialize_default_pages()
    
    def _initialize_default_pages(self):
        self.wiki.create_topic_page(
            'A股市场分析框架',
            '基于多因子模型和宏观情景分析的A股市场研究框架。包括因子分析、行业轮动、风险评估等核心模块。',
            ['多因子模型', '宏观情景分析', '风险评估']
        )
        
        self.wiki.create_topic_page(
            '多因子模型',
            '基于动量、估值、质量、波动率、流动性等因子构建的量化选股模型。',
            ['动量因子', '估值因子', '质量因子']
        )
        
        self.wiki.create_factor_page('ROC_5', '5日收益率变化率', 'ROC_5 = (Close - Close_5) / Close_5', 'momentum')
        self.wiki.create_factor_page('ROC_20', '20日收益率变化率', 'ROC_20 = (Close - Close_20) / Close_20', 'momentum')
        self.wiki.create_factor_page('PB_ratio', '市净率', 'PB = MarketCap / BookValue', 'value')
        self.wiki.create_factor_page('ROE', '净资产收益率', 'ROE = NetProfit / ShareholderEquity', 'quality')
        
        self.graph.build_factor_knowledge('ROC_5', 'momentum', '5日收益率变化率', ['ROC_20'])
        self.graph.build_factor_knowledge('ROC_20', 'momentum', '20日收益率变化率', ['ROC_5'])
        self.graph.build_factor_knowledge('PB_ratio', 'value', '市净率')
        self.graph.build_factor_knowledge('ROE', 'quality', '净资产收益率')
    
    def ingest_document(self, document: Dict[str, Any]):
        doc_id = document.get('id', str(hash(str(document))))
        
        self.document_store.add(document)
        
        content = document.get('content', '')
        if content:
            embedding = self.vector_store.encode(content)
            self.vector_store.add(doc_id, embedding)
        
        self._extract_and_store_knowledge(document)
        
        logger.info(f"Ingested document: {doc_id}")
    
    def _extract_and_store_knowledge(self, doc: Dict[str, Any]):
        content = doc.get('content', '')
        metadata = doc.get('metadata', {})
        
        if 'stock_code' in metadata and 'stock_name' in metadata:
            self.wiki.create_entity_page(
                metadata['stock_name'],
                content[:200],
                metadata
            )
            self.graph.build_stock_knowledge(
                metadata['stock_code'],
                metadata['stock_name'],
                metadata.get('industry', 'unknown'),
                metadata.get('sector', 'unknown'),
                metadata.get('market_cap', 0),
                metadata.get('factors', [])
            )
        
        elif 'factor_name' in metadata:
            self.wiki.create_factor_page(
                metadata['factor_name'],
                content[:200],
                metadata.get('formula', ''),
                metadata.get('category', 'other'),
                metadata.get('ic_value')
            )
            self.graph.build_factor_knowledge(
                metadata['factor_name'],
                metadata.get('category', 'other'),
                content[:200],
                metadata.get('related_factors')
            )
    
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
    
    def update_wiki_page(self, page_id: str, content: str, commit_message: str = ""):
        self.wiki.update_page(page_id, content, commit_message)
    
    def create_analysis_report(self, report_name: str, content: str, date: str = None):
        self.wiki.create_analysis_page(report_name, content, date)
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        self.graph.add_node(
            f"analysis_{date}_{report_name.lower().replace(' ', '_')}",
            'analysis',
            {'name': report_name, 'date': date}
        )
    
    def get_stats(self) -> Dict[str, Any]:
        wiki_stats = self.wiki.get_stats()
        graph_stats = self.graph.get_stats()
        
        return {
            'wiki': wiki_stats,
            'graph': graph_stats,
            'documents': self.document_store.size(),
            'total_knowledge_items': wiki_stats['total_pages'] + graph_stats['total_nodes'] + self.document_store.size(),
            'updated_at': datetime.now().isoformat()
        }
    
    def get_recent_updates(self, hours: int = 24) -> Dict[str, Any]:
        wiki_updates = self.wiki.get_recent_updates(hours)
        change_log = self.wiki.get_change_log(hours)
        
        return {
            'wiki_updates': [p.to_dict() for p in wiki_updates],
            'change_log': change_log,
            'update_count': len(wiki_updates)
        }
    
    def get_knowledge_summary(self) -> str:
        stats = self.get_stats()
        
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
        
        if stats['wiki']['recent_updates_24h'] > 0:
            summary.append(f"\n### 📝 最近24小时更新")
            summary.append(f"- 更新次数: {stats['wiki']['recent_updates_24h']}")
            summary.append(f"- 今日更新: {stats['wiki']['today_updates']}")
        
        return "\n".join(summary)
    
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