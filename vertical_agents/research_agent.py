import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain.agent_base import BaseAgent
from research.document_parser import DocumentParserFactory
from research.keyword_extractor import KeywordExtractor
from research.chart_analyzer import ChartAnalyzer
from research.report_fetcher import ReportManager

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("ResearchAgent")
        self.document_parser = DocumentParserFactory()
        self.keyword_extractor = KeywordExtractor()
        self.chart_analyzer = ChartAnalyzer()
        self.report_manager = ReportManager()
        self.analysis_cache = {}
    
    def execute(self, task_type: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"ResearchAgent executing task: {task_type}")
        
        try:
            if task_type == 'fetch_reports':
                return self._fetch_reports(inputs)
            elif task_type == 'analyze_report':
                return self._analyze_report(inputs)
            elif task_type == 'extract_keywords':
                return self._extract_keywords(inputs)
            elif task_type == 'analyze_charts':
                return self._analyze_charts(inputs)
            elif task_type == 'summarize_report':
                return self._summarize_report(inputs)
            elif task_type == 'batch_analyze':
                return self._batch_analyze(inputs)
            else:
                return {'error': f"Unknown task type: {task_type}"}
        except Exception as e:
            logger.error(f"ResearchAgent error: {str(e)}", exc_info=True)
            return {'error': str(e)}
    
    def _fetch_reports(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        source = inputs.get('source', 'all')
        symbol = inputs.get('symbol')
        date = inputs.get('date')
        limit = inputs.get('limit', 10)
        
        reports = self.report_manager.get_reports(
            source=source,
            symbol=symbol,
            date=date,
            limit=limit
        )
        
        return {
            'reports': reports,
            'count': len(reports),
            'source': source,
        }
    
    def _analyze_report(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        report_path = inputs.get('file_path')
        
        if not report_path or not os.path.exists(report_path):
            report_id = inputs.get('report_id')
            if report_id:
                report_detail = self.report_manager.get_report_detail(report_id)
                if report_detail and 'filepath' in report_detail:
                    report_path = report_detail['filepath']
        
        if not report_path or not os.path.exists(report_path):
            return {'error': f"Report not found: {report_path}"}
        
        cached = self.analysis_cache.get(report_path)
        if cached:
            return cached
        
        parsed = self.document_parser.parse(report_path)
        
        if 'error' in parsed:
            return parsed
        
        keywords = self.keyword_extractor.extract_keywords(parsed['text'], top_n=20)
        key_sentences = self.keyword_extractor.extract_sentences(parsed['text'], max_sentences=10)
        entities = self.keyword_extractor.extract_entities(parsed['text'])
        numeric_info = self.keyword_extractor.extract_numeric_info(parsed['text'])
        
        chart_analysis = self.chart_analyzer.analyze_tables(parsed.get('tables', []))
        chart_descriptions = self.chart_analyzer.extract_chart_descriptions(parsed['text'])
        
        analysis = {
            'report_id': os.path.basename(report_path).replace('.pdf', ''),
            'file_path': report_path,
            'title': parsed.get('metadata', {}).get('title', os.path.basename(report_path)),
            'metadata': parsed.get('metadata', {}),
            'text_length': len(parsed['text']),
            'tables_count': len(parsed.get('tables', [])),
            'images_count': len(parsed.get('images', [])),
            'keywords': keywords,
            'key_sentences': key_sentences,
            'entities': entities,
            'numeric_info': numeric_info,
            'chart_analysis': chart_analysis,
            'chart_descriptions': chart_descriptions,
        }
        analysis['summary'] = self._generate_summary(analysis)
        
        self.analysis_cache[report_path] = analysis
        return analysis
    
    def _extract_keywords(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        text = inputs.get('text', '')
        
        if not text:
            report_path = inputs.get('file_path')
            if report_path and os.path.exists(report_path):
                parsed = self.document_parser.parse(report_path)
                text = parsed.get('text', '')
        
        if not text:
            return {'error': 'No text provided'}
        
        keywords = self.keyword_extractor.extract_keywords(text, top_n=inputs.get('top_n', 20))
        entities = self.keyword_extractor.extract_entities(text)
        numeric_info = self.keyword_extractor.extract_numeric_info(text)
        
        return {
            'keywords': keywords,
            'entities': entities,
            'numeric_info': numeric_info,
            'keyword_count': len(keywords),
        }
    
    def _analyze_charts(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        report_path = inputs.get('file_path')
        
        if not report_path or not os.path.exists(report_path):
            return {'error': f"Report not found: {report_path}"}
        
        parsed = self.document_parser.parse(report_path)
        
        if 'error' in parsed:
            return parsed
        
        table_analysis = self.chart_analyzer.analyze_tables(parsed.get('tables', []))
        chart_descriptions = self.chart_analyzer.extract_chart_descriptions(parsed['text'])
        
        return {
            'tables': table_analysis,
            'tables_count': len(table_analysis),
            'chart_descriptions': chart_descriptions,
            'charts_count': len(chart_descriptions),
        }
    
    def _summarize_report(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        analysis = self._analyze_report(inputs)
        
        if 'error' in analysis:
            return analysis
        
        summary = self._generate_summary(analysis)
        
        return {
            'title': analysis['title'],
            'summary': summary,
            'keywords': [k['keyword'] for k in analysis['keywords'][:10]],
            'key_findings': self._extract_key_findings(analysis),
        }
    
    def _batch_analyze(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        report_ids = inputs.get('report_ids', [])
        report_paths = inputs.get('report_paths', [])
        
        all_reports = []
        
        for report_id in report_ids:
            detail = self.report_manager.get_report_detail(report_id)
            if detail and 'filepath' in detail:
                all_reports.append(detail['filepath'])
        
        for path in report_paths:
            if os.path.exists(path):
                all_reports.append(path)
        
        results = []
        for report_path in all_reports[:20]:
            try:
                analysis = self._analyze_report({'file_path': report_path})
                results.append(analysis)
            except Exception as e:
                logger.error(f"Error analyzing {report_path}: {str(e)}")
                results.append({'error': str(e), 'file_path': report_path})
        
        return {
            'total_reports': len(all_reports),
            'analyzed_count': len(results),
            'results': results,
            'comprehensive_summary': self._generate_comprehensive_summary(results),
        }
    
    def _generate_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        keywords = [k['keyword'] for k in analysis.get('keywords', [])[:10]]
        key_sentences = [s['sentence'] for s in analysis.get('key_sentences', [])[:5]]
        numeric_info = analysis.get('numeric_info', [])[:5]
        chart_descriptions = [c['title'] for c in analysis.get('chart_descriptions', [])[:5]]
        
        return {
            'keywords': keywords,
            'key_points': key_sentences,
            'numeric_data': numeric_info,
            'charts': chart_descriptions,
            'word_count': analysis.get('text_length', 0),
            'estimated_reading_time': f"{analysis.get('text_length', 0) // 300} minutes",
        }
    
    def _extract_key_findings(self, analysis: Dict[str, Any]) -> List[str]:
        findings = []
        
        keywords = analysis.get('keywords', [])
        for kw in keywords[:5]:
            findings.append(f"核心关键词: {kw['keyword']} (权重: {kw['weight']:.4f})")
        
        numeric_info = analysis.get('numeric_info', [])
        for num in numeric_info[:5]:
            findings.append(f"{num['label']}: {num['value']}")
        
        chart_analysis = analysis.get('chart_analysis', [])
        for chart in chart_analysis[:3]:
            key_findings = chart.get('key_findings', [])
            findings.extend(key_findings[:2])
        
        return findings[:10]
    
    def _generate_comprehensive_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        all_keywords = []
        all_numeric_info = []
        all_chart_types = []
        
        for result in results:
            if 'error' in result:
                continue
            
            all_keywords.extend(result.get('keywords', []))
            all_numeric_info.extend(result.get('numeric_info', []))
            chart_analysis = result.get('chart_analysis', [])
            for chart in chart_analysis:
                all_chart_types.append(chart.get('type', 'unknown'))
        
        keyword_counts = {}
        for kw in all_keywords:
            keyword = kw['keyword']
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:15]
        
        return {
            'total_reports': len(results),
            'top_keywords': [{'keyword': k, 'count': c} for k, c in sorted_keywords],
            'numeric_summary': self._summarize_numeric_info(all_numeric_info),
        }
    
    def _summarize_numeric_info(self, numeric_info: List[Dict[str, Any]]) -> Dict[str, Any]:
        summary = {}
        for num in numeric_info:
            label = num['label']
            value = num['value']
            
            if label not in summary:
                summary[label] = []
            summary[label].append(value)
        
        for label in summary:
            values = summary[label]
            summary[label] = {
                'count': len(values),
                'avg': float(sum(values) / len(values)),
                'max': float(max(values)),
                'min': float(min(values)),
            }
        
        return summary
    
    def run(self, task_type: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return self.execute(task_type, inputs)