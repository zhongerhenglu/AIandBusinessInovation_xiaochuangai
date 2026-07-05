import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notification import PushPlusSender, NotificationScheduler, MessageQueue, Message
from quant.data_simulator import DataSimulator
from quant.macro_scenario_analyzer import MacroScenarioAnalyzer
from quant.chart_generator import ChartGenerator
from quant.quant_analyzer import QuantAnalyzer

logger = logging.getLogger(__name__)


class MarketNotificationService:
    def __init__(self):
        self.sender = PushPlusSender()
        self.scheduler = NotificationScheduler()
        self.message_queue = MessageQueue()
        self.message_queue.set_sender(self.sender)
        
        self.data_simulator = DataSimulator()
        self.scenario_analyzer = MacroScenarioAnalyzer()
        self.chart_generator = ChartGenerator()
        self.quant_analyzer = QuantAnalyzer()
        
        self._running = False
    
    async def start(self):
        if self._running:
            logger.warning("Market notification service is already running")
            return
        
        await self.message_queue.start()
        
        self.scheduler.add_daily_task(
            task_id='daily_market_report',
            name='每日股市热点报告',
            callback=self.send_daily_market_report,
            hour=8,
            minute=30
        )
        
        self.scheduler.add_weekly_task(
            task_id='weekly_summary_report',
            name='股市周报',
            callback=self.send_weekly_report,
            weekday=4,
            hour=8,
            minute=30
        )
        
        self.scheduler.add_daily_task(
            task_id='monthly_report',
            name='股市月报',
            callback=self.send_monthly_report,
            hour=8,
            minute=30
        )
        
        self.scheduler.add_daily_task(
            task_id='half_year_report',
            name='股市半年报',
            callback=self.send_half_year_report,
            hour=8,
            minute=30
        )
        
        self.scheduler.add_weekly_task(
            task_id='factor_recommendation_report',
            name='强势因子推荐报告',
            callback=self.send_factor_recommendation_report,
            weekday=0,
            hour=8,
            minute=30
        )
        
        await self.scheduler.start()
        self._running = True
        logger.info("Market notification service started")
    
    async def stop(self):
        self._running = False
        await self.scheduler.stop()
        await self.message_queue.stop()
        logger.info("Market notification service stopped")
    
    async def send_daily_market_report(self):
        try:
            report_data = await self._generate_daily_report()
            
            result = self.sender.send_daily_report(report_data)
            
            if result.get('success'):
                logger.info("Daily market report sent successfully")
            else:
                logger.error(f"Failed to send daily report: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error generating daily report: {str(e)}", exc_info=True)
    
    async def send_weekly_report(self):
        try:
            report_data = await self._generate_weekly_report()
            
            result = self.sender.send_weekly_report(report_data)
            
            if result.get('success'):
                logger.info("Weekly report sent successfully")
            else:
                logger.error(f"Failed to send weekly report: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error generating weekly report: {str(e)}", exc_info=True)
    
    async def send_monthly_report(self):
        today = datetime.now()
        if today.day != 1:
            return
        
        try:
            report_data = await self._generate_monthly_report()
            
            title = f"📊 A股统计月报 {today.strftime('%Y年%m月')}"
            content = self._format_monthly_report(report_data)
            
            result = self.sender.send_markdown(title, content)
            
            if result.get('success'):
                logger.info("Monthly report sent successfully")
            else:
                logger.error(f"Failed to send monthly report: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error generating monthly report: {str(e)}", exc_info=True)
    
    async def send_half_year_report(self):
        today = datetime.now()
        if today.month not in [1, 7] or today.day != 1:
            return
        
        try:
            report_data = await self._generate_half_year_report()
            
            half_year = "上半年" if today.month == 7 else "下半年"
            title = f"📊 A股统计半年报 {today.strftime('%Y年')}{half_year}"
            content = self._format_half_year_report(report_data)
            
            result = self.sender.send_markdown(title, content)
            
            if result.get('success'):
                logger.info("Half-year report sent successfully")
            else:
                logger.error(f"Failed to send half-year report: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error generating half-year report: {str(e)}", exc_info=True)
    
    async def send_factor_recommendation_report(self):
        try:
            report_data = await self._generate_factor_recommendation_report()
            
            title = f"🔮 下周A股强势因子与统计验证报告 {datetime.now().strftime('%Y-%m-%d')}"
            content = self._format_factor_recommendation_report(report_data)
            
            result = self.sender.send_markdown(title, content)
            
            if result.get('success'):
                logger.info("Factor recommendation report sent successfully")
            else:
                logger.error(f"Failed to send factor recommendation report: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error generating factor recommendation report: {str(e)}", exc_info=True)
    
    async def _generate_daily_report(self) -> Dict[str, Any]:
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        market_summary = self._get_global_market_summary()
        hot_topics = self._get_hot_topics()
        sector_performance = self._get_sector_performance()
        top_stocks = self._get_top_stocks()
        factor_analysis = self._get_factor_analysis()
        risk_warnings = self._get_risk_warnings()
        
        return {
            'date': date_str,
            'market_summary': market_summary,
            'hot_topics': hot_topics,
            'sector_performance': sector_performance,
            'top_stocks': top_stocks,
            'factor_analysis': factor_analysis,
            'risk_warnings': risk_warnings
        }
    
    async def _generate_weekly_report(self) -> Dict[str, Any]:
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=6)
        week_range = f"{week_start.strftime('%Y-%m-%d')} ~ {week_end.strftime('%Y-%m-%d')}"
        
        weekly_summary = self._get_weekly_summary()
        period_comparison = self._get_period_comparison()
        top_performers = self._get_top_performers()
        bottom_performers = self._get_bottom_performers()
        scenario_analysis = self._get_scenario_analysis()
        investment_suggestion = self._get_investment_suggestion()
        
        return {
            'week_range': week_range,
            'weekly_summary': weekly_summary,
            'period_comparison': period_comparison,
            'top_performers': top_performers,
            'bottom_performers': bottom_performers,
            'scenario_analysis': scenario_analysis,
            'investment_suggestion': investment_suggestion
        }
    
    async def _generate_monthly_report(self) -> Dict[str, Any]:
        now = datetime.now()
        month_start = now.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        month_range = f"{month_start.strftime('%Y-%m-%d')} ~ {month_end.strftime('%Y-%m-%d')}"
        
        monthly_data = self.data_simulator.generate_csi300_prices(
            start_date=month_start.strftime('%Y-%m-%d'),
            end_date=month_end.strftime('%Y-%m-%d')
        )
        
        summary = self.quant_analyzer.generate_statistical_summary(
            monthly_data, [('month', month_range)]
        )
        
        return {
            'month_range': month_range,
            'monthly_stats': summary['overall_stats'],
            'sector_performance': self._get_sector_performance(),
            'top_stocks': self._get_top_stocks(),
            'factor_performance': self._get_factor_performance(),
            'market_trend': self._analyze_market_trend(monthly_data)
        }
    
    async def _generate_half_year_report(self) -> Dict[str, Any]:
        now = datetime.now()
        if now.month >= 7:
            half_start = now.replace(month=7, day=1)
            half_end = now.replace(month=12, day=31)
            half_name = "下半年"
        else:
            half_start = now.replace(month=1, day=1)
            half_end = now.replace(month=6, day=30)
            half_name = "上半年"
        
        half_range = f"{half_start.strftime('%Y-%m-%d')} ~ {half_end.strftime('%Y-%m-%d')}"
        
        scenario_params = {
            'fed_rate_unchanged': True,
            'japan_korea_crash': False,
            'china_rescue_amount': 2 if now.month >= 7 else 0
        }
        
        half_data = self.data_simulator.generate_csi300_prices(
            start_date=half_start.strftime('%Y-%m-%d'),
            end_date=half_end.strftime('%Y-%m-%d'),
            scenario_params=scenario_params
        )
        
        periods = [
            ('2024下半年', '2024-07-01', '2024-12-31'),
            ('2025上半年', '2025-01-01', '2025-06-30'),
            ('2025下半年', '2025-07-01', '2025-12-31'),
            ('2026上半年', '2026-01-01', '2026-06-30'),
            (f'2026{half_name}', half_start.strftime('%Y-%m-%d'), half_end.strftime('%Y-%m-%d'))
        ]
        
        summary = self.quant_analyzer.generate_statistical_summary(half_data, periods)
        
        scenario_analysis = self.scenario_analyzer.analyze_scenario(scenario_params)
        
        return {
            'half_name': half_name,
            'half_range': half_range,
            'period_analysis': summary['period_analysis'],
            'overall_stats': summary['overall_stats'],
            'csi300_trends': summary.get('csi300_trends', {}),
            'scenario_analysis': scenario_analysis,
            'sector_recommendations': scenario_analysis.get('sector_impact', {}),
            'stock_recommendations': scenario_analysis.get('stock_recommendations', []),
            'risk_assessment': scenario_analysis.get('risk_assessment', {})
        }
    
    async def _generate_factor_recommendation_report(self) -> Dict[str, Any]:
        now = datetime.now()
        next_week_start = now + timedelta(days=(7 - now.weekday()))
        next_week_end = next_week_start + timedelta(days=6)
        week_range = f"{next_week_start.strftime('%Y-%m-%d')} ~ {next_week_end.strftime('%Y-%m-%d')}"
        
        strong_factors = self._get_strong_factors()
        factor_validation = self._validate_factors()
        tracking_factors = self._get_tracking_factors()
        trend_analysis = self._analyze_trend()
        
        return {
            'week_range': week_range,
            'strong_factors': strong_factors,
            'factor_validation': factor_validation,
            'tracking_factors': tracking_factors,
            'trend_analysis': trend_analysis
        }
    
    def _get_global_market_summary(self) -> Dict[str, Dict[str, float]]:
        return {
            '上证指数': {'price': 3285.67, 'change': 0.85},
            '沪深300': {'price': 4056.32, 'change': 1.02},
            '日经225': {'price': 32540.89, 'change': -1.23},
            '韩国KOSPI': {'price': 2580.45, 'change': -0.95},
            '纳斯达克': {'price': 18520.34, 'change': 0.56},
            '道琼斯': {'price': 39850.67, 'change': 0.32},
            '标普500': {'price': 5230.89, 'change': 0.44}
        }
    
    def _get_hot_topics(self) -> List[str]:
        return [
            '美联储维持利率不变，市场预期年底前降息',
            '日韩股市波动加大，投资者避险情绪升温',
            '中国央行逆回购操作释放流动性',
            'AI板块持续活跃，科技股领涨',
            '新能源板块回暖，光伏、锂电池表现亮眼',
            '房地产政策持续加码，央企地产股走强'
        ]
    
    def _get_sector_performance(self) -> List[Dict[str, Any]]:
        return [
            {'name': '银行', 'change': 2.35},
            {'name': '科技成长', 'change': 1.89},
            {'name': '新能源', 'change': 1.56},
            {'name': '基建', 'change': 1.34},
            {'name': '医药', 'change': 0.87}
        ]
    
    def _get_top_stocks(self) -> List[Dict[str, Any]]:
        return [
            {'name': '宁德时代', 'code': '300750.SZ', 'change': 5.23},
            {'name': '中际旭创', 'code': '300308.SZ', 'change': 4.89},
            {'name': '招商银行', 'code': '600036.SH', 'change': 3.56},
            {'name': '中国平安', 'code': '601318.SH', 'change': 3.21},
            {'name': '比亚迪', 'code': '002594.SZ', 'change': 2.98}
        ]
    
    def _get_factor_analysis(self) -> List[Dict[str, Any]]:
        return [
            {'name': '动量因子', 'ic': 0.18},
            {'name': '估值因子', 'ic': 0.15},
            {'name': '质量因子', 'ic': 0.12},
            {'name': '波动率因子', 'ic': -0.08},
            {'name': '流动性因子', 'ic': 0.05}
        ]
    
    def _get_factor_performance(self) -> List[Dict[str, Any]]:
        return [
            {'name': '动量因子', 'monthly_ic': 0.22, 'rank': 1},
            {'name': '估值因子', 'monthly_ic': 0.18, 'rank': 2},
            {'name': '质量因子', 'monthly_ic': 0.15, 'rank': 3},
            {'name': '流动性因子', 'monthly_ic': 0.08, 'rank': 4},
            {'name': '波动率因子', 'monthly_ic': -0.12, 'rank': 5}
        ]
    
    def _get_strong_factors(self) -> List[Dict[str, Any]]:
        return [
            {'name': '短期动量(ROC_5)', 'ic': 0.25, 'ir': 1.8, 'recommendation': '强烈推荐', 'reason': '近期市场趋势明显，短期动量因子表现优异'},
            {'name': '中期动量(ROC_20)', 'ic': 0.21, 'ir': 1.5, 'recommendation': '推荐', 'reason': '中期趋势持续，动量效应显著'},
            {'name': '估值因子(PB_ratio)', 'ic': 0.18, 'ir': 1.3, 'recommendation': '推荐', 'reason': '低估值板块有修复机会'},
            {'name': '质量因子(ROE)', 'ic': 0.15, 'ir': 1.2, 'recommendation': '中性', 'reason': '业绩确定性强的个股表现稳定'},
            {'name': '流动性因子(Volume_ratio)', 'ic': 0.12, 'ir': 1.0, 'recommendation': '中性', 'reason': '资金流向指标，辅助判断'}
        ]
    
    def _validate_factors(self) -> Dict[str, Any]:
        return {
            'validation_period': '2026年上半年',
            'total_factors': 15,
            'pass_rate': 87,
            'high_quality_factors': ['ROC_5', 'ROC_20', 'PB_ratio', 'ROE'],
            'factor_decay_analysis': [
                {'factor': 'ROC_5', 'half_life': 5, 'decay_rate': 0.15},
                {'factor': 'ROC_20', 'half_life': 15, 'decay_rate': 0.08},
                {'factor': 'PB_ratio', 'half_life': 60, 'decay_rate': 0.02},
                {'factor': 'ROE', 'half_life': 90, 'decay_rate': 0.01}
            ],
            'turnover_analysis': [
                {'factor': 'ROC_5', 'turnover': 65, 'cost_impact': -0.5},
                {'factor': 'ROC_20', 'turnover': 45, 'cost_impact': -0.3},
                {'factor': 'PB_ratio', 'turnover': 20, 'cost_impact': -0.1},
                {'factor': 'ROE', 'turnover': 15, 'cost_impact': -0.05}
            ]
        }
    
    def _get_tracking_factors(self) -> List[Dict[str, Any]]:
        return [
            {'name': '市场情绪(VIX)', 'current_value': 18.5, 'status': '正常', 'signal': '无'},
            {'name': '资金流向(北向资金)', 'current_value': '+52亿', 'status': '流入', 'signal': '看多'},
            {'name': '成交额(日均)', 'current_value': '8500亿', 'status': '活跃', 'signal': '偏多'},
            {'name': '涨跌家数比', 'current_value': '1.8:1', 'status': '偏多', 'signal': '看多'},
            {'name': '行业扩散度', 'current_value': '65%', 'status': '中等', 'signal': '无'},
            {'name': '均线多头排列', 'current_value': '72%', 'status': '偏多', 'signal': '看多'}
        ]
    
    def _analyze_trend(self) -> Dict[str, Any]:
        return {
            'short_term': {
                'trend': '震荡上行',
                'support': 3200,
                'resistance': 3350,
                'probability': 65
            },
            'medium_term': {
                'trend': '上升趋势',
                'support': 3100,
                'resistance': 3500,
                'probability': 75
            },
            'long_term': {
                'trend': '强势行情',
                'target': 3800,
                'timeframe': '3-6个月',
                'probability': 80
            },
            'key_levels': [
                {'level': 3200, 'type': '支撑', 'strength': '强'},
                {'level': 3300, 'type': '压力', 'strength': '中'},
                {'level': 3350, 'type': '压力', 'strength': '强'},
                {'level': 3500, 'type': '目标', 'strength': '中'}
            ],
            'pattern_analysis': [
                {'pattern': '均线多头排列', 'signal': '看多', 'reliability': '高'},
                {'pattern': '量价配合', 'signal': '看多', 'reliability': '中高'},
                {'pattern': 'MACD金叉', 'signal': '看多', 'reliability': '中'},
                {'pattern': 'RSI超买', 'signal': '警惕回调', 'reliability': '中'}
            ]
        }
    
    def _analyze_market_trend(self, data) -> Dict[str, Any]:
        return {
            'trend': '震荡上行',
            'momentum': 'positive',
            'volatility': 'moderate',
            'volume_trend': 'increasing'
        }
    
    def _get_risk_warnings(self) -> List[str]:
        return [
            '日韩股市波动可能传导至A股',
            '美联储政策转向风险需关注',
            '地缘政治紧张局势持续'
        ]
    
    def _get_weekly_summary(self) -> Dict[str, Any]:
        return {
            'market_return': 3.25,
            'volatility': 18.56,
            'volume': 685000000000
        }
    
    def _get_period_comparison(self) -> Dict[str, Dict[str, float]]:
        return {
            '2024下半年': {'return': -4.01},
            '2025上半年': {'return': 6.31},
            '2025下半年': {'return': 13.82},
            '2026上半年': {'return': 2.41},
            '2026下半年至今': {'return': 8.56}
        }
    
    def _get_top_performers(self) -> List[Dict[str, Any]]:
        return [
            {'name': '科技成长', 'return': 8.23},
            {'name': '新能源', 'return': 6.56},
            {'name': '银行', 'return': 5.89},
            {'name': '基建', 'return': 4.34},
            {'name': '医药', 'return': 3.21}
        ]
    
    def _get_bottom_performers(self) -> List[Dict[str, Any]]:
        return [
            {'name': '半导体', 'return': -2.34},
            {'name': '消费', 'return': -1.89},
            {'name': '资源品', 'return': -1.23},
            {'name': '出口相关', 'return': -0.87},
            {'name': '房地产', 'return': 0.56}
        ]
    
    def _get_scenario_analysis(self) -> Dict[str, Any]:
        scenario_params = {
            'fed_rate_unchanged': True,
            'japan_korea_crash': False,
            'china_rescue_amount': 0
        }
        analysis = self.scenario_analyzer.analyze_scenario(scenario_params)
        
        return {
            'description': analysis['scenario_description'],
            'expected_return': analysis['market_impact']['total_expected_return'],
            'risk_level': analysis['risk_assessment']['total_risk_level']
        }
    
    def _get_investment_suggestion(self) -> str:
        return (
            "本周市场整体表现较好，科技成长和新能源板块领涨。建议继续关注流动性宽松"
            "带来的投资机会，重点配置金融、科技成长和基建板块。短期注意防范日韩"
            "股市波动传导风险，建议适当控制仓位，保持灵活配置。"
        )
    
    def _format_monthly_report(self, report: Dict[str, Any]) -> str:
        sections = []
        
        sections.append(f"## 📅 {report.get('month_range', '')}")
        
        stats = report.get('monthly_stats', {})
        sections.append("### 📊 月度统计概览")
        sections.append(f"- **交易天数**: {stats.get('total_days', 0)}")
        sections.append(f"- **区间收益率**: {stats.get('total_return', 0) * 100:.2f}%")
        sections.append(f"- **年化收益率**: {stats.get('annualized_return', 0) * 100:.2f}%")
        sections.append(f"- **夏普比率**: {stats.get('sharpe_ratio', 0):.2f}")
        sections.append(f"- **最大回撤**: {stats.get('max_drawdown', 0) * 100:.2f}%")
        sections.append(f"- **波动率**: {stats.get('annualized_volatility', 0) * 100:.2f}%")
        sections.append(f"- **胜率**: {stats.get('win_rate', 0) * 100:.1f}%")
        
        if 'sector_performance' in report:
            sections.append("\n### 📈 行业表现")
            for sector in report['sector_performance'][:5]:
                change_str = f"+{sector['change']}%" if sector['change'] > 0 else f"{sector['change']}%"
                sections.append(f"- **{sector['name']}**: {change_str}")
        
        if 'factor_performance' in report:
            sections.append("\n### 📊 因子表现排名")
            for factor in report['factor_performance']:
                sections.append(f"- **{factor['name']}**: IC={factor['monthly_ic']:.3f} (排名第{factor['rank']})")
        
        if 'market_trend' in report:
            trend = report['market_trend']
            sections.append("\n### 🔮 趋势分析")
            sections.append(f"- **趋势方向**: {trend.get('trend', '')}")
            sections.append(f"- **动量状态**: {trend.get('momentum', '')}")
            sections.append(f"- **波动率**: {trend.get('volatility', '')}")
        
        return '\n\n'.join(sections)
    
    def _format_half_year_report(self, report: Dict[str, Any]) -> str:
        sections = []
        
        sections.append(f"## 📅 2026年{report.get('half_name', '')}")
        sections.append(f"**统计区间**: {report.get('half_range', '')}")
        
        if 'period_analysis' in report:
            sections.append("\n### 📊 各时间段对比")
            sections.append("| 时间段 | 收益率 | 年化收益 | 夏普比率 | 最大回撤 |")
            sections.append("|--------|--------|----------|----------|----------|")
            for period, data in report['period_analysis'].items():
                ret_str = f"+{data['return']*100:.2f}%" if data['return'] > 0 else f"{data['return']*100:.2f}%"
                ann_str = f"+{data['annualized_return']*100:.2f}%" if data['annualized_return'] > 0 else f"{data['annualized_return']*100:.2f}%"
                dd_str = f"{data['max_drawdown']*100:.2f}%"
                sections.append(f"| {period} | {ret_str} | {ann_str} | {data['sharpe_ratio']:.2f} | {dd_str} |")
        
        if 'overall_stats' in report:
            stats = report['overall_stats']
            sections.append("\n### 📈 整体统计")
            sections.append(f"- **交易天数**: {stats.get('total_days', 0)}")
            sections.append(f"- **区间收益率**: {stats.get('total_return', 0) * 100:.2f}%")
            sections.append(f"- **年化收益率**: {stats.get('annualized_return', 0) * 100:.2f}%")
            sections.append(f"- **夏普比率**: {stats.get('sharpe_ratio', 0):.2f}")
            sections.append(f"- **最大回撤**: {stats.get('max_drawdown', 0) * 100:.2f}%")
        
        if 'scenario_analysis' in report:
            scenario = report['scenario_analysis']
            sections.append("\n### 🔮 宏观情景分析")
            sections.append(f"- **情景描述**: {scenario.get('scenario_description', '')}")
            expected_return = scenario['market_impact']['total_expected_return']
            ret_str = f"+{expected_return*100:.1f}%" if expected_return > 0 else f"{expected_return*100:.1f}%"
            sections.append(f"- **预期收益**: {ret_str}")
        
        if 'sector_recommendations' in report:
            sections.append("\n### 🎯 行业评级")
            for sector, data in report['sector_recommendations'].items():
                sections.append(f"- **{sector}**: {data['rating']} | 预期收益: {data['expected_return']*100:.1f}%")
        
        if 'risk_assessment' in report:
            risk = report['risk_assessment']
            sections.append("\n### ⚠️ 风险评估")
            sections.append(f"- **整体风险等级**: {risk.get('total_risk_level', '')}")
            for r in risk.get('key_risks', [])[:3]:
                sections.append(f"- **{r['risk']}**: 概率{r['probability']*100:.0f}% | 影响{r['impact']*100:.0f}% | {r['level']}")
        
        return '\n\n'.join(sections)
    
    def _format_factor_recommendation_report(self, report: Dict[str, Any]) -> str:
        sections = []
        
        sections.append(f"## 📅 {report.get('week_range', '')}")
        
        sections.append("\n### 🏆 强势因子推荐")
        for factor in report.get('strong_factors', []):
            sections.append(f"**{factor['name']}**")
            sections.append(f"- IC: {factor['ic']:.3f} | IR: {factor['ir']:.2f}")
            sections.append(f"- 评级: {factor['recommendation']}")
            sections.append(f"- 理由: {factor['reason']}")
            sections.append("")
        
        if 'factor_validation' in report:
            validation = report['factor_validation']
            sections.append("\n### ✅ 因子验证报告")
            sections.append(f"- **验证周期**: {validation.get('validation_period', '')}")
            sections.append(f"- **因子总数**: {validation.get('total_factors', 0)}")
            sections.append(f"- **通过率**: {validation.get('pass_rate', 0)}%")
            sections.append(f"- **高质量因子**: {', '.join(validation.get('high_quality_factors', []))}")
            
            sections.append("\n**因子衰减分析**:")
            for decay in validation.get('factor_decay_analysis', []):
                sections.append(f"- {decay['factor']}: 半衰期={decay['half_life']}天, 衰减率={decay['decay_rate']*100:.1f}%")
            
            sections.append("\n**换手率分析**:")
            for turnover in validation.get('turnover_analysis', []):
                cost_str = f"{turnover['cost_impact']:.1f}%"
                sections.append(f"- {turnover['factor']}: 换手率={turnover['turnover']}%, 成本影响={cost_str}")
        
        if 'tracking_factors' in report:
            sections.append("\n### 📡 盯盘因子")
            sections.append("| 因子 | 当前值 | 状态 | 信号 |")
            sections.append("|------|--------|------|------|")
            for factor in report.get('tracking_factors', []):
                sections.append(f"| {factor['name']} | {factor['current_value']} | {factor['status']} | {factor['signal']} |")
        
        if 'trend_analysis' in report:
            trend = report['trend_analysis']
            sections.append("\n### 📈 后续走势分析")
            
            sections.append("\n**短期趋势**:")
            st = trend['short_term']
            sections.append(f"- 方向: {st['trend']}")
            sections.append(f"- 支撑: {st['support']} | 压力: {st['resistance']}")
            sections.append(f"- 概率: {st['probability']}%")
            
            sections.append("\n**中期趋势**:")
            mt = trend['medium_term']
            sections.append(f"- 方向: {mt['trend']}")
            sections.append(f"- 支撑: {mt['support']} | 压力: {mt['resistance']}")
            sections.append(f"- 概率: {mt['probability']}%")
            
            sections.append("\n**长期趋势**:")
            lt = trend['long_term']
            sections.append(f"- 方向: {lt['trend']}")
            sections.append(f"- 目标: {lt['target']} | 时间: {lt['timeframe']}")
            sections.append(f"- 概率: {lt['probability']}%")
            
            sections.append("\n**关键价位**:")
            for level in trend.get('key_levels', []):
                sections.append(f"- {level['level']}: {level['type']}位 (强度: {level['strength']})")
            
            sections.append("\n**技术形态**:")
            for pattern in trend.get('pattern_analysis', []):
                sections.append(f"- {pattern['pattern']}: {pattern['signal']} (可靠性: {pattern['reliability']})")
        
        return '\n\n'.join(sections)