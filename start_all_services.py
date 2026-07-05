import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notification.market_notification_service import MarketNotificationService
from notification.knowledge_notification_service import KnowledgeNotificationService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('all_services.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


async def main():
    logger.info("=" * 60)
    logger.info("启动Super Agent所有服务")
    logger.info("=" * 60)
    
    market_service = MarketNotificationService()
    knowledge_service = KnowledgeNotificationService()
    
    logger.info("\n📈 市场通知服务配置:")
    logger.info("  - 每日8:30: 股市热点报告")
    logger.info("  - 每周五8:30: 股市周报")
    logger.info("  - 每月1日8:30: 股市月报")
    logger.info("  - 每年1月/7月1日8:30: 股市半年报")
    logger.info("  - 每周一8:30: 强势因子推荐报告")
    
    logger.info("\n📚 知识通知服务配置:")
    logger.info("  - 每日8:00: 知识体系更新统计")
    logger.info("  - 每日12:00: 知识体系更新统计")
    logger.info("  - 每日16:00: 知识体系更新统计")
    logger.info("  - 每日20:00: 知识体系更新统计")
    logger.info("  - 每日24:00: 知识体系更新统计")
    
    logger.info("\n🚀 正在启动服务...")
    
    await market_service.start()
    logger.info("✓ 市场通知服务已启动")
    
    await knowledge_service.start()
    logger.info("✓ 知识通知服务已启动")
    
    logger.info("\n✅ 所有服务启动完成")
    logger.info("服务运行中... (按 Ctrl+C 停止)")
    
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        logger.info("\n正在停止服务...")
        await market_service.stop()
        await knowledge_service.stop()
        logger.info("✓ 所有服务已停止")


if __name__ == '__main__':
    asyncio.run(main())