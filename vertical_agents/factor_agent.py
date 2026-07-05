from typing import Dict, Any
from brain.agent_base import BaseAgent
from factor_library.factor_library import FactorLibrary
from factor_library.factor_analyzer import FactorAnalyzer
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class FactorAgent(BaseAgent):
    def __init__(self):
        super().__init__("FactorAgent")
        self.factor_library = FactorLibrary()
        self.factor_analyzer = FactorAnalyzer()
    
    async def execute(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if task_type == "calculate_factor":
            return await self._calculate_factor(payload)
        elif task_type == "analyze_factors":
            return await self._analyze_factors(payload)
        elif task_type == "deduplicate_factors":
            return await self._deduplicate_factors(payload)
        elif task_type == "research_factors":
            return await self._research_factors(payload)
        
        return {"error": f"Unknown task type: {task_type}"}
    
    async def _calculate_factor(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        factor_id = payload.get("factor_id")
        data = self._create_mock_data()
        
        factor_values = self.factor_library.calculate_factor(factor_id, data)
        
        return {
            "factor_id": factor_id,
            "values": factor_values.tolist()[:10],
            "category": self._get_factor_category(factor_id)
        }
    
    async def _analyze_factors(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = self._create_mock_data()
        analysis_results = self.factor_analyzer.analyze_all_factors(data)
        
        summary = {}
        for factor_id, result in analysis_results.items():
            summary[factor_id] = {
                "ic_mean": result.get("ic_mean"),
                "ir": result.get("ir")
            }
        
        return {"analysis_summary": summary}
    
    async def _deduplicate_factors(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = self._create_mock_data()
        all_factors = self.factor_library.calculate_all_factors(data)
        unique_factors = self.factor_library.deduplicate_factors(all_factors)
        
        return {
            "total_factors": len(all_factors),
            "unique_factors": len(unique_factors),
            "unique_factor_ids": list(unique_factors.keys())
        }
    
    async def _research_factors(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = self._create_mock_data()
        
        all_factors = self.factor_library.calculate_all_factors(data)
        unique_factors = self.factor_library.deduplicate_factors(all_factors)
        
        results = {}
        for factor_id, values in unique_factors.items():
            try:
                analysis = self.factor_analyzer.analyze_factor(factor_id, data)
                results[factor_id] = {
                    "ic_mean": analysis.get("ic_mean"),
                    "ir": analysis.get("ir")
                }
            except Exception as e:
                logger.warning(f"Failed to analyze factor {factor_id}: {e}")
        
        return {
            "research_summary": results,
            "high_quality_factors": [k for k, v in results.items() if v.get("ir", 0) > 0.5]
        }
    
    def _create_mock_data(self) -> pd.DataFrame:
        dates = pd.date_range(start='2023-01-01', periods=252, freq='D')
        data = pd.DataFrame({
            'date': dates,
            'open': np.random.uniform(100, 200, 252),
            'high': np.random.uniform(100, 200, 252),
            'low': np.random.uniform(100, 200, 252),
            'close': np.random.uniform(100, 200, 252),
            'volume': np.random.randint(1000000, 10000000, 252)
        })
        return data
    
    def _get_factor_category(self, factor_id: str) -> str:
        for category, factors in self.factor_library.factor_categories.items():
            if factor_id in factors:
                return category
        return "unknown"


import numpy as np