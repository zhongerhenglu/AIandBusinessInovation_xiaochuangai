from typing import Dict, Any, List
from .llm_client import LLMClient
import logging

logger = logging.getLogger(__name__)


class ReasoningChain:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.steps = []
    
    def add_step(self, step_name: str, prompt_template: str):
        self.steps.append({"name": step_name, "template": prompt_template})
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        
        for step in self.steps:
            prompt = step["template"].format(**state)
            response = self.llm_client.chat(prompt)
            results[step["name"]] = response
            state[step["name"]] = response
            logger.info(f"Completed reasoning step: {step['name']}")
        
        return results


class StrategyReasoningChain(ReasoningChain):
    def __init__(self, llm_client: LLMClient):
        super().__init__(llm_client)
        self._setup_default_steps()
    
    def _setup_default_steps(self):
        self.add_step(
            "market_analysis",
            """Analyze the current market state:
            Features: {features}
            Text: {text}
            
            Provide a concise market analysis including:
            1. Key trends
            2. Risk assessment
            3. Opportunities"""
        )
        
        self.add_step(
            "rule_matching",
            """Based on the market analysis:
            {market_analysis}
            
            Current rules: {rules}
            
            Which rules are triggered? Explain your reasoning."""
        )
        
        self.add_step(
            "decision_synthesis",
            """Market analysis: {market_analysis}
            Rule matches: {rule_matching}
            Knowledge context: {knowledge_context}
            
            Synthesize a trading decision with:
            - Action (BUY/SELL/HOLD)
            - Confidence level
            - Risk assessment
            - Rationale"""
        )