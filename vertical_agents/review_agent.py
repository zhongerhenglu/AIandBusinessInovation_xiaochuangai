from typing import Dict, Any
from brain.agent_base import BaseAgent
from brain.llm_client import LLMClient
import logging

logger = logging.getLogger(__name__)


class ReviewAgent(BaseAgent):
    def __init__(self):
        super().__init__("ReviewAgent")
        self.llm_client = LLMClient()
    
    async def execute(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if task_type == "generate_replay_data":
            return await self._generate_replay_data(payload)
        elif task_type == "build_codex_prompt":
            return await self._build_codex_prompt(payload)
        elif task_type == "optimize_strategy":
            return await self._optimize_strategy(payload)
        
        return {"error": f"Unknown task type: {task_type}"}
    
    async def _generate_replay_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        strategy_id = payload.get("strategy_id")
        
        return {
            "strategy_id": strategy_id,
            "trades": [],
            "pnl_curve": [0.0, 0.01, 0.005, 0.02],
            "statistics": {
                "win_rate": 0.62,
                "sharpe_ratio": 1.85,
                "max_drawdown": 0.12
            }
        }
    
    async def _build_codex_prompt(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        comments = payload.get("comments", [])
        strategy_id = payload.get("strategy_id")
        
        prompt = f"""
        # Strategy Optimization Task
        Strategy ID: {strategy_id}
        
        Review Comments:
        {comments}
        
        Task: Analyze the comments and optimize the strategy rules.
        Output: Updated Python policy code with clear explanations.
        """
        
        return {"prompt": prompt}
    
    async def _optimize_strategy(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        prompt = payload.get("prompt")
        optimization_result = self.llm_client.chat(prompt)
        
        return {
            "optimization_result": optimization_result,
            "ai_plain_language_comment": "Strategy has been optimized based on review comments."
        }