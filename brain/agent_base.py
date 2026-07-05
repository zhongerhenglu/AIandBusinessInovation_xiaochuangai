import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.status = "idle"
        self.last_execution_time: Optional[datetime] = None
        self.execution_count = 0
        self.success_count = 0
    
    @abstractmethod
    async def execute(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    async def run(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.status = "running"
        self.last_execution_time = datetime.now()
        self.execution_count += 1
        
        logger.info(f"Agent {self.agent_name} starting task: {task_type}")
        
        try:
            result = await self.execute(task_type, payload)
            self.success_count += 1
            self.status = "idle"
            logger.info(f"Agent {self.agent_name} completed task: {task_type}")
            return {"status": "success", "result": result}
        except Exception as e:
            self.status = "error"
            logger.error(f"Agent {self.agent_name} failed task {task_type}: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_metrics(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "status": self.status,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "success_rate": self.success_count / max(self.execution_count, 1),
            "last_execution_time": self.last_execution_time.isoformat() if self.last_execution_time else None
        }