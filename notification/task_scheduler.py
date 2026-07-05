import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ScheduledTask:
    task_id: str
    name: str
    callback: Callable
    schedule_type: str
    hour: int = 8
    minute: int = 30
    weekday: Optional[int] = None
    kwargs: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


class NotificationScheduler:
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running: bool = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._task: Optional[asyncio.Task] = None
    
    def add_daily_task(self, task_id: str, name: str, callback: Callable, 
                       hour: int = 8, minute: int = 30, **kwargs):
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            callback=callback,
            schedule_type='daily',
            hour=hour,
            minute=minute,
            kwargs=kwargs
        )
        self.tasks[task_id] = task
        logger.info(f"Added daily task: {task_id} at {hour:02d}:{minute:02d}")
    
    def add_weekly_task(self, task_id: str, name: str, callback: Callable,
                        weekday: int, hour: int = 8, minute: int = 30, **kwargs):
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            callback=callback,
            schedule_type='weekly',
            hour=hour,
            minute=minute,
            weekday=weekday,
            kwargs=kwargs
        )
        self.tasks[task_id] = task
        logger.info(f"Added weekly task: {task_id} at weekday {weekday}, {hour:02d}:{minute:02d}")
    
    def remove_task(self, task_id: str):
        if task_id in self.tasks:
            del self.tasks[task_id]
            logger.info(f"Removed task: {task_id}")
    
    def enable_task(self, task_id: str):
        if task_id in self.tasks:
            self.tasks[task_id].enabled = True
            logger.info(f"Enabled task: {task_id}")
    
    def disable_task(self, task_id: str):
        if task_id in self.tasks:
            self.tasks[task_id].enabled = False
            logger.info(f"Disabled task: {task_id}")
    
    def get_next_run_time(self, task: ScheduledTask) -> datetime:
        now = datetime.now()
        target_time = datetime.combine(now.date(), time(task.hour, task.minute))
        
        if task.schedule_type == 'daily':
            if target_time > now:
                return target_time
            return target_time + timedelta(days=1)
        
        elif task.schedule_type == 'weekly':
            if task.weekday is None:
                return target_time
            
            days_ahead = task.weekday - now.weekday()
            if days_ahead < 0:
                days_ahead += 7
            
            target_date = now + timedelta(days=days_ahead)
            target_time = datetime.combine(target_date, time(task.hour, task.minute))
            
            if target_time <= now:
                target_time += timedelta(weeks=1)
            
            return target_time
        
        return target_time + timedelta(days=1)
    
    async def start(self):
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self._loop = asyncio.get_event_loop()
        self._task = self._loop.create_task(self._run_loop())
        logger.info("Notification scheduler started")
    
    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Notification scheduler stopped")
    
    async def _run_loop(self):
        while self.running:
            now = datetime.now()
            
            for task_id, task in self.tasks.items():
                if not task.enabled:
                    continue
                
                if task.next_run is None:
                    task.next_run = self.get_next_run_time(task)
                
                if now >= task.next_run:
                    await self._execute_task(task)
                    task.next_run = self.get_next_run_time(task)
            
            await asyncio.sleep(30)
    
    async def _execute_task(self, task: ScheduledTask):
        logger.info(f"Executing scheduled task: {task.task_id}")
        
        try:
            if asyncio.iscoroutinefunction(task.callback):
                await task.callback(**task.kwargs)
            else:
                task.callback(**task.kwargs)
            
            task.last_run = datetime.now()
            logger.info(f"Task completed successfully: {task.task_id}")
        
        except Exception as e:
            logger.error(f"Failed to execute task {task.task_id}: {str(e)}", exc_info=True)
    
    def get_task_status(self, task_id: str) -> Optional[ScheduledTask]:
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> Dict[str, ScheduledTask]:
        return self.tasks