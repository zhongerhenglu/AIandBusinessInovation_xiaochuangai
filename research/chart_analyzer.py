import re
import logging
from typing import Dict, Any, List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class ChartAnalyzer:
    def analyze_tables(self, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not tables:
            return []
        
        results = []
        for table in tables:
            analysis = self._analyze_single_table(table)
            if analysis:
                results.append(analysis)
        
        return results
    
    def _analyze_single_table(self, table: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data = table.get('data', [])
        if not data or len(data) < 2:
            return None
        
        analysis = {
            'page': table.get('page', 0),
            'table_index': table.get('table_index', 0),
            'rows': table.get('rows', 0),
            'columns': table.get('columns', 0),
            'type': self._detect_table_type(data),
            'headers': data[0] if data else [],
            'summary': {},
            'key_findings': [],
        }
        
        if analysis['type'] == 'factor_table':
            analysis['summary'] = self._analyze_factor_table(data)
        elif analysis['type'] == 'financial_table':
            analysis['summary'] = self._analyze_financial_table(data)
        elif analysis['type'] == 'comparison_table':
            analysis['summary'] = self._analyze_comparison_table(data)
        elif analysis['type'] == 'return_table':
            analysis['summary'] = self._analyze_return_table(data)
        else:
            analysis['summary'] = self._analyze_general_table(data)
        
        analysis['key_findings'] = self._extract_key_findings(data, analysis['type'])
        
        return analysis
    
    def _detect_table_type(self, data: List[List[str]]) -> str:
        headers = [str(h).lower() for h in data[0]]
        
        if any('因子' in h or 'factor' in h or 'ic' in h or 'ir' in h for h in headers):
            return 'factor_table'
        
        if any('pe' in h or 'pb' in h or 'roe' in h or 'roa' in h or 'eps' in h for h in headers):
            return 'financial_table'
        
        if any('收益率' in h or 'return' in h or '收益' in h for h in headers):
            return 'return_table'
        
        if len(data) > 5 and len(data[0]) > 3:
            return 'comparison_table'
        
        return 'general_table'
    
    def _analyze_factor_table(self, data: List[List[str]]) -> Dict[str, Any]:
        headers = data[0]
        ic_col_idx = -1
        ir_col_idx = -1
        
        for i, h in enumerate(headers):
            if 'ic' in str(h).lower():
                ic_col_idx = i
            elif 'ir' in str(h).lower():
                ir_col_idx = i
        
        ic_values = []
        ir_values = []
        factor_names = []
        
        for row in data[1:]:
            factor_names.append(row[0])
            if ic_col_idx >= 0 and ic_col_idx < len(row):
                try:
                    ic_values.append(float(row[ic_col_idx].replace('%', '').replace('-', '0')))
                except ValueError:
                    pass
            if ir_col_idx >= 0 and ir_col_idx < len(row):
                try:
                    ir_values.append(float(row[ir_col_idx].replace('%', '').replace('-', '0')))
                except ValueError:
                    pass
        
        return {
            'factor_count': len(factor_names),
            'avg_ic': float(np.mean(ic_values)) if ic_values else None,
            'avg_ir': float(np.mean(ir_values)) if ir_values else None,
            'high_ic_factors': [factor_names[i] for i, v in enumerate(ic_values) if abs(v) > 0.3],
            'low_ic_factors': [factor_names[i] for i, v in enumerate(ic_values) if abs(v) < 0.1],
        }
    
    def _analyze_financial_table(self, data: List[List[str]]) -> Dict[str, Any]:
        headers = data[0]
        metrics = {}
        
        for row in data[1:]:
            if not row or not row[0]:
                continue
            
            metric_name = row[0]
            values = []
            for val in row[1:]:
                try:
                    values.append(float(val.replace('%', '').replace(',', '')))
                except ValueError:
                    continue
            
            if values:
                metrics[metric_name] = {
                    'values': values,
                    'latest': values[-1],
                    'avg': float(np.mean(values)),
                    'trend': 'up' if len(values) >= 2 and values[-1] > values[-2] else 'down' if len(values) >= 2 else 'stable',
                }
        
        return {
            'metrics_count': len(metrics),
            'metrics': metrics,
        }
    
    def _analyze_comparison_table(self, data: List[List[str]]) -> Dict[str, Any]:
        headers = data[0]
        categories = []
        best_performers = {}
        
        for col_idx, header in enumerate(headers[1:]):
            col_values = []
            for row in data[1:]:
                if col_idx + 1 < len(row):
                    try:
                        col_values.append(float(row[col_idx + 1].replace('%', '').replace(',', '')))
                    except ValueError:
                        pass
            
            if col_values:
                best_performers[header] = {
                    'avg': float(np.mean(col_values)),
                    'max': float(np.max(col_values)),
                    'min': float(np.min(col_values)),
                }
        
        return {
            'comparison_items': len(headers) - 1,
            'best_performers': best_performers,
        }
    
    def _analyze_return_table(self, data: List[List[str]]) -> Dict[str, Any]:
        headers = data[0]
        return_data = {}
        
        for row in data[1:]:
            if not row or not row[0]:
                continue
            
            period = row[0]
            values = []
            for val in row[1:]:
                try:
                    values.append(float(val.replace('%', '').replace(',', '')))
                except ValueError:
                    continue
            
            if values:
                return_data[period] = {
                    'values': values,
                    'avg': float(np.mean(values)),
                    'max': float(np.max(values)),
                    'min': float(np.min(values)),
                }
        
        return {
            'periods': list(return_data.keys()),
            'return_data': return_data,
        }
    
    def _analyze_general_table(self, data: List[List[str]]) -> Dict[str, Any]:
        numeric_count = 0
        total_count = 0
        
        for row in data[1:]:
            for cell in row[1:]:
                total_count += 1
                try:
                    float(cell.replace('%', '').replace(',', ''))
                    numeric_count += 1
                except ValueError:
                    continue
        
        return {
            'data_density': float(numeric_count) / total_count if total_count > 0 else 0,
            'has_numeric_data': numeric_count > 0,
            'estimated_type': self._guess_table_purpose(data),
        }
    
    def _guess_table_purpose(self, data: List[List[str]]) -> str:
        text_sample = ' '.join(' '.join(row) for row in data[:5])
        
        if any(kw in text_sample for kw in ['收益率', '回报', '收益', 'return']):
            return 'return_analysis'
        elif any(kw in text_sample for kw in ['风险', 'volatility', '波动', 'risk']):
            return 'risk_analysis'
        elif any(kw in text_sample for kw in ['因子', 'factor', 'ic', 'ir']):
            return 'factor_analysis'
        elif any(kw in text_sample for kw in ['策略', 'strategy', '模型', 'model']):
            return 'strategy_comparison'
        else:
            return 'general_information'
    
    def _extract_key_findings(self, data: List[List[str]], table_type: str) -> List[str]:
        findings = []
        text_sample = ' '.join(' '.join(row) for row in data)
        
        if table_type == 'factor_table':
            ic_pattern = re.compile(r'([\d.]+)\s*%?\s*(?:IC|信息系数)')
            ic_matches = ic_pattern.findall(text_sample)
            for match in ic_matches[:3]:
                findings.append(f"因子IC值: {match}%")
            
            ir_pattern = re.compile(r'([\d.]+)\s*%?\s*(?:IR|信息比率)')
            ir_matches = ir_pattern.findall(text_sample)
            for match in ir_matches[:3]:
                findings.append(f"因子IR值: {match}")
        
        elif table_type == 'financial_table':
            pe_pattern = re.compile(r'PE\s*[：:]\s*([\d.]+)')
            pe_matches = pe_pattern.findall(text_sample)
            for match in pe_matches[:3]:
                findings.append(f"市盈率PE: {match}")
            
            roe_pattern = re.compile(r'ROE\s*[：:]\s*([\d.]+)')
            roe_matches = roe_pattern.findall(text_sample)
            for match in roe_matches[:3]:
                findings.append(f"净资产收益率ROE: {match}%")
        
        elif table_type == 'return_table':
            return_pattern = re.compile(r'([\d.]+)\s*%')
            return_matches = return_pattern.findall(text_sample)
            numeric_returns = []
            for match in return_matches:
                try:
                    numeric_returns.append(float(match))
                except ValueError:
                    continue
            
            if numeric_returns:
                findings.append(f"最高收益率: {max(numeric_returns):.2f}%")
                findings.append(f"最低收益率: {min(numeric_returns):.2f}%")
                findings.append(f"平均收益率: {np.mean(numeric_returns):.2f}%")
        
        return findings[:5]
    
    def analyze_text_for_charts(self, text: str) -> List[Dict[str, Any]]:
        chart_patterns = [
            (r'(图|图表|Figure|Chart)\s*[0-9]+\s*[：:]\s*([^\n。！？]+)', 'chart'),
            (r'(表|Table)\s*[0-9]+\s*[：:]\s*([^\n。！？]+)', 'table'),
            (r'(柱状图|折线图|饼图|散点图|热力图)', 'chart_type'),
        ]
        
        results = []
        for pattern, label in chart_patterns:
            matches = re.findall(pattern, text)
            for match in matches[:10]:
                if isinstance(match, tuple):
                    chart_num = match[0]
                    chart_title = match[1]
                    results.append({
                        'type': label,
                        'number': chart_num,
                        'title': chart_title.strip(),
                    })
                else:
                    results.append({
                        'type': label,
                        'value': match,
                    })
        
        return results
    
    def extract_chart_descriptions(self, text: str) -> List[Dict[str, Any]]:
        chart_sections = []
        lines = text.split('\n')
        
        in_chart_section = False
        current_chart = {}
        
        for line in lines:
            chart_match = re.match(r'(图|图表|Figure|Chart|表|Table)\s*([0-9]+)\s*[：:]\s*(.*)', line)
            if chart_match:
                if current_chart:
                    chart_sections.append(current_chart)
                
                current_chart = {
                    'type': 'chart' if chart_match.group(1) in ['图', '图表', 'Figure', 'Chart'] else 'table',
                    'number': chart_match.group(2),
                    'title': chart_match.group(3).strip(),
                    'description': '',
                }
                in_chart_section = True
            
            elif in_chart_section and line.strip():
                if len(current_chart['description']) < 500:
                    current_chart['description'] += line.strip() + ' '
            
            elif in_chart_section and not line.strip():
                if current_chart:
                    chart_sections.append(current_chart)
                in_chart_section = False
                current_chart = {}
        
        if current_chart:
            chart_sections.append(current_chart)
        
        return chart_sections[:15]