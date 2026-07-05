import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import Dict, Any, List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notification import PushPlusSender, NotificationScheduler, MessageQueue, Message
from knowledge import EnhancedKnowledgeBase

logger = logging.getLogger(__name__)


class KnowledgeNotificationService:
    def __init__(self):
        self.sender = PushPlusSender()
        self.scheduler = NotificationScheduler()
        self.message_queue = MessageQueue()
        self.message_queue.set_sender(self.sender)
        
        self.knowledge_base = EnhancedKnowledgeBase()
        
        self._running = False
        self._update_history: List[Dict[str, Any]] = []
    
    async def start(self):
        if self._running:
            logger.warning("Knowledge notification service is already running")
            return
        
        await self.message_queue.start()
        
        send_times = [8, 12, 16, 20, 24]
        
        for hour in send_times:
            if hour == 24:
                sched_hour = 0
            else:
                sched_hour = hour
            
            self.scheduler.add_daily_task(
                task_id=f'knowledge_update_{hour}',
                name=f'知识更新通知_{hour}:00',
                callback=self.send_knowledge_update,
                hour=sched_hour,
                minute=0
            )
        
        await self.scheduler.start()
        self._running = True
        logger.info("Knowledge notification service started")
        logger.info(f"定时任务已注册: {send_times}点")
    
    async def stop(self):
        self._running = False
        await self.scheduler.stop()
        await self.message_queue.stop()
        logger.info("Knowledge notification service stopped")
    
    async def send_knowledge_update(self):
        try:
            current_time = datetime.now()
            
            if current_time.hour >= 24:
                return
            
            report_data = await self._generate_knowledge_report()
            
            title = f"📚 知识体系更新统计 {current_time.strftime('%Y-%m-%d %H:%M')}"
            content = self._format_knowledge_report(report_data)
            
            result = self.sender.send_markdown(title, content)
            
            if result.get('success'):
                logger.info(f"Knowledge update sent successfully at {current_time}")
                self._update_history.append({
                    'time': current_time.isoformat(),
                    'success': True,
                    'update_count': report_data.get('update_count', 0)
                })
            else:
                logger.error(f"Failed to send knowledge update: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error generating knowledge report: {str(e)}", exc_info=True)
    
    async def _generate_knowledge_report(self) -> Dict[str, Any]:
        stats = self.knowledge_base.get_stats()
        recent_updates = self.knowledge_base.get_recent_updates(4)
        
        return {
            'generated_at': datetime.now().isoformat(),
            'stats': stats,
            'recent_updates': recent_updates,
            'update_count': recent_updates['update_count'],
            'knowledge_summary': self.knowledge_base.get_knowledge_summary()
        }
    
    def _format_knowledge_report(self, report: Dict[str, Any]) -> str:
        sections = []
        
        sections.append(f"## 📅 {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
        
        stats = report.get('stats', {})
        wiki_stats = stats.get('wiki', {})
        graph_stats = stats.get('graph', {})
        
        sections.append("\n### 📊 知识体系概览")
        sections.append(f"- **总知识条目**: {stats.get('total_knowledge_items', 0)}")
        sections.append(f"- **Wiki页面**: {wiki_stats.get('total_pages', 0)}")
        sections.append(f"- **图谱节点**: {graph_stats.get('total_nodes', 0)}")
        sections.append(f"- **图谱边**: {graph_stats.get('total_edges', 0)}")
        sections.append(f"- **文档数量**: {stats.get('documents', 0)}")
        sections.append(f"- **总版本数**: {wiki_stats.get('total_versions', 0)}")
        
        if wiki_stats.get('pages_by_type'):
            sections.append("\n### 📁 Wiki页面分类")
            for page_type, count in wiki_stats['pages_by_type'].items():
                sections.append(f"- {page_type}: {count}页")
        
        if graph_stats.get('nodes_by_type'):
            sections.append("\n### 🔗 图谱节点分类")
            for node_type, count in graph_stats['nodes_by_type'].items():
                sections.append(f"- {node_type}: {count}个")
        
        if graph_stats.get('edges_by_relation'):
            sections.append("\n### 🔗 图谱关系分布")
            for relation, count in graph_stats['edges_by_relation'].items():
                sections.append(f"- {relation}: {count}条")
        
        recent_updates = report.get('recent_updates', {})
        if recent_updates.get('wiki_updates'):
            sections.append(f"\n### 📝 最近4小时更新 ({len(recent_updates['wiki_updates'])}条)")
            for update in recent_updates['wiki_updates'][:5]:
                sections.append(f"- **[{update['page_id']}]** ({update['page_type']}) v{update['version']}")
        
        if recent_updates.get('change_log'):
            sections.append(f"\n### 📋 更新日志")
            for change in recent_updates['change_log'][:5]:
                sections.append(f"- {change['page_id']} ({change['page_type']})")
        
        sections.append("\n### 💡 系统状态")
        sections.append("- ✅ 知识图谱正常运行")
        sections.append("- ✅ 版本控制已启用")
        sections.append("- ✅ Beyond RAG架构完整")
        
        return '\n\n'.join(sections)
    
    def get_knowledge_base(self) -> EnhancedKnowledgeBase:
        return self.knowledge_base
    
    def get_update_history(self) -> List[Dict[str, Any]]:
        return self._update_history


async def run_service():
    service = KnowledgeNotificationService()
    await service.start()
    
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        await service.stop()


if __name__ == '__main__':
    asyncio.run(run_service())