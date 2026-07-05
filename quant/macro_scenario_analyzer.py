import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MacroScenarioAnalyzer:
    def __init__(self):
        self.scenarios = {}
    
    def analyze_scenario(self, scenario_params: Dict[str, Any]) -> Dict[str, Any]:
        fed_rate_unchanged = scenario_params.get('fed_rate_unchanged', True)
        japan_korea_crash = scenario_params.get('japan_korea_crash', False)
        china_rescue_amount = scenario_params.get('china_rescue_amount', 0)
        start_date = scenario_params.get('start_date', '2026-07-01')
        end_date = scenario_params.get('end_date', '2026-12-31')
        
        analysis = {
            'scenario_description': self._generate_scenario_description(
                fed_rate_unchanged, japan_korea_crash, china_rescue_amount
            ),
            'key_assumptions': {
                'fed_rate_unchanged': fed_rate_unchanged,
                'japan_korea_crash': japan_korea_crash,
                'china_rescue_amount': china_rescue_amount,
                'time_period': f"{start_date}~{end_date}"
            },
            'market_impact': {},
            'sector_impact': {},
            'stock_recommendations': [],
            'risk_assessment': {}
        }
        
        analysis['market_impact'] = self._calculate_market_impact(
            fed_rate_unchanged, japan_korea_crash, china_rescue_amount
        )
        
        analysis['sector_impact'] = self._calculate_sector_impact(
            japan_korea_crash, china_rescue_amount
        )
        
        analysis['stock_recommendations'] = self._generate_stock_recommendations(
            analysis['sector_impact']
        )
        
        analysis['risk_assessment'] = self._assess_risks(
            fed_rate_unchanged, japan_korea_crash, china_rescue_amount
        )
        
        return analysis
    
    def _generate_scenario_description(self, fed_unchanged: bool, 
                                       jk_crash: bool, rescue: float) -> str:
        parts = []
        if fed_unchanged:
            parts.append("美联储在2026年10月前维持利率不变")
        if jk_crash:
            parts.append("日韩股市崩盘")
        if rescue > 0:
            parts.append(f"中国央行注入{rescue}万亿人民币救市")
        
        return "、".join(parts) if parts else "基准情景"
    
    def _calculate_market_impact(self, fed_unchanged: bool, 
                                  jk_crash: bool, rescue: float) -> Dict[str, Any]:
        base_return = 0.08
        
        impacts = {
            'factors': [],
            'total_expected_return': base_return,
            'volatility_change': 0,
            'timing': {}
        }
        
        if fed_unchanged:
            impacts['factors'].append({
                'factor': '美联储利率不变',
                'impact': 0.03,
                'reason': '利率稳定有利于风险资产估值提升，外资流入增加',
                'confidence': 0.85
            })
            base_return += 0.03
        
        if jk_crash:
            impacts['factors'].append({
                'factor': '日韩股市崩盘',
                'impact': -0.12,
                'reason': '区域金融市场恐慌情绪传导，外资避险流出亚洲市场',
                'confidence': 0.75
            })
            base_return -= 0.12
            impacts['volatility_change'] += 0.05
        
        if rescue > 0:
            rescue_factor = min(rescue * 0.08, 0.25)
            impacts['factors'].append({
                'factor': '央行救市',
                'impact': rescue_factor,
                'reason': f'{rescue}万亿流动性注入提振市场信心，利好股市',
                'confidence': 0.80
            })
            base_return += rescue_factor
            impacts['volatility_change'] -= 0.03
        
        impacts['total_expected_return'] = base_return
        impacts['net_volatility_change'] = impacts['volatility_change']
        
        impacts['timing'] = {
            'short_term': '震荡下跌',
            'medium_term': '触底反弹',
            'long_term': '强势上行'
        }
        
        return impacts
    
    def _calculate_sector_impact(self, jk_crash: bool, rescue: float) -> Dict[str, Any]:
        sectors = {}
        
        sector_base = {
            '银行': {'base_score': 0.6, 'rescue_boost': 0.3},
            '非银行金融': {'base_score': 0.5, 'rescue_boost': 0.25},
            '房地产': {'base_score': 0.4, 'rescue_boost': 0.35},
            '基建': {'base_score': 0.5, 'rescue_boost': 0.3},
            '消费': {'base_score': 0.55, 'rescue_boost': 0.15},
            '科技成长': {'base_score': 0.65, 'rescue_boost': 0.2},
            '新能源': {'base_score': 0.5, 'rescue_boost': 0.2},
            '医药': {'base_score': 0.55, 'rescue_boost': 0.1},
            '半导体': {'base_score': 0.6, 'rescue_boost': 0.15},
            '高端制造': {'base_score': 0.55, 'rescue_boost': 0.2},
            '出口相关': {'base_score': 0.4, 'rescue_boost': 0.1},
            '资源品': {'base_score': 0.45, 'rescue_boost': 0.15}
        }
        
        for sector, info in sector_base.items():
            score = info['base_score']
            
            if jk_crash and sector in ['出口相关', '半导体']:
                score -= 0.15
            
            if rescue > 0:
                score += info['rescue_boost']
            
            score = max(0.1, min(1.0, score))
            
            sectors[sector] = {
                'score': score,
                'rating': self._get_rating(score),
                'expected_return': (score - 0.5) * 0.4,
                'reason': self._generate_sector_reason(sector, jk_crash, rescue)
            }
        
        return sectors
    
    def _get_rating(self, score: float) -> str:
        if score >= 0.75:
            return '强烈推荐'
        elif score >= 0.6:
            return '推荐'
        elif score >= 0.45:
            return '中性'
        elif score >= 0.3:
            return '谨慎'
        else:
            return '回避'
    
    def _generate_sector_reason(self, sector: str, jk_crash: bool, rescue: float) -> str:
        reasons = []
        
        if rescue > 0:
            if sector in ['银行', '非银行金融']:
                reasons.append('央行流动性注入直接利好金融板块')
            if sector in ['房地产', '基建']:
                reasons.append('救市资金有望流入实体经济，利好地产和基建')
            if sector in ['科技成长', '新能源']:
                reasons.append('流动性宽松环境利好成长股估值')
        
        if jk_crash:
            if sector in ['出口相关', '半导体']:
                reasons.append('日韩崩盘可能影响产业链和出口需求')
        
        if sector == '消费':
            reasons.append('国内需求相对稳定，防御性较强')
        
        return '；'.join(reasons) if reasons else '行业基本面稳定'
    
    def _generate_stock_recommendations(self, sector_impact: Dict[str, Any]) -> List[Dict[str, Any]]:
        top_sectors = sorted(sector_impact.items(), key=lambda x: x[1]['score'], reverse=True)[:5]
        
        stock_pool = {
            '银行': [
                {'code': '601318.SH', 'name': '中国平安', 'reason': '金融龙头，受益于流动性宽松'},
                {'code': '601398.SH', 'name': '工商银行', 'reason': '大行稳定，低估值'},
                {'code': '600036.SH', 'name': '招商银行', 'reason': '零售银行龙头'}
            ],
            '非银行金融': [
                {'code': '600519.SH', 'name': '贵州茅台', 'reason': '消费龙头，防御性强'},
                {'code': '000001.SZ', 'name': '平安银行', 'reason': '股份制银行代表'}
            ],
            '房地产': [
                {'code': '600048.SH', 'name': '保利发展', 'reason': '央企地产，政策受益'},
                {'code': '000002.SZ', 'name': '万科A', 'reason': '行业龙头，稳健经营'},
                {'code': '601155.SH', 'name': '新城控股', 'reason': '商业地产转型成功'}
            ],
            '基建': [
                {'code': '601390.SH', 'name': '中国中铁', 'reason': '基建央企龙头'},
                {'code': '601800.SH', 'name': '中国交建', 'reason': '海外业务拓展'},
                {'code': '600039.SH', 'name': '四川路桥', 'reason': '区域基建龙头'}
            ],
            '科技成长': [
                {'code': '300750.SZ', 'name': '宁德时代', 'reason': '新能源龙头，行业景气'},
                {'code': '300308.SZ', 'name': '中际旭创', 'reason': '光通信龙头，AI受益'},
                {'code': '600588.SH', 'name': '用友网络', 'reason': '工业软件龙头'}
            ],
            '消费': [
                {'code': '600519.SH', 'name': '贵州茅台', 'reason': '白酒龙头，业绩稳定'},
                {'code': '000858.SZ', 'name': '五粮液', 'reason': '次高端白酒'},
                {'code': '601318.SH', 'name': '中国平安', 'reason': '保险龙头'}
            ],
            '新能源': [
                {'code': '300750.SZ', 'name': '宁德时代', 'reason': '动力电池龙头'},
                {'code': '601012.SH', 'name': '隆基绿能', 'reason': '光伏龙头'},
                {'code': '002594.SZ', 'name': '比亚迪', 'reason': '新能源汽车龙头'}
            ],
            '医药': [
                {'code': '300760.SZ', 'name': '迈瑞医疗', 'reason': '医疗器械龙头'},
                {'code': '600276.SH', 'name': '恒瑞医药', 'reason': '创新药龙头'},
                {'code': '000661.SZ', 'name': '长春高新', 'reason': '生长激素龙头'}
            ],
            '半导体': [
                {'code': '600584.SH', 'name': '中芯国际', 'reason': '晶圆代工龙头'},
                {'code': '002371.SZ', 'name': '北方华创', 'reason': '半导体设备龙头'},
                {'code': '300782.SZ', 'name': '卓胜微', 'reason': '射频芯片龙头'}
            ],
            '高端制造': [
                {'code': '600031.SH', 'name': '三一重工', 'reason': '工程机械龙头'},
                {'code': '002594.SZ', 'name': '比亚迪', 'reason': '新能源车制造'},
                {'code': '601117.SH', 'name': '中国化学', 'reason': '化工工程龙头'}
            ],
            '出口相关': [
                {'code': '002415.SZ', 'name': '海康威视', 'reason': '安防龙头'},
                {'code': '000333.SZ', 'name': '美的集团', 'reason': '家电龙头'}
            ],
            '资源品': [
                {'code': '601899.SH', 'name': '紫金矿业', 'reason': '黄金龙头'},
                {'code': '600028.SH', 'name': '中国石化', 'reason': '石油龙头'}
            ]
        }
        
        recommendations = []
        for sector, impact in top_sectors:
            if sector in stock_pool:
                for stock in stock_pool[sector][:3]:
                    recommendations.append({
                        'sector': sector,
                        'code': stock['code'],
                        'name': stock['name'],
                        'expected_return': float(impact['expected_return']),
                        'rating': impact['rating'],
                        'reason': stock['reason'],
                        'sector_score': float(impact['score'])
                    })
        
        return sorted(recommendations, key=lambda x: x['sector_score'], reverse=True)[:15]
    
    def _assess_risks(self, fed_unchanged: bool, jk_crash: bool, rescue: float) -> Dict[str, Any]:
        risks = []
        
        if jk_crash:
            risks.append({
                'risk': '区域金融风险传导',
                'probability': 0.7,
                'impact': 0.8,
                'mitigation': '国内政策对冲，资本管制',
                'level': '高'
            })
        
        risks.append({
            'risk': '美联储政策转向风险',
            'probability': 0.3,
            'impact': 0.7,
            'mitigation': '关注FOMC会议信号',
            'level': '中'
        })
        
        if rescue > 0:
            risks.append({
                'risk': '救市资金效果不及预期',
                'probability': 0.4,
                'impact': 0.6,
                'mitigation': '密切跟踪资金流向',
                'level': '中'
            })
        
        risks.append({
            'risk': '国内经济基本面恶化',
            'probability': 0.35,
            'impact': 0.75,
            'mitigation': '关注PMI等宏观数据',
            'level': '中高'
        })
        
        risks.append({
            'risk': '地缘政治风险',
            'probability': 0.25,
            'impact': 0.85,
            'mitigation': '多元化配置',
            'level': '中高'
        })
        
        return {
            'total_risk_level': '中高',
            'key_risks': risks,
            'risk_summary': '当前情景下，区域金融风险和国内基本面是主要关注点，但央行救市政策有助于缓解下行压力'
        }
    
    def generate_scenario_comparison(self, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = []
        
        for scenario in scenarios:
            analysis = self.analyze_scenario(scenario)
            results.append({
                'scenario_name': scenario.get('name', '未命名情景'),
                'description': analysis['scenario_description'],
                'expected_return': analysis['market_impact']['total_expected_return'],
                'volatility_change': analysis['market_impact']['net_volatility_change'],
                'risk_level': analysis['risk_assessment']['total_risk_level']
            })
        
        best_scenario = max(results, key=lambda x: x['expected_return'])
        worst_scenario = min(results, key=lambda x: x['expected_return'])
        
        return {
            'scenarios': results,
            'best_scenario': best_scenario,
            'worst_scenario': worst_scenario,
            'summary': f"最佳情景'{best_scenario['scenario_name']}'预期收益{best_scenario['expected_return']*100:.1f}%，"
                       f"最差情景'{worst_scenario['scenario_name']}'预期收益{worst_scenario['expected_return']*100:.1f}%"
        }