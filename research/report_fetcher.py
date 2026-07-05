import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ReportFetcher(ABC):
    @abstractmethod
    def fetch_reports(self, symbol: str = None, date: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def fetch_report_detail(self, report_id: str) -> Optional[Dict[str, Any]]:
        pass


class LocalReportFetcher(ReportFetcher):
    def __init__(self, report_dir: str = None):
        if report_dir is None:
            report_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '课程大报告论文')
        self.report_dir = report_dir
        logger.info(f"Local report fetcher initialized with directory: {self.report_dir}")
    
    def fetch_reports(self, symbol: str = None, date: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        reports = []
        
        if not os.path.exists(self.report_dir):
            logger.warning(f"Report directory not found: {self.report_dir}")
            return reports
        
        for filename in os.listdir(self.report_dir):
            if filename.endswith('.pdf'):
                filepath = os.path.join(self.report_dir, filename)
                report_info = self._extract_report_info(filename, filepath)
                reports.append(report_info)
        
        if symbol:
            reports = [r for r in reports if symbol.lower() in r['title'].lower()]
        
        reports.sort(key=lambda x: x.get('date', datetime.now()), reverse=True)
        
        return reports[:limit]
    
    def _extract_report_info(self, filename: str, filepath: str) -> Dict[str, Any]:
        file_size = os.path.getsize(filepath)
        mtime = os.path.getmtime(filepath)
        modified_date = datetime.fromtimestamp(mtime)
        
        title = filename.replace('.pdf', '')
        title = title.replace('-', ' ')
        title = title.replace('_', ' ')
        
        category = self._classify_report(title)
        
        return {
            'report_id': os.path.splitext(filename)[0],
            'title': title,
            'filename': filename,
            'filepath': filepath,
            'file_size': file_size,
            'file_size_human': self._format_file_size(file_size),
            'date': modified_date,
            'date_str': modified_date.strftime('%Y-%m-%d'),
            'category': category,
            'source': 'local',
        }
    
    def _classify_report(self, title: str) -> str:
        if any(kw in title for kw in ['Barra', '风险因子']):
            return 'risk_factor'
        elif any(kw in title for kw in ['Fama-French', '三因子']):
            return 'factor_model'
        elif any(kw in title for kw in ['LLM', '大语言模型']):
            return 'llm_research'
        elif any(kw in title for kw in ['高频', 'tick']):
            return 'high_frequency'
        elif any(kw in title for kw in ['机器学习', 'ML', '神经网络']):
            return 'machine_learning'
        elif any(kw in title for kw in ['基本面', '财务', '现金流']):
            return 'fundamental'
        elif any(kw in title for kw in ['遗传算法']):
            return 'genetic_algorithm'
        elif any(kw in title for kw in ['组合优化', 'portfolio']):
            return 'portfolio_optimization'
        elif any(kw in title for kw in ['Winners', 'Losers', '动量']):
            return 'momentum_strategy'
        else:
            return 'general_research'
    
    def _format_file_size(self, size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
    
    def fetch_report_detail(self, report_id: str) -> Optional[Dict[str, Any]]:
        filepath = os.path.join(self.report_dir, f"{report_id}.pdf")
        
        if not os.path.exists(filepath):
            for filename in os.listdir(self.report_dir):
                if filename.startswith(report_id) and filename.endswith('.pdf'):
                    filepath = os.path.join(self.report_dir, filename)
                    break
        
        if not os.path.exists(filepath):
            logger.warning(f"Report not found: {report_id}")
            return None
        
        return self._extract_report_info(os.path.basename(filepath), filepath)


class MockAPIFetcher(ReportFetcher):
    def __init__(self):
        self.mock_reports = self._generate_mock_reports()
    
    def _generate_mock_reports(self) -> List[Dict[str, Any]]:
        today = datetime.now()
        reports = []
        
        institutions = ['中信证券', '中金公司', '国泰君安', '华泰证券', '海通证券']
        sectors = ['科技', '金融', '消费', '医药', '新能源']
        
        for i in range(30):
            date = today - timedelta(days=i % 10)
            reports.append({
                'report_id': f"RPT{2026070000 + i}",
                'title': f"{sectors[i % 5]}行业{['深度研究', '投资策略', '估值分析', '业绩点评', '行业展望'][i % 5]}报告",
                'institution': institutions[i % 5],
                'author': f"分析师{'张' if i % 2 == 0 else '李'}{chr(ord('A') + i % 26)}",
                'date': date,
                'date_str': date.strftime('%Y-%m-%d'),
                'rating': ['买入', '增持', '中性', '减持'][i % 4],
                'target_price': round(10 + i * 2.5, 2),
                'source': 'api',
                'url': f"https://api.example.com/reports/RPT{2026070000 + i}",
            })
        
        return reports
    
    def fetch_reports(self, symbol: str = None, date: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        reports = self.mock_reports.copy()
        
        if symbol:
            reports = [r for r in reports if symbol in r['title']]
        
        if date:
            reports = [r for r in reports if r['date_str'] == date]
        
        reports.sort(key=lambda x: x['date'], reverse=True)
        
        return reports[:limit]
    
    def fetch_report_detail(self, report_id: str) -> Optional[Dict[str, Any]]:
        for report in self.mock_reports:
            if report['report_id'] == report_id:
                return report
        return None


class ReportFetcherFactory:
    @classmethod
    def get_fetcher(cls, source: str = 'local') -> ReportFetcher:
        if source == 'api':
            return MockAPIFetcher()
        else:
            return LocalReportFetcher()


class ReportManager:
    def __init__(self):
        self.local_fetcher = LocalReportFetcher()
        self.api_fetcher = MockAPIFetcher()
        self.report_cache = {}
    
    def get_reports(self, source: str = 'all', symbol: str = None, date: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        reports = []
        
        if source in ['local', 'all']:
            reports.extend(self.local_fetcher.fetch_reports(symbol, date, limit))
        
        if source in ['api', 'all']:
            reports.extend(self.api_fetcher.fetch_reports(symbol, date, limit))
        
        reports.sort(key=lambda x: x.get('date', datetime.now()), reverse=True)
        
        return reports[:limit]
    
    def get_report_detail(self, report_id: str, source: str = 'all') -> Optional[Dict[str, Any]]:
        cached = self.report_cache.get(report_id)
        if cached:
            return cached
        
        detail = self.local_fetcher.fetch_report_detail(report_id)
        if detail:
            self.report_cache[report_id] = detail
            return detail
        
        detail = self.api_fetcher.fetch_report_detail(report_id)
        if detail:
            self.report_cache[report_id] = detail
            return detail
        
        return None
    
    def get_report_categories(self) -> Dict[str, int]:
        reports = self.get_reports(source='all', limit=100)
        categories = {}
        
        for report in reports:
            cat = report.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        return categories
    
    def search_reports(self, query: str) -> List[Dict[str, Any]]:
        reports = self.get_reports(source='all', limit=100)
        
        results = []
        for report in reports:
            title = report.get('title', '')
            if query.lower() in title.lower():
                results.append(report)
        
        return results