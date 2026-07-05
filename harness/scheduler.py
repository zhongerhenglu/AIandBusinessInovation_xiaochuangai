import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Task:
    task_id: str
    agent_name: str
    task_type: str
    priority: int = 0
    payload: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"
    result: Optional[Any] = None


class CentralScheduler:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.agent_registry: Dict[str, Callable] = {}
        self.running_tasks: List[str] = []
        self.completed_tasks: List[str] = []
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
    
    def register_agent(self, agent_name: str, agent_handler: Callable):
        self.agent_registry[agent_name] = agent_handler
        logger.info(f"Agent registered: {agent_name}")
    
    def submit_task(self, task: Task):
        self.tasks[task.task_id] = task
        self.task_queue.put_nowait((-task.priority, task.task_id))
        logger.info(f"Task submitted: {task.task_id} ({task.task_type})")
    
    async def process_tasks(self):
        while True:
            try:
                priority, task_id = await asyncio.wait_for(
                    self.task_queue.get(), timeout=60
                )
                task = self.tasks.get(task_id)
                if not task:
                    continue
                
                await self._execute_task(task)
                self.task_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing tasks: {e}")
    
    async def _execute_task(self, task: Task):
        if task.status != "pending":
            return
        
        if task.dependencies:
            for dep in task.dependencies:
                if dep not in self.completed_tasks:
                    logger.info(f"Task {task.task_id} waiting for dependency: {dep}")
                    await self._wait_for_dependency(dep)
        
        task.status = "running"
        self.running_tasks.append(task.task_id)
        logger.info(f"Starting task: {task.task_id}")
        
        try:
            agent_handler = self.agent_registry.get(task.agent_name)
            if not agent_handler:
                raise ValueError(f"Agent not found: {task.agent_name}")
            
            result = await agent_handler(task.payload)
            task.result = result
            task.status = "completed"
            self.completed_tasks.append(task.task_id)
            logger.info(f"Task completed: {task.task_id}")
            
            await self._trigger_dependent_tasks(task.task_id)
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            logger.error(f"Task failed: {task.task_id} - {e}")
        finally:
            self.running_tasks.remove(task.task_id)
    
    async def _wait_for_dependency(self, dep_task_id: str):
        while dep_task_id not in self.completed_tasks:
            await asyncio.sleep(1)
    
    async def _trigger_dependent_tasks(self, completed_task_id: str):
        for task_id, task in self.tasks.items():
            if completed_task_id in task.dependencies and task.status == "pending":
                self.task_queue.put_nowait((-task.priority, task_id))
    
    def get_task_status(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        return list(self.tasks.values())
    
    async def shutdown(self):
        logger.info("Shutting down scheduler...")
        self.task_queue = asyncio.PriorityQueue()