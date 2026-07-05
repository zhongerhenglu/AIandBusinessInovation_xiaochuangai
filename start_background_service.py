import asyncio
import logging
import sys
import os
import time
import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notification import PushPlusSender, NotificationScheduler, MessageQueue
from factor_library import FactorLibrary, FactorAnalyzer
from knowledge import EnhancedKnowledgeBase
from quant.data_simulator import DataSimulator
from quant.quant_analyzer import QuantAnalyzer
from quant.chart_generator import ChartGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('background_service.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


class BackgroundService:
    def __init__(self):
        self.sender = PushPlusSender()
        self.scheduler = NotificationScheduler()
        self.message_queue = MessageQueue()
        self.message_queue.set_sender(self.sender)
        
        self.factor_library = FactorLibrary()
        self.factor_analyzer = FactorAnalyzer()
        self.knowledge_base = EnhancedKnowledgeBase()
        self.data_simulator = DataSimulator()
        self.quant_analyzer = QuantAnalyzer()
        self.chart_generator = ChartGenerator()
        
        self._running = False
        self._shutdown_event = asyncio.Event()
    
    async def start(self):
        if self._running:
            logger.warning("Background service is already running")
            return
        
        await self.message_queue.start()
        
        self.scheduler.add_daily_task(
            task_id='morning_factor_report',
            name='早间因子报告',
            callback=self.send_morning_factor_report,
            hour=8,
            minute=0
        )
        
        self.scheduler.add_daily_task(
            task_id='noon_factor_report',
            name='午间因子报告',
            callback=self.send_noon_factor_report,
            hour=12,
            minute=0
        )
        
        self.scheduler.add_daily_task(
            task_id='afternoon_factor_report',
            name='下午因子报告',
            callback=self.send_afternoon_factor_report,
            hour=16,
            minute=0
        )
        
        self.scheduler.add_daily_task(
            task_id='evening_factor_report',
            name='晚间因子报告',
            callback=self.send_evening_factor_report,
            hour=20,
            minute=0
        )
        
        self.scheduler.add_daily_task(
            task_id='daily_summary_report',
            name='每日因子汇总报告',
            callback=self.send_daily_factor_summary,
            hour=24,
            minute=0
        )
        
        await self.scheduler.start()
        self._running = True
        logger.info("=" * 60)
        logger.info("Background Service Started")
        logger.info("=" * 60)
        logger.info("Scheduled tasks:")
        logger.info("  - 08:00 早间因子报告")
        logger.info("  - 12:00 午间因子报告")
        logger.info("  - 16:00 下午因子报告")
        logger.info("  - 20:00 晚间因子报告")
        logger.info("  - 24:00 每日因子汇总报告")
        logger.info("=" * 60)
    
    async def stop(self):
        self._running = False
        self._shutdown_event.set()
        await self.scheduler.stop()
        await self.message_queue.stop()
        logger.info("Background service stopped")
    
    async def send_morning_factor_report(self):
        try:
            report = await self._generate_factor_report("早间")
            title = f"📊 早间因子报告 {time.strftime('%Y-%m-%d %H:%M')}"
            result = self.sender.send_markdown(title, report)
            if result.get('success'):
                logger.info("Morning factor report sent successfully")
            else:
                logger.error(f"Failed to send morning report: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error generating morning factor report: {str(e)}", exc_info=True)
    
    async def send_noon_factor_report(self):
        try:
            report = await self._generate_factor_report("午间")
            title = f"📊 午间因子报告 {time.strftime('%Y-%m-%d %H:%M')}"
            result = self.sender.send_markdown(title, report)
            if result.get('success'):
                logger.info("Noon factor report sent successfully")
            else:
                logger.error(f"Failed to send noon report: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error generating noon factor report: {str(e)}", exc_info=True)
    
    async def send_afternoon_factor_report(self):
        try:
            report = await self._generate_factor_report("下午")
            title = f"📊 下午因子报告 {time.strftime('%Y-%m-%d %H:%M')}"
            result = self.sender.send_markdown(title, report)
            if result.get('success'):
                logger.info("Afternoon factor report sent successfully")
            else:
                logger.error(f"Failed to send afternoon report: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error generating afternoon factor report: {str(e)}", exc_info=True)
    
    async def send_evening_factor_report(self):
        try:
            report = await self._generate_factor_report("晚间")
            title = f"📊 晚间因子报告 {time.strftime('%Y-%m-%d %H:%M')}"
            result = self.sender.send_markdown(title, report)
            if result.get('success'):
                logger.info("Evening factor report sent successfully")
            else:
                logger.error(f"Failed to send evening report: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error generating evening factor report: {str(e)}", exc_info=True)
    
    async def send_daily_factor_summary(self):
        try:
            report = await self._generate_daily_summary_report()
            title = f"📊 每日因子汇总报告 {time.strftime('%Y-%m-%d')}"
            result = self.sender.send_markdown(title, report)
            if result.get('success'):
                logger.info("Daily factor summary report sent successfully")
            else:
                logger.error(f"Failed to send daily summary report: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error generating daily factor summary report: {str(e)}", exc_info=True)
    
    async def _generate_factor_report(self, period: str) -> str:
        sections = []
        
        sections.append(f"## 📅 {period}因子报告")
        sections.append(f"**生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        factor_performance = self._get_factor_performance_data()
        sections.append("\n### 🏆 因子表现排行")
        for i, factor in enumerate(factor_performance[:10], 1):
            ic_str = f"+{factor['ic']*100:.2f}" if factor['ic'] > 0 else f"{factor['ic']*100:.2f}"
            sections.append(f"{i}. **{factor['name']}**: IC={ic_str}% | IR={factor['ir']:.2f} | {factor['category']}")
        
        tracking_factors = self._get_tracking_factors()
        sections.append("\n### 📡 盯盘因子监控")
        sections.append("| 指标 | 当前值 | 状态 | 信号 |")
        sections.append("|------|--------|------|------|")
        for factor in tracking_factors:
            sections.append(f"| {factor['name']} | {factor['current_value']} | {factor['status']} | {factor['signal']} |")
        
        strong_factors = self._get_strong_factors()
        sections.append("\n### 💎 强势因子推荐")
        for factor in strong_factors[:5]:
            sections.append(f"**{factor['name']}**")
            sections.append(f"- IC: {factor['ic']:.3f} | IR: {factor['ir']:.2f}")
            sections.append(f"- 评级: {factor['recommendation']}")
            sections.append(f"- 理由: {factor['reason']}")
            sections.append("")
        
        stats = self._get_market_statistics()
        sections.append("\n### 📈 市场统计数据")
        sections.append(f"- **上证指数**: {stats['shanghai']['price']} ({stats['shanghai']['change']:+.2f}%)")
        sections.append(f"- **沪深300**: {stats['csi300']['price']} ({stats['csi300']['change']:+.2f}%)")
        sections.append(f"- **成交额**: {stats['volume']}")
        sections.append(f"- **涨跌家数比**: {stats['advance_decline_ratio']}")
        sections.append(f"- **北向资金**: {stats['northbound']}")
        
        knowledge_stats = self.knowledge_base.get_stats()
        sections.append("\n### 🧠 知识体系更新")
        sections.append(f"- **总页面数**: {knowledge_stats['total_pages']}")
        sections.append(f"- **图谱节点**: {knowledge_stats['total_nodes']}")
        sections.append(f"- **今日更新**: {knowledge_stats['today_updates']}")
        
        return '\n\n'.join(sections)
    
    async def _generate_daily_summary_report(self) -> str:
        sections = []
        
        sections.append(f"## 📅 每日因子汇总报告")
        sections.append(f"**日期**: {time.strftime('%Y-%m-%d')}")
        
        stats = self._get_market_statistics()
        sections.append("\n### 📊 市场概况")
        sections.append(f"- **上证指数**: {stats['shanghai']['price']} ({stats['shanghai']['change']:+.2f}%)")
        sections.append(f"- **沪深300**: {stats['csi300']['price']} ({stats['csi300']['change']:+.2f}%)")
        sections.append(f"- **日经225**: {stats['nikkei']['price']} ({stats['nikkei']['change']:+.2f}%)")
        sections.append(f"- **纳斯达克**: {stats['nasdaq']['price']} ({stats['nasdaq']['change']:+.2f}%)")
        
        factor_performance = self._get_factor_performance_data()
        sections.append("\n### 🏆 今日因子表现TOP10")
        sections.append("| 排名 | 因子名称 | IC | IR | 类别 |")
        sections.append("|------|----------|-----|-----|------|")
        for i, factor in enumerate(factor_performance[:10], 1):
            ic_str = f"+{factor['ic']*100:.2f}" if factor['ic'] > 0 else f"{factor['ic']*100:.2f}"
            sections.append(f"| {i} | {factor['name']} | {ic_str}% | {factor['ir']:.2f} | {factor['category']} |")
        
        strong_factors = self._get_strong_factors()
        sections.append("\n### 💎 强势因子推荐")
        for factor in strong_factors[:5]:
            sections.append(f"**{factor['name']}**")
            sections.append(f"- IC: {factor['ic']:.3f} | IR: {factor['ir']:.2f}")
            sections.append(f"- 评级: {factor['recommendation']}")
            sections.append(f"- 理由: {factor['reason']}")
            sections.append("")
        
        tracking_factors = self._get_tracking_factors()
        sections.append("\n### 📡 盯盘因子监控")
        sections.append("| 指标 | 当前值 | 状态 | 信号 |")
        sections.append("|------|--------|------|------|")
        for factor in tracking_factors:
            sections.append(f"| {factor['name']} | {factor['current_value']} | {factor['status']} | {factor['signal']} |")
        
        trend_analysis = self._get_trend_analysis()
        sections.append("\n### 🔮 趋势分析")
        sections.append(f"- **短期趋势**: {trend_analysis['short_term']['trend']}")
        sections.append(f"- **支撑/压力**: {trend_analysis['short_term']['support']} / {trend_analysis['short_term']['resistance']}")
        sections.append(f"- **中期趋势**: {trend_analysis['medium_term']['trend']}")
        sections.append(f"- **目标位**: {trend_analysis['medium_term']['target']}")
        
        knowledge_stats = self.knowledge_base.get_stats()
        sections.append("\n### 🧠 知识体系今日更新")
        sections.append(f"- **总页面数**: {knowledge_stats['total_pages']}")
        sections.append(f"- **图谱节点**: {knowledge_stats['total_nodes']}")
        sections.append(f"- **今日更新**: {knowledge_stats['today_updates']}")
        
        recent_updates = self.knowledge_base.get_recent_updates(hours=24)
        if recent_updates:
            sections.append("\n**今日新增/更新页面**:")
            for update in recent_updates[:5]:
                sections.append(f"- {update.get('title', '')}")
        
        return '\n\n'.join(sections)
    
    def _get_factor_performance_data(self):
        factors = [
            {'name': 'ROC_5', 'ic': 0.25, 'ir': 1.8, 'category': '动量'},
            {'name': 'ROC_20', 'ic': 0.21, 'ir': 1.5, 'category': '动量'},
            {'name': 'ROC_60', 'ic': 0.18, 'ir': 1.3, 'category': '动量'},
            {'name': 'PB_ratio', 'ic': 0.16, 'ir': 1.2, 'category': '估值'},
            {'name': 'PE_ratio', 'ic': 0.14, 'ir': 1.1, 'category': '估值'},
            {'name': 'ROE', 'ic': 0.15, 'ir': 1.2, 'category': '质量'},
            {'name': 'ROA', 'ic': 0.12, 'ir': 1.0, 'category': '质量'},
            {'name': 'ATR', 'ic': -0.08, 'ir': 0.6, 'category': '波动率'},
            {'name': 'STD_20', 'ic': -0.10, 'ir': 0.5, 'category': '波动率'},
            {'name': 'Volume_ratio', 'ic': 0.11, 'ir': 0.9, 'category': '流动性'},
            {'name': 'MFI', 'ic': 0.09, 'ir': 0.8, 'category': '流动性'},
            {'name': 'MA_cross', 'ic': 0.17, 'ir': 1.2, 'category': '技术'},
            {'name': 'Beta', 'ic': 0.05, 'ir': 0.4, 'category': '风险'},
            {'name': 'EV_EBITDA', 'ic': 0.13, 'ir': 1.0, 'category': '估值'},
            {'name': 'Dividend_yield', 'ic': 0.08, 'ir': 0.7, 'category': '收益'}
        ]
        return sorted(factors, key=lambda x: abs(x['ic']), reverse=True)
    
    def _get_tracking_factors(self):
        return [
            {'name': '市场情绪(VIX)', 'current_value': '18.5', 'status': '正常', 'signal': '无'},
            {'name': '北向资金', 'current_value': '+52亿', 'status': '流入', 'signal': '看多'},
            {'name': '成交额', 'current_value': '8500亿', 'status': '活跃', 'signal': '偏多'},
            {'name': '涨跌家数比', 'current_value': '1.8:1', 'status': '偏多', 'signal': '看多'},
            {'name': '行业扩散度', 'current_value': '65%', 'status': '中等', 'signal': '无'},
            {'name': '均线多头排列', 'current_value': '72%', 'status': '偏多', 'signal': '看多'},
            {'name': 'MACD', 'current_value': '金叉', 'status': '看多', 'signal': '看多'},
            {'name': 'RSI', 'current_value': '62', 'status': '偏强', 'signal': '无'}
        ]
    
    def _get_strong_factors(self):
        return [
            {'name': '短期动量(ROC_5)', 'ic': 0.25, 'ir': 1.8, 'recommendation': '强烈推荐', 'reason': '近期市场趋势明显，短期动量因子表现优异'},
            {'name': '中期动量(ROC_20)', 'ic': 0.21, 'ir': 1.5, 'recommendation': '推荐', 'reason': '中期趋势持续，动量效应显著'},
            {'name': '估值因子(PB_ratio)', 'ic': 0.16, 'ir': 1.2, 'recommendation': '推荐', 'reason': '低估值板块有修复机会'},
            {'name': '质量因子(ROE)', 'ic': 0.15, 'ir': 1.2, 'recommendation': '中性', 'reason': '业绩确定性强的个股表现稳定'},
            {'name': '均线交叉(MA_cross)', 'ic': 0.17, 'ir': 1.2, 'recommendation': '推荐', 'reason': '技术面支撑，趋势明确'}
        ]
    
    def _get_market_statistics(self):
        return {
            'shanghai': {'price': 3285.67, 'change': 0.85},
            'csi300': {'price': 4056.32, 'change': 1.02},
            'nikkei': {'price': 32540.89, 'change': -1.23},
            'nasdaq': {'price': 18520.34, 'change': 0.56},
            'volume': '8500亿',
            'advance_decline_ratio': '1.8:1',
            'northbound': '+52亿'
        }
    
    def _get_trend_analysis(self):
        return {
            'short_term': {'trend': '震荡上行', 'support': 3200, 'resistance': 3350},
            'medium_term': {'trend': '上升趋势', 'support': 3100, 'target': 3500},
            'long_term': {'trend': '强势行情', 'target': 3800, 'timeframe': '3-6个月'}
        }


async def main():
    service = BackgroundService()
    
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(service.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    await service.start()
    
    try:
        while service._running:
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        pass
    finally:
        await service.stop()


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Super Agent Background Service")
    logger.info("=" * 60)
    logger.info("Starting background service...")
    
    asyncio.run(main())