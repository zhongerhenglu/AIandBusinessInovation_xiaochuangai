from typing import Dict, Any
from brain.agent_base import BaseAgent
from action.risk_manager import RiskManager
from action.position_manager import PositionManager
import logging

logger = logging.getLogger(__name__)


class RiskAgent(BaseAgent):
    def __init__(self):
        super().__init__("RiskAgent")
        self.risk_manager = RiskManager()
        self.position_manager = PositionManager()
    
    async def execute(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if task_type == "risk_check":
            return await self._risk_check(payload)
        elif task_type == "portfolio_risk":
            return await self._portfolio_risk(payload)
        elif task_type == "drawdown_monitor":
            return await self._drawdown_monitor(payload)
        
        return {"error": f"Unknown task type: {task_type}"}
    
    async def _risk_check(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        decision = payload.get("decision", {})
        risk_result = self.risk_manager.check(decision)
        
        return {
            "approved": risk_result.get("approved"),
            "reason": risk_result.get("reason"),
            "max_position": risk_result.get("max_position")
        }
    
    async def _portfolio_risk(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        positions = self.position_manager.get_positions()
        
        return {
            "total_positions": len(positions),
            "positions": positions,
            "risk_summary": {
                "sector_exposure": 0.2,
                "concentration": 0.15,
                "leverage": 1.0
            }
        }
    
    async def _drawdown_monitor(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "current_drawdown": 0.05,
            "max_drawdown": 0.12,
            "threshold": 0.15,
            "status": "safe"
        }