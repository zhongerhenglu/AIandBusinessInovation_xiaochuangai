from typing import Dict, Any
from brain.agent_base import BaseAgent
from perception.perception_layer import PerceptionLayer
from brain.brain_layer import BrainLayer
from action.action_layer import ActionLayer
import logging

logger = logging.getLogger(__name__)


class AlphaAgent(BaseAgent):
    def __init__(self):
        super().__init__("AlphaAgent")
        self.perception = PerceptionLayer()
        self.brain = BrainLayer()
        self.action = ActionLayer()
    
    async def execute(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if task_type == "trade_decision":
            return await self._make_trade_decision(payload)
        elif task_type == "market_analysis":
            return await self._perform_market_analysis(payload)
        elif task_type == "strategy_review":
            return await self._review_strategy(payload)
        
        return {"error": f"Unknown task type: {task_type}"}
    
    async def _make_trade_decision(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        timestamp = payload.get("timestamp")
        
        state = self.perception.collect_state(timestamp)
        
        decision = self.brain.think(state)
        
        execution_result = self.action.execute(decision)
        
        return {
            "state": state,
            "decision": decision,
            "execution": execution_result
        }
    
    async def _perform_market_analysis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        timestamp = payload.get("timestamp")
        state = self.perception.collect_state(timestamp)
        
        return {
            "timestamp": timestamp,
            "features": state.get("features"),
            "text_summary": state.get("text")
        }
    
    async def _review_strategy(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "strategy_id": payload.get("strategy_id"),
            "review_status": "completed",
            "recommendations": ["Adjust RSI threshold", "Add volume filter"]
        }