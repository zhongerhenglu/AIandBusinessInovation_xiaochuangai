import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notification.market_notification_service import MarketNotificationService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('notification_service.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


async def main():
    logger.info("=" * 60)
    logger.info("启动市场通知服务")
    logger.info("=" * 60)
    
    service = MarketNotificationService()
    
    logger.info("配置定时任务:")
    logger.info("  - 每日 8:30 发送股市热点报告")
    logger.info("  - 每周五 8:30 发送股市周报")
    
    await service.start()
    logger.info("✓ 市场通知服务已启动")
    logger.info("✓ PushPlus Token已配置")
    logger.info("✓ 消息队列已启动")
    logger.info("✓ 定时任务已注册")
    
    logger.info("\n服务运行中... (按 Ctrl+C 停止)")
    
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        logger.info("\n正在停止服务...")
        await service.stop()
        logger.info("✓ 市场通知服务已停止")


if __name__ == '__main__':
    asyncio.run(main())