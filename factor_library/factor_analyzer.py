import pandas as pd
import numpy as np
from typing import Dict, Any
from .factor_library import FactorLibrary
import logging

logger = logging.getLogger(__name__)


class FactorAnalyzer:
    def __init__(self):
        self.factor_library = FactorLibrary()
    
    def calculate_ic(self, factor_values: pd.Series, forward_returns: pd.Series, 
                     period: int = 20) -> pd.Series:
        ic_values = []
        valid_factor = factor_values.dropna()
        valid_returns = forward_returns.dropna()
        
        if len(valid_factor) < period or len(valid_returns) < period:
            return pd.Series([])
        
        aligned_factor, aligned_returns = valid_factor.align(valid_returns, join='inner')
        
        for i in range(len(aligned_factor) - period):
            factor_window = aligned_factor.iloc[i:i+period]
            return_window = aligned_returns.iloc[i:i+period]
            
            if len(factor_window.dropna()) >= period // 2 and len(return_window.dropna()) >= period // 2:
                corr = factor_window.corr(return_window)
                ic_values.append(corr if not np.isnan(corr) else 0)
            else:
                ic_values.append(0)
        
        return pd.Series(ic_values)
    
    def calculate_ir(self, ic_values: pd.Series) -> float:
        if ic_values.empty or ic_values.std() == 0:
            return 0.0
        return float(ic_values.mean() / ic_values.std())
    
    def analyze_factor(self, factor_id: str, data: pd.DataFrame) -> Dict[str, Any]:
        factor_values = self.factor_library.calculate_factor(factor_id, data)
        forward_returns = self._calculate_forward_returns(data)
        
        ic_series = self.calculate_ic(factor_values, forward_returns)
        ir = self.calculate_ir(ic_series)
        
        return {
            'factor_id': factor_id,
            'ic_mean': float(ic_series.mean()),
            'ic_std': float(ic_series.std()),
            'ir': ir,
            'ic_history': ic_series,
            'factor_values': factor_values
        }
    
    def analyze_all_factors(self, data: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        results = {}
        for category, factor_ids in self.factor_library.factor_categories.items():
            for factor_id in factor_ids:
                try:
                    results[factor_id] = self.analyze_factor(factor_id, data)
                except Exception as e:
                    logger.warning(f"Failed to analyze factor {factor_id}: {e}")
        return results
    
    def _calculate_forward_returns(self, data: pd.DataFrame) -> pd.Series:
        return data['close'].pct_change().shift(-1)