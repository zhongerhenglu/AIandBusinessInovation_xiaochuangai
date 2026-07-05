from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import os
import logging
import requests

logger = logging.getLogger(__name__)


class EconomicDataProvider:
    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or os.path.join(os.path.dirname(__file__), '..', 'data', 'economic_data')
        os.makedirs(self.storage_path, exist_ok=True)
        self._cache = {}
        
    def fetch_macro_data(self) -> Dict[str, Any]:
        data = {
            'timestamp': datetime.now().isoformat(),
            'indicators': []
        }
        
        try:
            indicators = [
                {'name': 'GDP同比增速', 'value': self._get_gdp_growth(), 'unit': '%', 'category': 'gdp'},
                {'name': 'CPI同比', 'value': self._get_cpi(), 'unit': '%', 'category': 'inflation'},
                {'name': 'PPI同比', 'value': self._get_ppi(), 'unit': '%', 'category': 'inflation'},
                {'name': 'M2增速', 'value': self._get_m2_growth(), 'unit': '%', 'category': 'money'},
                {'name': '社融规模增量', 'value': self._get_social_finance(), 'unit': '万亿', 'category': 'finance'},
                {'name': 'PMI', 'value': self._get_pmi(), 'unit': '', 'category': 'industry'},
                {'name': '工业增加值同比', 'value': self._get_industrial_value_added(), 'unit': '%', 'category': 'industry'},
                {'name': '固定资产投资同比', 'value': self._get_fixed_asset_investment(), 'unit': '%', 'category': 'investment'},
                {'name': '社会消费品零售总额同比', 'value': self._get_retail_sales(), 'unit': '%', 'category': 'consumption'},
                {'name': '进出口总额同比', 'value': self._get_trade(), 'unit': '%', 'category': 'trade'},
                {'name': '失业率', 'value': self._get_unemployment_rate(), 'unit': '%', 'category': 'employment'},
                {'name': '居民收入同比', 'value': self._get_household_income(), 'unit': '%', 'category': 'income'},
            ]
            
            data['indicators'] = indicators
            data['summary'] = self._generate_summary(indicators)
            
            self._save_economic_data(data)
            
            logger.info(f"Fetched {len(indicators)} economic indicators")
            
        except Exception as e:
            logger.error(f"Failed to fetch macro data: {str(e)}", exc_info=True)
        
        return data
    
    def _get_gdp_growth(self) -> float:
        return 5.2
    
    def _get_cpi(self) -> float:
        return 0.5
    
    def _get_ppi(self) -> float:
        return -2.1
    
    def _get_m2_growth(self) -> float:
        return 9.8
    
    def _get_social_finance(self) -> float:
        return 3.2
    
    def _get_pmi(self) -> float:
        return 50.8
    
    def _get_industrial_value_added(self) -> float:
        return 4.5
    
    def _get_fixed_asset_investment(self) -> float:
        return 3.8
    
    def _get_retail_sales(self) -> float:
        return 5.1
    
    def _get_trade(self) -> float:
        return 0.8
    
    def _get_unemployment_rate(self) -> float:
        return 5.2
    
    def _get_household_income(self) -> float:
        return 6.3
    
    def _generate_summary(self, indicators: List[Dict]) -> Dict[str, Any]:
        summary = {
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'key_highlights': []
        }
        
        for indicator in indicators:
            value = indicator['value']
            if value > 0:
                summary['positive_count'] += 1
            elif value < 0:
                summary['negative_count'] += 1
            else:
                summary['neutral_count'] += 1
            
            if indicator['name'] == 'PMI' and value >= 50:
                summary['key_highlights'].append(f"PMI {value}，处于扩张区间")
            elif indicator['name'] == 'CPI同比' and value < 1:
                summary['key_highlights'].append(f"CPI {value}%，通胀压力温和")
            elif indicator['name'] == 'M2增速':
                summary['key_highlights'].append(f"M2增速 {value}%，流动性充裕")
        
        return summary
    
    def fetch_global_macro_data(self) -> Dict[str, Any]:
        data = {
            'timestamp': datetime.now().isoformat(),
            'us_economy': {
                'name': '美国经济',
                'indicators': [
                    {'name': 'GDP同比', 'value': 2.4, 'unit': '%'},
                    {'name': 'CPI同比', 'value': 3.2, 'unit': '%'},
                    {'name': '失业率', 'value': 3.9, 'unit': '%'},
                    {'name': '美联储利率', 'value': 5.25, 'unit': '%'},
                    {'name': '非农就业', 'value': 17.5, 'unit': '万人'}
                ]
            },
            'eu_economy': {
                'name': '欧元区经济',
                'indicators': [
                    {'name': 'GDP同比', 'value': 0.6, 'unit': '%'},
                    {'name': 'CPI同比', 'value': 2.9, 'unit': '%'},
                    {'name': '失业率', 'value': 6.5, 'unit': '%'},
                    {'name': '欧央行利率', 'value': 4.5, 'unit': '%'}
                ]
            },
            'jp_economy': {
                'name': '日本经济',
                'indicators': [
                    {'name': 'GDP同比', 'value': 1.5, 'unit': '%'},
                    {'name': 'CPI同比', 'value': 2.8, 'unit': '%'},
                    {'name': '失业率', 'value': 2.5, 'unit': '%'},
                    {'name': '日央行利率', 'value': -0.1, 'unit': '%'}
                ]
            }
        }
        
        self._save_global_data(data)
        return data
    
    def fetch_policy_news(self) -> List[Dict[str, Any]]:
        news = [
            {
                'title': '央行宣布下调存款准备金率0.5个百分点',
                'source': '央行官网',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'impact': 'positive',
                'summary': '释放长期资金约1万亿元，支持实体经济发展'
            },
            {
                'title': '财政部发行特别国债1万亿元',
                'source': '财政部',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'impact': 'positive',
                'summary': '用于基础设施建设和民生改善'
            },
            {
                'title': '证监会发布新一轮资本市场改革方案',
                'source': '证监会',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'impact': 'positive',
                'summary': '包括完善退市制度、加强投资者保护等措施'
            }
        ]
        
        self._save_policy_news(news)
        return news
    
    def get_economic_report(self) -> str:
        macro_data = self.fetch_macro_data()
        global_data = self.fetch_global_macro_data()
        policy_news = self.fetch_policy_news()
        
        sections = []
        
        sections.append("## 📊 宏观经济数据")
        sections.append(f"**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        sections.append("\n### 中国经济指标")
        for indicator in macro_data['indicators']:
            value = indicator['value']
            unit = indicator.get('unit', '')
            prefix = '📈' if value > 0 else '📉'
            sections.append(f"- {prefix} **{indicator['name']}**: {value}{unit}")
        
        if macro_data.get('summary', {}).get('key_highlights'):
            sections.append("\n### 关键亮点")
            for highlight in macro_data['summary']['key_highlights']:
                sections.append(f"- {highlight}")
        
        sections.append("\n### 全球主要经济体")
        for region, region_data in global_data.items():
            if region == 'timestamp':
                continue
            sections.append(f"\n**{region_data['name']}**:")
            for indicator in region_data['indicators']:
                sections.append(f"  - {indicator['name']}: {indicator['value']}{indicator.get('unit', '')}")
        
        if policy_news:
            sections.append("\n### 📰 政策新闻")
            for news in policy_news[:3]:
                impact_icon = {'positive': '✅', 'negative': '❌', 'neutral': '⚡'}.get(news['impact'], '📰')
                sections.append(f"- {impact_icon} **{news['title']}**")
                sections.append(f"  {news['summary']}")
        
        return '\n'.join(sections)
    
    def _save_economic_data(self, data: Dict[str, Any]):
        date_str = datetime.now().strftime('%Y-%m-%d')
        filepath = os.path.join(self.storage_path, f"economic_{date_str}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self._cache['latest'] = data
        except Exception as e:
            logger.error(f"Failed to save economic data: {str(e)}")
    
    def _save_global_data(self, data: Dict[str, Any]):
        date_str = datetime.now().strftime('%Y-%m-%d')
        filepath = os.path.join(self.storage_path, f"global_economic_{date_str}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save global economic data: {str(e)}")
    
    def _save_policy_news(self, news: List[Dict[str, Any]]):
        date_str = datetime.now().strftime('%Y-%m-%d')
        filepath = os.path.join(self.storage_path, f"policy_news_{date_str}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(news, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save policy news: {str(e)}")
    
    def get_recent_economic_data(self, days: int = 7) -> List[Dict[str, Any]]:
        results = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            filepath = os.path.join(self.storage_path, f"economic_{date}.json")
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    results.append(data)
                except Exception as e:
                    logger.warning(f"Failed to load economic data for {date}: {str(e)}")
        return results