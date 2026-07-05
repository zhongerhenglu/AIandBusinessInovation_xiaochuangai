import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notification import PushPlusSender, NotificationScheduler, MessageQueue, Message
from notification.market_notification_service import MarketNotificationService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_notification.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


async def test_pushplus_sender():
    logger.info("=" * 60)
    logger.info("测试1: PushPlus消息发送")
    logger.info("=" * 60)
    
    sender = PushPlusSender()
    
    test_title = "📊 测试消息 - 股市简报"
    test_content = """## 测试消息

这是一条测试消息，用于验证PushPlus发送功能。

### 市场数据
- **上证指数**: 3285.67 (+0.85%)
- **沪深300**: 4056.32 (+1.02%)

### 热点资讯
1. 测试消息功能正常
2. 通知服务已就绪

### 风险提示
- 测试环境，非真实数据"""
    
    result = sender.send_markdown(test_title, test_content)
    logger.info(f"发送结果: {result}")
    
    if result.get('success'):
        logger.info("✓ PushPlus发送成功")
    else:
        logger.error(f"✗ PushPlus发送失败: {result.get('error')}")
    
    return result


async def test_message_queue():
    logger.info("\n" + "=" * 60)
    logger.info("测试2: 消息队列")
    logger.info("=" * 60)
    
    sender = PushPlusSender()
    queue = MessageQueue()
    queue.set_sender(sender)
    
    await queue.start()
    
    message_id = queue.create_and_enqueue(
        title="📋 队列测试消息",
        content="## 消息队列测试\n\n这是通过消息队列发送的测试消息。",
        priority=1
    )
    
    logger.info(f"消息已入队: {message_id}")
    logger.info(f"队列大小: {queue.get_queue_size()}")
    
    await asyncio.sleep(5)
    
    message = queue.get_message_status(message_id)
    if message:
        logger.info(f"消息状态: {message.status}")
        if message.status == 'sent':
            logger.info("✓ 消息队列测试成功")
        else:
            logger.warning(f"✗ 消息状态: {message.status}, 错误: {message.error}")
    
    await queue.stop()
    
    return True


async def test_task_scheduler():
    logger.info("\n" + "=" * 60)
    logger.info("测试3: 定时任务调度器")
    logger.info("=" * 60)
    
    scheduler = NotificationScheduler()
    task_results = []
    
    def test_callback(task_name: str):
        logger.info(f"定时任务执行: {task_name}")
        task_results.append(task_name)
    
    scheduler.add_daily_task(
        task_id='test_daily_task',
        name='测试每日任务',
        callback=test_callback,
        hour=0,
        minute=0,
        task_name='测试任务'
    )
    
    await scheduler.start()
    
    await asyncio.sleep(2)
    
    await scheduler.stop()
    
    if task_results:
        logger.info("✓ 定时任务调度器测试成功")
    else:
        logger.warning("✗ 定时任务未执行（可能需要等待到下一分钟）")
    
    return True


async def test_market_notification_service():
    logger.info("\n" + "=" * 60)
    logger.info("测试4: 市场通知服务")
    logger.info("=" * 60)
    
    service = MarketNotificationService()
    
    logger.info("测试生成日报数据...")
    daily_report = await service._generate_daily_report()
    logger.info(f"日报数据包含: {list(daily_report.keys())}")
    logger.info(f"市场概览: {daily_report.get('market_summary', {})}")
    logger.info(f"热点资讯数量: {len(daily_report.get('hot_topics', []))}")
    
    logger.info("\n测试生成周报数据...")
    weekly_report = await service._generate_weekly_report()
    logger.info(f"周报数据包含: {list(weekly_report.keys())}")
    logger.info(f"周期间范围: {weekly_report.get('week_range', '')}")
    logger.info(f"周总结: {weekly_report.get('weekly_summary', {})}")
    
    logger.info("\n测试发送日报...")
    result = service.sender.send_daily_report(daily_report)
    if result.get('success'):
        logger.info("✓ 日报发送成功")
    else:
        logger.error(f"✗ 日报发送失败: {result.get('error')}")
    
    logger.info("\n测试发送周报...")
    result = service.sender.send_weekly_report(weekly_report)
    if result.get('success'):
        logger.info("✓ 周报发送成功")
    else:
        logger.error(f"✗ 周报发送失败: {result.get('error')}")
    
    return True


async def main():
    logger.info("=" * 60)
    logger.info("通知服务测试套件")
    logger.info("=" * 60)
    
    try:
        await test_pushplus_sender()
        await test_message_queue()
        await test_task_scheduler()
        await test_market_notification_service()
        
        logger.info("\n" + "=" * 60)
        logger.info("所有测试完成!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"测试失败: {str(e)}", exc_info=True)
        raise


if __name__ == '__main__':
    asyncio.run(main())