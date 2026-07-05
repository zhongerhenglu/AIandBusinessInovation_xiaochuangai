import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DataSimulator:
    def __init__(self):
        self.base_price = 3000.0
        self.seed = 42
        np.random.seed(self.seed)
    
    def generate_csi300_prices(self, start_date: str = '2024-01-01', 
                               end_date: str = '2026-06-30',
                               scenario_params: Dict[str, Any] = None) -> pd.DataFrame:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        dates = []
        current = start
        while current <= end:
            if current.weekday() < 5:
                dates.append(current)
            current += timedelta(days=1)
        
        n_days = len(dates)
        daily_returns = np.random.normal(0.0002, 0.012, n_days)
        
        period_adjustments = []
        for i, date in enumerate(dates):
            year = date.year
            month = date.month
            
            if year == 2024 and month >= 7:
                period_adjustments.append(0.0005)
            elif year == 2025 and month <= 6:
                period_adjustments.append(-0.0008)
            elif year == 2025 and month >= 7:
                period_adjustments.append(0.0003)
            elif year == 2026 and month <= 6:
                period_adjustments.append(0.0006)
            elif year == 2026 and month >= 7:
                period_adjustments.append(self._get_scenario_adjustment(date, scenario_params))
            else:
                period_adjustments.append(0)
        
        adjusted_returns = daily_returns + np.array(period_adjustments)
        
        prices = [self.base_price]
        for ret in adjusted_returns:
            prices.append(prices[-1] * (1 + ret))
        
        prices = prices[:-1]
        
        highs = prices * (1 + np.random.uniform(0, 0.02, n_days))
        lows = prices * (1 - np.random.uniform(0, 0.02, n_days))
        opens = prices * (1 + np.random.uniform(-0.01, 0.01, n_days))
        volumes = np.random.randint(100000000, 500000000, n_days)
        
        df = pd.DataFrame({
            'date': [d.strftime('%Y-%m-%d') for d in dates],
            'open': opens,
            'high': highs,
            'low': lows,
            'close': prices,
            'volume': volumes
        })
        
        logger.info(f"Generated {len(df)} trading days of CSI 300 data")
        return df
    
    def generate_factor_data(self, prices_df: pd.DataFrame, 
                            factor_name: str = 'momentum') -> pd.DataFrame:
        dates = prices_df['date']
        close = prices_df['close']
        
        if factor_name == 'momentum':
            factor_values = close.pct_change(20)
        elif factor_name == 'value':
            factor_values = 1 / (close.pct_change(60) + 1.1)
        elif factor_name == 'quality':
            factor_values = close.rolling(60).mean() / close.rolling(60).std()
        elif factor_name == 'volatility':
            factor_values = close.pct_change().rolling(20).std()
        elif factor_name == 'volume':
            factor_values = prices_df['volume'] / prices_df['volume'].rolling(20).mean()
        else:
            factor_values = close.pct_change(20)
        
        df = pd.DataFrame({
            'date': dates,
            factor_name: factor_values
        })
        
        return df.dropna()
    
    def generate_trading_signals(self, prices_df: pd.DataFrame, 
                                 strategy: str = 'moving_average') -> pd.DataFrame:
        close = prices_df['close']
        
        if strategy == 'moving_average':
            ma5 = close.rolling(5).mean()
            ma20 = close.rolling(20).mean()
            signal = np.where(ma5 > ma20, 1, -1)
        elif strategy == 'momentum':
            momentum = close.pct_change(20)
            signal = np.where(momentum > 0, 1, -1)
        elif strategy == 'mean_reversion':
            z_score = (close - close.rolling(20).mean()) / close.rolling(20).std()
            signal = np.where(z_score > 1, -1, np.where(z_score < -1, 1, 0))
        else:
            signal = np.where(close.pct_change(5) > 0, 1, -1)
        
        df = pd.DataFrame({
            'date': prices_df['date'],
            'signal': signal
        })
        
        return df
    
    def generate_multi_factor_data(self, prices_df: pd.DataFrame) -> pd.DataFrame:
        df = prices_df[['date']].copy()
        
        df['momentum_5'] = prices_df['close'].pct_change(5)
        df['momentum_20'] = prices_df['close'].pct_change(20)
        df['momentum_60'] = prices_df['close'].pct_change(60)
        df['volatility_20'] = prices_df['close'].pct_change().rolling(20).std()
        df['volume_ratio'] = prices_df['volume'] / prices_df['volume'].rolling(20).mean()
        df['ma5_ma20_diff'] = prices_df['close'].rolling(5).mean() - prices_df['close'].rolling(20).mean()
        df['rsi_14'] = self._calculate_rsi(prices_df['close'], 14)
        
        return df.dropna()
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window).mean()
        avg_loss = loss.rolling(window).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _get_scenario_adjustment(self, date: datetime, scenario_params: Dict[str, Any] = None) -> float:
        if scenario_params is None:
            scenario_params = {}
        
        base_adjustment = 0.0008
        
        japan_korea_crash = scenario_params.get('japan_korea_crash', False)
        china_rescue_amount = scenario_params.get('china_rescue_amount', 0)
        month = date.month
        
        if japan_korea_crash:
            if month <= 8:
                base_adjustment -= 0.0015
            elif month <= 10:
                base_adjustment += 0.0010
        
        if china_rescue_amount > 0:
            rescue_boost = min(china_rescue_amount * 0.0005, 0.002)
            if month >= 8:
                base_adjustment += rescue_boost
            elif month >= 10:
                base_adjustment += rescue_boost * 1.5
        
        return base_adjustment
    
    def generate_period_comparison_data(self, scenario_params: Dict[str, Any] = None) -> Dict[str, pd.DataFrame]:
        periods = {
            '2024下半年': ('2024-07-01', '2024-12-31'),
            '2025上半年': ('2025-01-01', '2025-06-30'),
            '2025下半年': ('2025-07-01', '2025-12-31'),
            '2026上半年': ('2026-01-01', '2026-06-30'),
            '2026下半年': ('2026-07-01', '2026-12-31')
        }
        
        end_date = '2026-12-31' if '2026下半年' in periods else '2026-06-30'
        all_data = self.generate_csi300_prices('2024-07-01', end_date, scenario_params)
        result = {}
        
        for period_name, (start, end) in periods.items():
            mask = (all_data['date'] >= start) & (all_data['date'] <= end)
            result[period_name] = all_data[mask]
        
        result['all'] = all_data
        return result