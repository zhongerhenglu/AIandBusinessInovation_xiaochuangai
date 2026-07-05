import pandas as pd
import numpy as np
from typing import Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)


class FactorLibrary:
    def __init__(self):
        self.factors: Dict[str, Callable] = {}
        self.factor_categories = {
            'momentum': ['roc_5', 'roc_20', 'roc_60', 'ma_cross'],
            'value': ['pe_ratio', 'pb_ratio', 'ev_ebitda', 'dividend_yield'],
            'quality': ['roe', 'roa', 'profit_margin', 'debt_ratio'],
            'volatility': ['std_20', 'atr', 'beta', 'downside_deviation'],
            'volume': ['volume_ratio', 'vwap', 'money_flow']
        }
        self.threshold = 0.7
        
        self._register_default_factors()
    
    def _register_default_factors(self):
        self.factors['roc_5'] = self._roc_5
        self.factors['roc_20'] = self._roc_20
        self.factors['roc_60'] = self._roc_60
        self.factors['ma_cross'] = self._ma_cross
        self.factors['pe_ratio'] = self._pe_ratio
        self.factors['pb_ratio'] = self._pb_ratio
        self.factors['ev_ebitda'] = self._ev_ebitda
        self.factors['dividend_yield'] = self._dividend_yield
        self.factors['roe'] = self._roe
        self.factors['roa'] = self._roa
        self.factors['profit_margin'] = self._profit_margin
        self.factors['debt_ratio'] = self._debt_ratio
        self.factors['std_20'] = self._std_20
        self.factors['atr'] = self._atr
        self.factors['beta'] = self._beta
        self.factors['downside_deviation'] = self._downside_deviation
        self.factors['volume_ratio'] = self._volume_ratio
        self.factors['vwap'] = self._vwap
        self.factors['money_flow'] = self._money_flow
    
    def _roc_5(self, data: pd.DataFrame) -> pd.Series:
        return data['close'].pct_change(5)
    
    def _roc_20(self, data: pd.DataFrame) -> pd.Series:
        return data['close'].pct_change(20)
    
    def _roc_60(self, data: pd.DataFrame) -> pd.Series:
        return data['close'].pct_change(60)
    
    def _pe_ratio(self, data: pd.DataFrame) -> pd.Series:
        return data.get('close', data.iloc[:, 3]) / data.get('earnings', 1)
    
    def _std_20(self, data: pd.DataFrame) -> pd.Series:
        return data['close'].pct_change().rolling(20).std()
    
    def _atr(self, data: pd.DataFrame) -> pd.Series:
        high_low = data['high'] - data['low']
        high_close = (data['high'] - data['close'].shift()).abs()
        low_close = (data['low'] - data['close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(14).mean()
    
    def _ma_cross(self, data: pd.DataFrame) -> pd.Series:
        ma5 = data['close'].rolling(5).mean()
        ma20 = data['close'].rolling(20).mean()
        return ma5 - ma20
    
    def _pb_ratio(self, data: pd.DataFrame) -> pd.Series:
        return data.get('close', data.iloc[:, 3]) / data.get('book_value', 1)
    
    def _ev_ebitda(self, data: pd.DataFrame) -> pd.Series:
        return data.get('close', data.iloc[:, 3]) * data.get('shares', 1) / data.get('ebitda', 1)
    
    def _dividend_yield(self, data: pd.DataFrame) -> pd.Series:
        return data.get('dividend', 0) / data.get('close', data.iloc[:, 3])
    
    def _roe(self, data: pd.DataFrame) -> pd.Series:
        return data.get('net_income', 0) / data.get('equity', 1)
    
    def _roa(self, data: pd.DataFrame) -> pd.Series:
        return data.get('net_income', 0) / data.get('assets', 1)
    
    def _profit_margin(self, data: pd.DataFrame) -> pd.Series:
        return data.get('net_income', 0) / data.get('revenue', 1)
    
    def _debt_ratio(self, data: pd.DataFrame) -> pd.Series:
        return data.get('debt', 0) / data.get('assets', 1)
    
    def _beta(self, data: pd.DataFrame) -> pd.Series:
        returns = data['close'].pct_change().dropna()
        market_returns = returns.rolling(60).mean()
        return returns.rolling(60).cov(market_returns) / market_returns.rolling(60).var()
    
    def _downside_deviation(self, data: pd.DataFrame) -> pd.Series:
        returns = data['close'].pct_change()
        downside = returns[returns < 0]
        return downside.rolling(20).std()
    
    def _volume_ratio(self, data: pd.DataFrame) -> pd.Series:
        return data['volume'] / data['volume'].rolling(20).mean()
    
    def _vwap(self, data: pd.DataFrame) -> pd.Series:
        return (data['close'] * data['volume']).rolling(20).sum() / data['volume'].rolling(20).sum()
    
    def _money_flow(self, data: pd.DataFrame) -> pd.Series:
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        money_flow = typical_price * data['volume']
        positive_flow = money_flow[data['close'] > data['close'].shift()]
        negative_flow = money_flow[data['close'] < data['close'].shift()]
        mfi = (positive_flow.rolling(14).sum() / negative_flow.rolling(14).sum()) * 100
        return mfi
    
    def calculate_factor(self, factor_id: str, data: pd.DataFrame) -> pd.Series:
        if factor_id not in self.factors:
            raise ValueError(f"Factor {factor_id} not found")
        return self.factors[factor_id](data)
    
    def calculate_all_factors(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        results = {}
        for category, factor_ids in self.factor_categories.items():
            for factor_id in factor_ids:
                try:
                    results[factor_id] = self.calculate_factor(factor_id, data)
                except Exception as e:
                    logger.warning(f"Failed to calculate factor {factor_id}: {e}")
        return results
    
    def deduplicate_factors(self, factors_data: Dict[str, pd.Series]) -> Dict[str, pd.Series]:
        unique_factors = {}
        processed_pairs = set()
        
        valid_factors = {k: v for k, v in factors_data.items() if isinstance(v, pd.Series) and len(v.dropna()) > 10}
        factor_ids = list(valid_factors.keys())
        
        for i, fid1 in enumerate(factor_ids):
            is_unique = True
            for j, fid2 in enumerate(factor_ids):
                if i != j and (i, j) not in processed_pairs:
                    corr = self.get_factor_correlation(valid_factors[fid1], valid_factors[fid2])
                    processed_pairs.add((i, j))
                    processed_pairs.add((j, i))
                    if abs(corr) >= self.threshold:
                        is_unique = False
                        break
            if is_unique:
                unique_factors[fid1] = valid_factors[fid1]
        
        return unique_factors
    
    def get_factor_correlation(self, factor1: pd.Series, factor2: pd.Series) -> float:
        return float(factor1.corr(factor2))
    
    def add_factor(self, factor_id: str, category: str, calculation_func: Callable):
        self.factors[factor_id] = calculation_func
        if category not in self.factor_categories:
            self.factor_categories[category] = []
        self.factor_categories[category].append(factor_id)