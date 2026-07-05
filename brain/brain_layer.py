from typing import Dict, Any, Optional, List
from .llm_client import LLMClient
from .reasoning_chain import StrategyReasoningChain
import logging

logger = logging.getLogger(__name__)


class ShortTermMemory:
    def __init__(self, max_size: int = 100):
        self.memory = []
        self.max_size = max_size
    
    def store(self, state: Dict[str, Any], decision: Dict[str, Any]):
        entry = {
            "state": state,
            "decision": decision,
            "timestamp": state.get("timestamp")
        }
        self.memory.append(entry)
        if len(self.memory) > self.max_size:
            self.memory.pop(0)
    
    def retrieve(self, state: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
        return self.memory[-top_k:] if self.memory else []


class BrainLayer:
    def __init__(self, policy_registry=None, knowledge_base=None):
        self.policy_registry = policy_registry
        self.knowledge_base = knowledge_base
        self.llm_client = LLMClient()
        self.memory = ShortTermMemory()
        self.reasoning_chain = StrategyReasoningChain(self.llm_client)
    
    def think(self, state: Dict[str, Any]) -> Dict[str, Any]:
        rule_matches = self._match_rules(state)
        knowledge_context = self._retrieve_knowledge(state)
        
        reasoning_input = {
            "features": str(state.get("features", {})),
            "text": state.get("text", ""),
            "rules": str(rule_matches),
            "knowledge_context": str(knowledge_context)
        }
        
        reasoning_results = self.reasoning_chain.run(reasoning_input)
        
        decision = self._parse_decision(reasoning_results)
        decision = self._validate_decision(decision)
        
        self.memory.store(state, decision)
        
        if self.knowledge_base:
            self.knowledge_base.update(
                topic='trading_decisions',
                content=self._generate_decision_summary(decision)
            )
        
        return decision
    
    def _match_rules(self, state: Dict[str, Any]) -> List[str]:
        if not self.policy_registry:
            return []
        
        active_policy = self.policy_registry.get_active_policy()
        if not active_policy:
            return []
        
        matched_rules = []
        for rule in active_policy.get("rules", []):
            if self._evaluate_rule(rule, state):
                matched_rules.append(rule.get("rule_id"))
        
        return matched_rules
    
    def _evaluate_rule(self, rule: Dict[str, Any], state: Dict[str, Any]) -> bool:
        return True
    
    def _retrieve_knowledge(self, state: Dict[str, Any]) -> str:
        if not self.knowledge_base:
            return ""
        
        return self.knowledge_base.query(
            state.get("text", ""),
            context_type='strategy_decision'
        )
    
    def _parse_decision(self, reasoning_results: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "action": "HOLD",
            "confidence": 0.5,
            "reasoning": reasoning_results.get("decision_synthesis", ""),
            "timestamp": reasoning_results.get("timestamp")
        }
    
    def _validate_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        return decision
    
    def _generate_decision_summary(self, decision: Dict[str, Any]) -> str:
        return f"Decision: {decision.get('action')}, Confidence: {decision.get('confidence')}"