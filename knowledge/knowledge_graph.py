from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import os
import logging

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    def __init__(self, storage_path: str = None):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
        self.storage_path = storage_path or os.path.join(os.path.dirname(__file__), 'graph_storage')
        self._init_storage()
        self.load_from_storage()
    
    def _init_storage(self):
        os.makedirs(self.storage_path, exist_ok=True)
    
    def add_node(self, node_id: str, node_type: str, properties: Dict[str, Any] = None):
        if node_id in self.nodes:
            self.update_node(node_id, properties)
            return
        
        self.nodes[node_id] = {
            'id': node_id,
            'type': node_type,
            'properties': properties or {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        logger.info(f"Graph node added: {node_id} ({node_type})")
    
    def update_node(self, node_id: str, properties: Dict[str, Any]):
        if node_id not in self.nodes:
            raise ValueError(f"Node not found: {node_id}")
        
        self.nodes[node_id]['properties'].update(properties)
        self.nodes[node_id]['updated_at'] = datetime.now().isoformat()
        logger.info(f"Graph node updated: {node_id}")
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        return self.nodes.get(node_id)
    
    def delete_node(self, node_id: str):
        if node_id in self.nodes:
            del self.nodes[node_id]
            self.edges = [e for e in self.edges if e['source'] != node_id and e['target'] != node_id]
            logger.info(f"Graph node deleted: {node_id}")
    
    def add_edge(self, source: str, target: str, relation_type: str, properties: Dict[str, Any] = None):
        if source not in self.nodes or target not in self.nodes:
            raise ValueError("Source or target node not found")
        
        edge = {
            'source': source,
            'target': target,
            'relation_type': relation_type,
            'properties': properties or {},
            'created_at': datetime.now().isoformat()
        }
        
        self.edges.append(edge)
        logger.info(f"Graph edge added: {source} -{relation_type}-> {target}")
    
    def get_edges(self, node_id: str = None, relation_type: str = None) -> List[Dict[str, Any]]:
        edges = self.edges
        
        if node_id:
            edges = [e for e in edges if e['source'] == node_id or e['target'] == node_id]
        
        if relation_type:
            edges = [e for e in edges if e['relation_type'] == relation_type]
        
        return edges
    
    def get_neighbors(self, node_id: str) -> List[Dict[str, Any]]:
        neighbors = []
        for edge in self.edges:
            if edge['source'] == node_id:
                neighbor = self.nodes.get(edge['target'])
                if neighbor:
                    neighbors.append({**neighbor, 'relation': edge['relation_type']})
            elif edge['target'] == node_id:
                neighbor = self.nodes.get(edge['source'])
                if neighbor:
                    neighbors.append({**neighbor, 'relation': edge['relation_type']})
        
        return neighbors
    
    def search(self, query: str) -> List[Tuple[str, Dict[str, Any]]]:
        results = []
        
        for node_id, node in self.nodes.items():
            if (query.lower() in node_id.lower() or
                query.lower() in node['type'].lower() or
                any(query.lower() in str(v).lower() for v in node['properties'].values())):
                results.append((node_id, node))
        
        return results
    
    def get_nodes_by_type(self, node_type: str) -> List[Dict[str, Any]]:
        return [node for node in self.nodes.values() if node['type'] == node_type]
    
    def get_path(self, source: str, target: str, max_depth: int = 3) -> List[str]:
        visited = {source}
        queue = [(source, [source])]
        
        while queue:
            node, path = queue.pop(0)
            
            if node == target:
                return path
            
            if len(path) > max_depth:
                continue
            
            for edge in self.get_edges(node):
                next_node = edge['target'] if edge['source'] == node else edge['source']
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, path + [next_node]))
        
        return []
    
    def get_stats(self) -> Dict[str, Any]:
        type_counts = {}
        for node in self.nodes.values():
            type_counts[node['type']] = type_counts.get(node['type'], 0) + 1
        
        relation_counts = {}
        for edge in self.edges:
            relation_counts[edge['relation_type']] = relation_counts.get(edge['relation_type'], 0) + 1
        
        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'nodes_by_type': type_counts,
            'edges_by_relation': relation_counts
        }
    
    def save_to_storage(self):
        data = {
            'nodes': self.nodes,
            'edges': self.edges,
            'saved_at': datetime.now().isoformat()
        }
        
        with open(os.path.join(self.storage_path, 'knowledge_graph.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Knowledge graph saved: {len(self.nodes)} nodes, {len(self.edges)} edges")
    
    def load_from_storage(self):
        graph_file = os.path.join(self.storage_path, 'knowledge_graph.json')
        if not os.path.exists(graph_file):
            return
        
        try:
            with open(graph_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.nodes = data.get('nodes', {})
            self.edges = data.get('edges', [])
            logger.info(f"Knowledge graph loaded: {len(self.nodes)} nodes, {len(self.edges)} edges")
        except Exception as e:
            logger.error(f"Failed to load knowledge graph: {str(e)}")
    
    def build_stock_knowledge(self, stock_code: str, stock_name: str, industry: str, 
                             sector: str, market_cap: float, factors: List[str] = None):
        stock_node_id = f"stock_{stock_code}"
        self.add_node(stock_node_id, 'stock', {
            'name': stock_name,
            'code': stock_code,
            'industry': industry,
            'sector': sector,
            'market_cap': market_cap,
            'update_date': datetime.now().strftime('%Y-%m-%d')
        })
        
        industry_node_id = f"industry_{industry.lower().replace(' ', '_')}"
        self.add_node(industry_node_id, 'industry', {'name': industry})
        self.add_edge(stock_node_id, industry_node_id, 'belongs_to')
        
        sector_node_id = f"sector_{sector.lower().replace(' ', '_')}"
        self.add_node(sector_node_id, 'sector', {'name': sector})
        self.add_edge(stock_node_id, sector_node_id, 'in_sector')
        
        if factors:
            for factor_name in factors:
                factor_node_id = f"factor_{factor_name.lower().replace(' ', '_')}"
                self.add_node(factor_node_id, 'factor', {'name': factor_name})
                self.add_edge(stock_node_id, factor_node_id, 'related_to')
    
    def build_factor_knowledge(self, factor_name: str, category: str, 
                               definition: str, related_factors: List[str] = None):
        factor_node_id = f"factor_{factor_name.lower().replace(' ', '_')}"
        self.add_node(factor_node_id, 'factor', {
            'name': factor_name,
            'category': category,
            'definition': definition
        })
        
        category_node_id = f"category_{category.lower().replace(' ', '_')}"
        self.add_node(category_node_id, 'factor_category', {'name': category})
        self.add_edge(factor_node_id, category_node_id, 'belongs_to')
        
        if related_factors:
            for related_name in related_factors:
                related_node_id = f"factor_{related_name.lower().replace(' ', '_')}"
                self.add_node(related_node_id, 'factor', {'name': related_name})
                self.add_edge(factor_node_id, related_node_id, 'related_to')