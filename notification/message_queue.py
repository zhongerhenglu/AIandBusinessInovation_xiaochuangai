import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Message:
    message_id: str
    title: str
    content: str
    priority: int = 0
    channel: str = 'default'
    status: str = 'pending'
    created_at: datetime = field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None
    error: Optional[str] = None


class MessageQueue:
    def __init__(self, max_size: int = 1000):
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=max_size)
        self._messages: Dict[str, Message] = {}
        self._running: bool = False
        self._worker_task: Optional[asyncio.Task] = None
        self._sender = None
        self._processing_lock = asyncio.Lock()
    
    def set_sender(self, sender):
        self._sender = sender
        logger.info("Message sender configured")
    
    def enqueue(self, message: Message):
        if self._queue.full():
            logger.warning("Message queue is full")
            return False
        
        self._messages[message.message_id] = message
        self._queue.put_nowait((-message.priority, message.message_id))
        logger.info(f"Message enqueued: {message.message_id}")
        return True
    
    def create_and_enqueue(self, title: str, content: str, priority: int = 0, 
                           channel: str = 'default') -> str:
        message_id = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(title) % 10000}"
        message = Message(
            message_id=message_id,
            title=title,
            content=content,
            priority=priority,
            channel=channel
        )
        self.enqueue(message)
        return message_id
    
    async def process_messages(self):
        self._running = True
        logger.info("Message queue processor started")
        
        while self._running:
            try:
                priority, message_id = await self._queue.get()
                message = self._messages.get(message_id)
                
                if not message:
                    continue
                
                await self._send_message(message)
                self._queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
        
        logger.info("Message queue processor stopped")
    
    async def _send_message(self, message: Message):
        if not self._sender:
            logger.error("No sender configured")
            message.status = 'failed'
            message.error = 'No sender configured'
            return
        
        try:
            result = await asyncio.to_thread(
                self._sender.send_markdown,
                message.title,
                message.content,
                message.channel
            )
            
            if result.get('success'):
                message.status = 'sent'
                message.sent_at = datetime.now()
                logger.info(f"Message sent: {message.message_id}")
            else:
                message.status = 'failed'
                message.error = result.get('error', 'Unknown error')
                logger.error(f"Failed to send message: {message.message_id} - {message.error}")
        
        except Exception as e:
            message.status = 'failed'
            message.error = str(e)
            logger.error(f"Error sending message {message.message_id}: {str(e)}")
    
    async def start(self):
        if self._running:
            logger.warning("Message queue is already running")
            return
        
        self._worker_task = asyncio.create_task(self.process_messages())
    
    async def stop(self):
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
    
    def get_message_status(self, message_id: str) -> Optional[Message]:
        return self._messages.get(message_id)
    
    def get_pending_messages(self) -> List[Message]:
        return [m for m in self._messages.values() if m.status == 'pending']
    
    def get_queue_size(self) -> int:
        return self._queue.qsize()
    
    def is_running(self) -> bool:
        return self._running