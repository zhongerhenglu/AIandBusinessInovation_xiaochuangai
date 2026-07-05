from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class DataCrossSection:
    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or os.path.join(os.path.dirname(__file__), '..', 'data', 'cross_sections')
        os.makedirs(self.storage_path, exist_ok=True)
        self._cache = {}
    
    def save_cross_section(self, date: str, data: Dict[str, Any]):
        filepath = os.path.join(self.storage_path, f"cross_section_{date}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self._cache[date] = data
            logger.info(f"Saved cross section for {date}")
        except Exception as e:
            logger.error(f"Failed to save cross section: {str(e)}")
    
    def load_cross_section(self, date: str) -> Optional[Dict[str, Any]]:
        if date in self._cache:
            return self._cache[date]
        
        filepath = os.path.join(self.storage_path, f"cross_section_{date}.json")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._cache[date] = data
            return data
        except Exception as e:
            logger.warning(f"Failed to load cross section for {date}: {str(e)}")
            return None
    
    def generate_daily_cross_section(self, market_data: Dict, factor_data: Dict, 
                                     stock_quotes: List[Dict]) -> Dict[str, Any]:
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        cross_section = {
            'date': date_str,
            'timestamp': datetime.now().isoformat(),
            'market_overview': market_data,
            'factor_data': factor_data,
            'stock_quotes': stock_quotes,
            'statistics': self._compute_statistics(market_data, stock_quotes),
            'factor_ranking': self._compute_factor_ranking(factor_data),
            'sector_analysis': self._compute_sector_analysis(stock_quotes)
        }
        
        return cross_section
    
    def _compute_statistics(self, market_data: Dict, stock_quotes: List[Dict]) -> Dict[str, Any]:
        if not stock_quotes:
            return {}
        
        changes = [s.get('change', 0) for s in stock_quotes if isinstance(s.get('change', 0), (int, float))]
        
        return {
            'total_stocks': len(stock_quotes),
            'avg_change': sum(changes) / len(changes) if changes else 0,
            'max_change': max(changes) if changes else 0,
            'min_change': min(changes) if changes else 0,
            'up_count': sum(1 for c in changes if c > 0),
            'down_count': sum(1 for c in changes if c < 0),
            'flat_count': sum(1 for c in changes if c == 0),
            'market_cap_weighted_change': self._compute_weighted_change(stock_quotes)
        }
    
    def _compute_weighted_change(self, stock_quotes: List[Dict]) -> float:
        total_market_cap = sum(s.get('market_cap', 0) for s in stock_quotes)
        if total_market_cap == 0:
            return 0
        
        weighted_sum = sum(s.get('change', 0) * s.get('market_cap', 0) for s in stock_quotes)
        return weighted_sum / total_market_cap
    
    def _compute_factor_ranking(self, factor_data: Dict) -> List[Dict]:
        factors = []
        for factor_name, data in factor_data.items():
            ic = data.get('ic', 0)
            ir = data.get('ir', 0)
            factors.append({
                'factor_name': factor_name,
                'ic': ic,
                'ir': ir,
                'rank': abs(ic)
            })
        
        return sorted(factors, key=lambda x: x['rank'], reverse=True)
    
    def _compute_sector_analysis(self, stock_quotes: List[Dict]) -> Dict[str, Any]:
        sectors = {}
        for stock in stock_quotes:
            sector = stock.get('sector', 'unknown')
            if sector not in sectors:
                sectors[sector] = {'count': 0, 'total_change': 0, 'stocks': []}
            sectors[sector]['count'] += 1
            sectors[sector]['total_change'] += stock.get('change', 0)
            sectors[sector]['stocks'].append(stock.get('name', ''))
        
        sector_summary = []
        for sector, data in sectors.items():
            sector_summary.append({
                'sector': sector,
                'count': data['count'],
                'avg_change': data['total_change'] / data['count'],
                'representative_stocks': data['stocks'][:5]
            })
        
        return sorted(sector_summary, key=lambda x: x['avg_change'], reverse=True)
    
    def get_recent_cross_sections(self, days: int = 7) -> List[Dict]:
        sections = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            data = self.load_cross_section(date)
            if data:
                sections.append(data)
        return sections
    
    def get_factor_performance_trend(self, factor_name: str, days: int = 30) -> List[Dict]:
        trend = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            data = self.load_cross_section(date)
            if data:
                factor_data = data.get('factor_data', {})
                if factor_name in factor_data:
                    trend.append({
                        'date': date,
                        'ic': factor_data[factor_name].get('ic', 0),
                        'ir': factor_data[factor_name].get('ir', 0)
                    })
        return trend[::-1]


class PredictionValidator:
    def __init__(self, cross_section: DataCrossSection = None):
        self.cross_section = cross_section or DataCrossSection()
        self.validation_results: List[Dict[str, Any]] = []
    
    def validate_predictions(self, predictions: Dict[str, Any], actual_data: Dict[str, Any]) -> Dict[str, Any]:
        validation = {
            'timestamp': datetime.now().isoformat(),
            'predictions': predictions,
            'actual': actual_data,
            'metrics': {},
            'validations': []
        }
        
        if 'market_direction' in predictions:
            actual_dir = self._determine_direction(actual_data)
            predicted_dir = predictions['market_direction']
            
            validation['metrics']['market_direction_accuracy'] = \
                1 if predicted_dir == actual_dir else 0
            
            validation['validations'].append({
                'type': 'market_direction',
                'predicted': predicted_dir,
                'actual': actual_dir,
                'correct': predicted_dir == actual_dir
            })
        
        if 'factor_rankings' in predictions:
            actual_ranking = self._get_actual_factor_ranking(actual_data)
            predicted_ranking = predictions['factor_rankings']
            
            accuracy = self._compute_ranking_accuracy(predicted_ranking, actual_ranking)
            validation['metrics']['factor_ranking_accuracy'] = accuracy
            
            validation['validations'].append({
                'type': 'factor_ranking',
                'accuracy': accuracy,
                'predicted': [f['factor_name'] for f in predicted_ranking[:5]],
                'actual': [f['factor_name'] for f in actual_ranking[:5]]
            })
        
        if 'stock_picks' in predictions:
            predicted_stocks = [p['stock_code'] for p in predictions['stock_picks']]
            actual_performance = self._get_stock_performance(actual_data, predicted_stocks)
            
            avg_return = sum(actual_performance.values()) / len(actual_performance) if actual_performance else 0
            benchmark_return = actual_data.get('market_overview', {}).get('shanghai', {}).get('change', 0)
            
            validation['metrics']['stock_pick_avg_return'] = avg_return
            validation['metrics']['stock_pick_alpha'] = avg_return - benchmark_return
            validation['metrics']['stock_pick_win_rate'] = \
                sum(1 for r in actual_performance.values() if r > 0) / len(actual_performance) if actual_performance else 0
            
            validation['validations'].append({
                'type': 'stock_picks',
                'avg_return': avg_return,
                'alpha': avg_return - benchmark_return,
                'win_rate': sum(1 for r in actual_performance.values() if r > 0) / len(actual_performance) if actual_performance else 0,
                'stocks': [{'code': code, 'return': ret} for code, ret in actual_performance.items()]
            })
        
        self.validation_results.append(validation)
        
        return validation
    
    def _determine_direction(self, data: Dict) -> str:
        shanghai_change = data.get('market_overview', {}).get('shanghai', {}).get('change', 0)
        if shanghai_change > 0.5:
            return 'up'
        elif shanghai_change < -0.5:
            return 'down'
        else:
            return 'sideways'
    
    def _get_actual_factor_ranking(self, data: Dict) -> List[Dict]:
        factor_data = data.get('factor_data', {})
        factors = []
        for name, info in factor_data.items():
            factors.append({
                'factor_name': name,
                'ic': info.get('ic', 0)
            })
        return sorted(factors, key=lambda x: abs(x['ic']), reverse=True)
    
    def _compute_ranking_accuracy(self, predicted: List[Dict], actual: List[Dict]) -> float:
        if not predicted or not actual:
            return 0
        
        predicted_set = set(f['factor_name'] for f in predicted[:5])
        actual_set = set(f['factor_name'] for f in actual[:5])
        
        intersection = predicted_set & actual_set
        return len(intersection) / 5
    
    def _get_stock_performance(self, data: Dict, stock_codes: List[str]) -> Dict[str, float]:
        performance = {}
        stock_quotes = data.get('stock_quotes', [])
        
        for code in stock_codes:
            for stock in stock_quotes:
                if stock.get('code') == code or stock.get('symbol') == code:
                    performance[code] = stock.get('change', 0)
                    break
        
        return performance
    
    def get_validation_history(self, days: int = 30) -> List[Dict]:
        return self.validation_results[-days:]
    
    def get_validation_summary(self) -> Dict[str, Any]:
        if not self.validation_results:
            return {'total_validations': 0}
        
        metrics = {
            'total_validations': len(self.validation_results),
            'market_direction_accuracy': 0,
            'factor_ranking_accuracy': 0,
            'stock_pick_avg_alpha': 0,
            'stock_pick_win_rate': 0
        }
        
        md_count = 0
        fr_count = 0
        sp_count = 0
        
        for result in self.validation_results:
            if 'market_direction_accuracy' in result['metrics']:
                metrics['market_direction_accuracy'] += result['metrics']['market_direction_accuracy']
                md_count += 1
            
            if 'factor_ranking_accuracy' in result['metrics']:
                metrics['factor_ranking_accuracy'] += result['metrics']['factor_ranking_accuracy']
                fr_count += 1
            
            if 'stock_pick_alpha' in result['metrics']:
                metrics['stock_pick_avg_alpha'] += result['metrics']['stock_pick_alpha']
                sp_count += 1
            
            if 'stock_pick_win_rate' in result['metrics']:
                metrics['stock_pick_win_rate'] += result['metrics']['stock_pick_win_rate']
                sp_count += 1
        
        if md_count > 0:
            metrics['market_direction_accuracy'] = round(metrics['market_direction_accuracy'] / md_count, 3)
        if fr_count > 0:
            metrics['factor_ranking_accuracy'] = round(metrics['factor_ranking_accuracy'] / fr_count, 3)
        if sp_count > 0:
            metrics['stock_pick_avg_alpha'] = round(metrics['stock_pick_avg_alpha'] / sp_count, 3)
            metrics['stock_pick_win_rate'] = round(metrics['stock_pick_win_rate'] / sp_count, 3)
        
        return metrics


class FactorImprovementEngine:
    def __init__(self, cross_section: DataCrossSection = None):
        self.cross_section = cross_section or DataCrossSection()
        self.improvement_history: List[Dict[str, Any]] = []
    
    def analyze_factor_degradation(self, factor_name: str, days: int = 30) -> Dict[str, Any]:
        trend = self.cross_section.get_factor_performance_trend(factor_name, days)
        
        if len(trend) < 5:
            return {'factor_name': factor_name, 'insufficient_data': True}
        
        ics = [t['ic'] for t in trend]
        recent_ics = ics[-10:]
        
        avg_ic = sum(ics) / len(ics)
        recent_avg_ic = sum(recent_ics) / len(recent_ics)
        ic_decay = (recent_avg_ic - avg_ic) / abs(avg_ic) if avg_ic != 0 else 0
        
        improvement_suggestions = []
        
        if ic_decay < -0.2:
            improvement_suggestions.append({
                'type': 'parameter_adjustment',
                'suggestion': f"{factor_name} IC值下降超过20%，建议调整参数或重新定义因子",
                'action': 'review_factor_definition'
            })
            
            if 'ROC' in factor_name:
                improvement_suggestions.append({
                    'type': 'lookback_adjustment',
                    'suggestion': f"{factor_name}动量因子衰减明显，建议调整回看周期",
                    'action': 'adjust_lookback_period'
                })
        
        if len([ic for ic in ics if abs(ic) < 0.05]) > len(ics) * 0.5:
            improvement_suggestions.append({
                'type': 'factor_replacement',
                'suggestion': f"{factor_name} IC值持续低于5%，考虑替换为其他因子",
                'action': 'consider_factor_replacement'
            })
        
        return {
            'factor_name': factor_name,
            'trend_length': len(trend),
            'avg_ic': round(avg_ic, 4),
            'recent_avg_ic': round(recent_avg_ic, 4),
            'ic_decay': round(ic_decay, 4),
            'degradation_detected': ic_decay < -0.15,
            'improvement_suggestions': improvement_suggestions
        }
    
    def optimize_factor_weights(self, factor_performance: Dict[str, Dict]) -> Dict[str, float]:
        weights = {}
        total_score = 0
        
        for factor_name, data in factor_performance.items():
            ic = data.get('ic', 0)
            ir = data.get('ir', 0)
            score = abs(ic) * ir
            weights[factor_name] = score
            total_score += score
        
        if total_score > 0:
            weights = {k: round(v / total_score, 4) for k, v in weights.items()}
        
        return weights
    
    def generate_improvement_report(self, factors_to_analyze: List[str] = None) -> Dict[str, Any]:
        if factors_to_analyze is None:
            factors_to_analyze = ['ROC_5', 'ROC_20', 'PB_ratio', 'PE_ratio', 'ROE', 'ROA']
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'factors_analyzed': len(factors_to_analyze),
            'degrading_factors': [],
            'stable_factors': [],
            'improvement_actions': []
        }
        
        for factor_name in factors_to_analyze:
            analysis = self.analyze_factor_degradation(factor_name, 30)
            
            if analysis.get('insufficient_data'):
                continue
            
            if analysis['degradation_detected']:
                report['degrading_factors'].append({
                    'factor_name': factor_name,
                    'avg_ic': analysis['avg_ic'],
                    'recent_avg_ic': analysis['recent_avg_ic'],
                    'ic_decay': analysis['ic_decay']
                })
                
                for suggestion in analysis['improvement_suggestions']:
                    report['improvement_actions'].append({
                        'factor': factor_name,
                        'action_type': suggestion['type'],
                        'description': suggestion['suggestion'],
                        'action': suggestion['action']
                    })
            else:
                report['stable_factors'].append({
                    'factor_name': factor_name,
                    'avg_ic': analysis['avg_ic'],
                    'recent_avg_ic': analysis['recent_avg_ic']
                })
        
        return report
    
    def apply_improvement(self, factor_name: str, improvement_action: str, params: Dict = None):
        improvement_record = {
            'timestamp': datetime.now().isoformat(),
            'factor_name': factor_name,
            'action': improvement_action,
            'params': params or {},
            'status': 'applied'
        }
        
        self.improvement_history.append(improvement_record)
        logger.info(f"Applied improvement to {factor_name}: {improvement_action}")
        
        return improvement_record