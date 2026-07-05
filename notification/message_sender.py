import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PushPlusSender:
    def __init__(self, token: str = None):
        self.token = token or '512af99925174d1eb36df9c5567694bb'
        self.base_url = 'https://www.pushplus.plus/send'
    
    def send_message(self, title: str, content: str, template: str = 'txt', 
                    channel: str = None) -> Dict[str, Any]:
        if not self.token:
            logger.error("PushPlus token not configured")
            return {'success': False, 'error': 'Token not configured'}
        
        data = {
            'token': self.token,
            'title': title,
            'content': content,
            'template': template
        }
        
        if channel:
            data['channel'] = channel
        
        try:
            response = requests.post(self.base_url, data=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 200:
                logger.info(f"Message sent successfully: {title}")
                return {'success': True, 'message': result.get('msg', 'Success')}
            else:
                logger.error(f"Failed to send message: {result.get('msg')}")
                return {'success': False, 'error': result.get('msg')}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Send message error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_markdown(self, title: str, content: str, channel: str = None) -> Dict[str, Any]:
        return self.send_message(title, content, template='markdown', channel=channel)
    
    def send_daily_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        title = f"📊 每日股市简报 {datetime.now().strftime('%Y-%m-%d')}"
        
        content = self._format_daily_report(report_data)
        
        return self.send_markdown(title, content)
    
    def send_weekly_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        title = f"📈 股市周报 {datetime.now().strftime('%Y年第%W周')}"
        
        content = self._format_weekly_report(report_data)
        
        return self.send_markdown(title, content)
    
    def send_scenario_alert(self, scenario_name: str, alert_level: str, 
                            message: str) -> Dict[str, Any]:
        level_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }
        
        title = f"{level_emoji.get(alert_level, '📌')} 情景预警: {scenario_name}"
        content = f"**预警等级**: {alert_level}\n\n**预警信息**:\n{message}"
        
        return self.send_markdown(title, content)
    
    def _format_daily_report(self, report: Dict[str, Any]) -> str:
        sections = []
        
        sections.append(f"## 📅 {report.get('date', datetime.now().strftime('%Y-%m-%d'))}")
        
        if 'market_summary' in report:
            market = report['market_summary']
            sections.append("### 🌐 全球市场概览")
            for market_name, data in market.items():
                change_str = f"+{data['change']}%" if data['change'] > 0 else f"{data['change']}%"
                sections.append(f"- **{market_name}**: {data['price']} ({change_str})")
        
        if 'hot_topics' in report:
            sections.append("### 🔥 热点资讯")
            for i, topic in enumerate(report['hot_topics'], 1):
                sections.append(f"{i}. {topic}")
        
        if 'sector_performance' in report:
            sections.append("### 📈 行业表现")
            for sector in report['sector_performance'][:5]:
                change_str = f"+{sector['change']}%" if sector['change'] > 0 else f"{sector['change']}%"
                sections.append(f"- **{sector['name']}**: {change_str}")
        
        if 'top_stocks' in report:
            sections.append("### 🎯 异动股票")
            for stock in report['top_stocks'][:5]:
                change_str = f"+{stock['change']}%" if stock['change'] > 0 else f"{stock['change']}%"
                sections.append(f"- **{stock['name']}({stock['code']})**: {change_str}")
        
        if 'factor_analysis' in report:
            sections.append("### 📊 因子分析")
            for factor in report['factor_analysis'][:5]:
                sections.append(f"- **{factor['name']}**: IC={factor['ic']:.3f}")
        
        if 'risk_warnings' in report:
            sections.append("### ⚠️ 风险提示")
            for risk in report['risk_warnings'][:3]:
                sections.append(f"- {risk}")
        
        return '\n\n'.join(sections)
    
    def _format_weekly_report(self, report: Dict[str, Any]) -> str:
        sections = []
        
        sections.append(f"## 📅 {report.get('week_range', '')}")
        
        if 'weekly_summary' in report:
            summary = report['weekly_summary']
            sections.append("### 📊 本周概览")
            sections.append(f"- **市场表现**: {summary.get('market_return', 0):.2f}%")
            sections.append(f"- **波动率**: {summary.get('volatility', 0):.2f}%")
            sections.append(f"- **成交额**: {summary.get('volume', 0):,}")
        
        if 'period_comparison' in report:
            sections.append("### 🔄 周期对比")
            for period, data in report['period_comparison'].items():
                change_str = f"+{data['return']}%" if data['return'] > 0 else f"{data['return']}%"
                sections.append(f"- **{period}**: {change_str}")
        
        if 'top_performers' in report:
            sections.append("### 🏆 表现最好")
            for item in report['top_performers'][:5]:
                change_str = f"+{item['return']}%" if item['return'] > 0 else f"{item['return']}%"
                sections.append(f"- **{item['name']}**: {change_str}")
        
        if 'bottom_performers' in report:
            sections.append("### 💔 表现最差")
            for item in report['bottom_performers'][:5]:
                change_str = f"+{item['return']}%" if item['return'] > 0 else f"{item['return']}%"
                sections.append(f"- **{item['name']}**: {change_str}")
        
        if 'scenario_analysis' in report:
            scenario = report['scenario_analysis']
            sections.append("### 🔮 情景分析")
            sections.append(f"- **情景**: {scenario.get('description', '')}")
            expected_return = scenario.get('expected_return', 0)
            return_str = f"+{expected_return*100:.1f}%" if expected_return > 0 else f"{expected_return*100:.1f}%"
            sections.append(f"- **预期收益**: {return_str}")
        
        if 'investment_suggestion' in report:
            sections.append("### 💡 投资建议")
            sections.append(report['investment_suggestion'])
        
        return '\n\n'.join(sections)