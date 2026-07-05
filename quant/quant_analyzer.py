import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
import logging
import os
from datetime import datetime, timedelta
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

logger = logging.getLogger(__name__)


class QuantAnalyzer:
    def __init__(self):
        self.csi300_data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            '..', '沪深300近十年成分'
        )
        self.component_data: Dict[str, pd.DataFrame] = {}
        self.load_csi300_components()
    
    def load_csi300_components(self):
        if not os.path.exists(self.csi300_data_path):
            logger.warning(f"CSI 300 data path not found: {self.csi300_data_path}")
            return
        
        files = os.listdir(self.csi300_data_path)
        xlsx_files = [f for f in files if f.endswith('.xlsx') and '000300.SH' in f]
        
        for file in xlsx_files:
            try:
                date_str = file.split('-')[-1].replace('.xlsx', '')
                df = pd.read_excel(os.path.join(self.csi300_data_path, file))
                self.component_data[date_str] = df
                logger.info(f"Loaded CSI 300 components for {date_str}: {len(df)} stocks")
            except Exception as e:
                logger.warning(f"Failed to load {file}: {e}")
    
    def get_component_data(self, date_str: str) -> pd.DataFrame:
        return self.component_data.get(date_str, pd.DataFrame())
    
    def get_available_dates(self) -> List[str]:
        return sorted(self.component_data.keys())
    
    def calculate_period_returns(self, prices_df: pd.DataFrame, 
                                  start_date: str, end_date: str) -> Dict[str, Any]:
        mask = (prices_df['date'] >= start_date) & (prices_df['date'] <= end_date)
        period_data = prices_df[mask]
        
        if period_data.empty:
            return {'error': 'No data for the specified period'}
        
        start_price = period_data['close'].iloc[0]
        end_price = period_data['close'].iloc[-1]
        total_return = (end_price - start_price) / start_price
        
        daily_returns = period_data['close'].pct_change().dropna()
        sharpe_ratio = self._calculate_sharpe_ratio(daily_returns)
        max_drawdown = self._calculate_max_drawdown(period_data['close'])
        volatility = daily_returns.std() * np.sqrt(252)
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'start_price': float(start_price),
            'end_price': float(end_price),
            'total_return': float(total_return),
            'annualized_return': float((1 + total_return) ** (252 / len(daily_returns)) - 1),
            'sharpe_ratio': float(sharpe_ratio),
            'max_drawdown': float(max_drawdown),
            'volatility': float(volatility),
            'period_length': len(period_data),
            'avg_daily_return': float(daily_returns.mean()),
            'std_daily_return': float(daily_returns.std())
        }
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        if returns.empty or returns.std() == 0:
            return 0.0
        excess_returns = returns - risk_free_rate / 252
        return float(excess_returns.mean() / excess_returns.std() * np.sqrt(252))
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        if prices.empty:
            return 0.0
        cummax = prices.cummax()
        drawdown = (prices - cummax) / cummax
        return float(drawdown.min())
    
    def analyze_periods(self, prices_df: pd.DataFrame, periods: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        results = []
        for start_date, end_date in periods:
            period_result = self.calculate_period_returns(prices_df, start_date, end_date)
            period_result['period_label'] = f"{start_date}~{end_date}"
            results.append(period_result)
        return results
    
    def analyze_csi300_composition_trend(self, start_year: int = 2016, end_year: int = 2025) -> Dict[str, Any]:
        results = {
            'yearly_counts': [],
            'sector_distribution': [],
            'top_weights': [],
            'turnover_analysis': {}
        }
        
        code_col = '代码'
        name_col = '简称'
        weight_col = '权重'
        industry_col = '中信一级行业'
        
        for year in range(start_year, end_year + 1):
            date_str = f"{year}1231"
            if date_str not in self.component_data:
                continue
            
            df = self.component_data[date_str]
            results['yearly_counts'].append({
                'year': year,
                'stock_count': len(df),
                'total_weight': df[weight_col].sum() if weight_col in df.columns else 0
            })
            
            if industry_col in df.columns and weight_col in df.columns:
                sector_dist = df.groupby(industry_col)[weight_col].sum().sort_values(ascending=False)
                results['sector_distribution'].append({
                    'year': year,
                    'sectors': sector_dist.head(10).to_dict()
                })
            
            if weight_col in df.columns:
                top_stocks = df.sort_values(weight_col, ascending=False).head(10)
                top_list = []
                for _, row in top_stocks.iterrows():
                    top_list.append({
                        'code': row[code_col] if code_col in df.columns else '',
                        'name': row[name_col] if name_col in df.columns else '',
                        'weight': row[weight_col] if weight_col in df.columns else 0
                    })
                results['top_weights'].append({
                    'year': year,
                    'top_stocks': top_list
                })
        
        for i in range(len(results['yearly_counts']) - 1):
            year1 = results['yearly_counts'][i]['year']
            year2 = results['yearly_counts'][i + 1]['year']
            
            df1 = self.component_data.get(f"{year1}1231", pd.DataFrame())
            df2 = self.component_data.get(f"{year2}1231", pd.DataFrame())
            
            if code_col in df1.columns and code_col in df2.columns:
                codes1 = set(df1[code_col].astype(str))
                codes2 = set(df2[code_col].astype(str))
                
                added = codes2 - codes1
                removed = codes1 - codes2
                retained = codes1 & codes2
                
                results['turnover_analysis'][f"{year1}-{year2}"] = {
                    'added': len(added),
                    'removed': len(removed),
                    'retained': len(retained),
                    'turnover_rate': (len(added) + len(removed)) / len(codes1) if codes1 else 0
                }
        
        return results
    
    def calculate_factor_performance(self, prices_df: pd.DataFrame, 
                                     factor_data: pd.DataFrame, factor_name: str,
                                     periods: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        results = []
        
        for start_date, end_date in periods:
            mask = (prices_df['date'] >= start_date) & (prices_df['date'] <= end_date)
            period_prices = prices_df[mask]
            
            factor_mask = (factor_data['date'] >= start_date) & (factor_data['date'] <= end_date)
            period_factor = factor_data[factor_mask]
            
            if period_prices.empty or period_factor.empty:
                results.append({
                    'period': f"{start_date}~{end_date}",
                    'error': 'No data available'
                })
                continue
            
            merged = pd.merge(period_prices, period_factor, on='date', how='inner')
            
            if len(merged) < 10:
                results.append({
                    'period': f"{start_date}~{end_date}",
                    'error': 'Insufficient data'
                })
                continue
            
            returns = merged['close'].pct_change().dropna()
            factor_values = merged[factor_name].dropna()
            
            aligned_returns, aligned_factor = returns.align(factor_values, join='inner')
            
            if len(aligned_returns) < 10:
                results.append({
                    'period': f"{start_date}~{end_date}",
                    'error': 'Insufficient aligned data'
                })
                continue
            
            ic = aligned_returns.corr(aligned_factor)
            icir = ic / aligned_returns.std() if aligned_returns.std() != 0 else 0
            
            results.append({
                'period': f"{start_date}~{end_date}",
                'factor_name': factor_name,
                'ic': float(ic),
                'icir': float(icir),
                'sample_size': len(aligned_returns),
                'factor_mean': float(aligned_factor.mean()),
                'factor_std': float(aligned_factor.std()),
                'return_mean': float(aligned_returns.mean()),
                'return_std': float(aligned_returns.std())
            })
        
        return results
    
    def predict_market_trend(self, prices_df: pd.DataFrame, 
                             prediction_days: int = 30) -> Dict[str, Any]:
        if len(prices_df) < 60:
            return {'error': 'Insufficient historical data'}
        
        dates = prices_df['date']
        prices = prices_df['close'].values
        
        X = np.arange(len(prices)).reshape(-1, 1)
        y = prices
        
        model = LinearRegression()
        model.fit(X, y)
        
        future_X = np.arange(len(prices), len(prices) + prediction_days).reshape(-1, 1)
        predictions = model.predict(future_X)
        
        last_date = pd.to_datetime(dates.iloc[-1])
        future_dates = [last_date + timedelta(days=i) for i in range(1, prediction_days + 1)]
        
        trend_slope = float(model.coef_[0])
        trend_direction = 'up' if trend_slope > 0 else 'down' if trend_slope < 0 else 'flat'
        
        r_squared = float(model.score(X, y))
        
        return {
            'trend_direction': trend_direction,
            'trend_slope': trend_slope,
            'r_squared': r_squared,
            'predictions': [{
                'date': date.strftime('%Y-%m-%d'),
                'price': float(price),
                'confidence': float(min(r_squared, 0.95))
            } for date, price in zip(future_dates, predictions)],
            'historical_stats': {
                'mean_price': float(prices.mean()),
                'std_price': float(prices.std()),
                'recent_max': float(prices[-30:].max()),
                'recent_min': float(prices[-30:].min())
            }
        }
    
    def generate_statistical_summary(self, prices_df: pd.DataFrame, 
                                     periods: List[Tuple[str, str]]) -> Dict[str, Any]:
        summary = {
            'period_analysis': self.analyze_periods(prices_df, periods),
            'overall_stats': {},
            'csi300_trends': self.analyze_csi300_composition_trend()
        }
        
        all_returns = prices_df['close'].pct_change().dropna()
        summary['overall_stats'] = {
            'total_days': len(prices_df),
            'start_date': prices_df['date'].iloc[0],
            'end_date': prices_df['date'].iloc[-1],
            'total_return': float((prices_df['close'].iloc[-1] - prices_df['close'].iloc[0]) / prices_df['close'].iloc[0]),
            'avg_daily_return': float(all_returns.mean()),
            'std_daily_return': float(all_returns.std()),
            'annualized_return': float((1 + all_returns.mean()) ** 252 - 1),
            'annualized_volatility': float(all_returns.std() * np.sqrt(252)),
            'sharpe_ratio': float(self._calculate_sharpe_ratio(all_returns)),
            'max_drawdown': float(self._calculate_max_drawdown(prices_df['close'])),
            'skewness': float(all_returns.skew()),
            'kurtosis': float(all_returns.kurt()),
            'positive_days': int((all_returns > 0).sum()),
            'negative_days': int((all_returns < 0).sum()),
            'win_rate': float((all_returns > 0).sum() / len(all_returns))
        }
        
        return summary
    
    def create_backtest_summary(self, prices_df: pd.DataFrame, 
                                signal_df: pd.DataFrame, signal_column: str = 'signal') -> Dict[str, Any]:
        merged = pd.merge(prices_df, signal_df, on='date', how='inner')
        
        if merged.empty or signal_column not in merged.columns:
            return {'error': 'No valid signal data'}
        
        merged['return'] = merged['close'].pct_change()
        merged['strategy_return'] = merged['return'] * merged[signal_column].shift()
        
        strategy_returns = merged['strategy_return'].dropna()
        benchmark_returns = merged['return'].dropna()
        
        strategy_cumulative = (1 + strategy_returns).cumprod()
        benchmark_cumulative = (1 + benchmark_returns).cumprod()
        
        return {
            'total_days': len(strategy_returns),
            'strategy_total_return': float(strategy_cumulative.iloc[-1] - 1),
            'benchmark_total_return': float(benchmark_cumulative.iloc[-1] - 1),
            'excess_return': float((strategy_cumulative.iloc[-1] - 1) - (benchmark_cumulative.iloc[-1] - 1)),
            'strategy_sharpe': float(self._calculate_sharpe_ratio(strategy_returns)),
            'benchmark_sharpe': float(self._calculate_sharpe_ratio(benchmark_returns)),
            'strategy_max_drawdown': float(self._calculate_max_drawdown(strategy_cumulative)),
            'benchmark_max_drawdown': float(self._calculate_max_drawdown(benchmark_cumulative)),
            'win_rate': float((strategy_returns > 0).sum() / len(strategy_returns)),
            'profit_factor': float(strategy_returns[strategy_returns > 0].sum() / abs(strategy_returns[strategy_returns < 0].sum())) if (strategy_returns < 0).sum() > 0 else float('inf'),
            'cagr': float((1 + strategy_returns.mean()) ** 252 - 1),
            'strategy_returns': strategy_returns.to_list(),
            'benchmark_returns': benchmark_returns.to_list(),
            'cumulative_curve': [{
                'date': merged['date'].iloc[i],
                'strategy': float(strategy_cumulative.iloc[i]),
                'benchmark': float(benchmark_cumulative.iloc[i])
            } for i in range(len(strategy_cumulative))]
        }