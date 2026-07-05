import pandas as pd
import numpy as np
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import os
import logging

logger = logging.getLogger(__name__)


class ChartGenerator:
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output')
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def generate_period_return_chart(self, period_results: List[Dict[str, Any]], 
                                     output_filename: str = 'period_returns.png') -> str:
        periods = [r['period_label'] for r in period_results if 'error' not in r]
        returns = [r['total_return'] * 100 for r in period_results if 'error' not in r]
        sharpe_ratios = [r['sharpe_ratio'] for r in period_results if 'error' not in r]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        colors = ['#1f77b4' if r >= 0 else '#ff4b5c' for r in returns]
        bars1 = ax1.bar(periods, returns, color=colors)
        ax1.set_title('各时间段收益率对比', fontsize=14, fontweight='bold')
        ax1.set_ylabel('收益率 (%)', fontsize=12)
        ax1.grid(True, axis='y', alpha=0.3)
        
        for i, bar in enumerate(bars1):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=10)
        
        bars2 = ax2.bar(periods, sharpe_ratios, color='#2ca02c')
        ax2.set_title('各时间段夏普比率', fontsize=14, fontweight='bold')
        ax2.set_ylabel('夏普比率', fontsize=12)
        ax2.set_xlabel('时间段', fontsize=12)
        ax2.grid(True, axis='y', alpha=0.3)
        
        for i, bar in enumerate(bars2):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, output_filename)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_equity_curve(self, prices_df: pd.DataFrame, 
                              predictions: List[Dict[str, float]] = None,
                              output_filename: str = 'equity_curve.png') -> str:
        fig, ax = plt.subplots(figsize=(14, 7))
        
        ax.plot(prices_df['date'], prices_df['close'], label='实际价格', color='#1f77b4', linewidth=2)
        
        if predictions:
            pred_dates = [p['date'] for p in predictions]
            pred_prices = [p['price'] for p in predictions]
            ax.plot(pred_dates, pred_prices, label='预测价格', color='#ff7f0e', linestyle='--', linewidth=2)
            
            confidence = predictions[0].get('confidence', 0.8)
            ax.fill_between(pred_dates, 
                            [p['price'] * (1 - (1 - confidence)) for p in predictions],
                            [p['price'] * (1 + (1 - confidence)) for p in predictions],
                            alpha=0.2, color='#ff7f0e', label=f'置信区间 ({confidence*100:.0f}%)')
        
        ax.set_title('价格走势与预测', fontsize=14, fontweight='bold')
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('价格', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        output_path = os.path.join(self.output_dir, output_filename)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_factor_ic_chart(self, factor_results: List[Dict[str, Any]],
                                 output_filename: str = 'factor_ic.png') -> str:
        periods = [r['period'] for r in factor_results if 'error' not in r]
        ics = [r['ic'] for r in factor_results if 'error' not in r]
        icirs = [r['icir'] for r in factor_results if 'error' not in r]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        colors = ['#1f77b4' if ic >= 0 else '#ff4b5c' for ic in ics]
        bars1 = ax1.bar(periods, ics, color=colors)
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax1.set_title(f'因子IC值 ({factor_results[0].get("factor_name", "Unknown")})', fontsize=14, fontweight='bold')
        ax1.set_ylabel('IC值', fontsize=12)
        ax1.grid(True, axis='y', alpha=0.3)
        
        for i, bar in enumerate(bars1):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}', ha='center', va='bottom' if height >= 0 else 'top', fontsize=10)
        
        bars2 = ax2.bar(periods, icirs, color='#9467bd')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.set_title('因子ICIR', fontsize=14, fontweight='bold')
        ax2.set_ylabel('ICIR', fontsize=12)
        ax2.set_xlabel('时间段', fontsize=12)
        ax2.grid(True, axis='y', alpha=0.3)
        
        for i, bar in enumerate(bars2):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom' if height >= 0 else 'top', fontsize=10)
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, output_filename)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_backtest_chart(self, backtest_result: Dict[str, Any],
                                output_filename: str = 'backtest.png') -> str:
        if 'cumulative_curve' not in backtest_result:
            return ''
        
        curve = backtest_result['cumulative_curve']
        dates = [c['date'] for c in curve]
        strategy = [c['strategy'] for c in curve]
        benchmark = [c['benchmark'] for c in curve]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        ax1.plot(dates, strategy, label='策略收益', color='#1f77b4', linewidth=2)
        ax1.plot(dates, benchmark, label='基准收益', color='#ff7f0e', linewidth=2)
        ax1.set_title('策略收益曲线', fontsize=14, fontweight='bold')
        ax1.set_ylabel('累计收益', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        excess = [s - b for s, b in zip(strategy, benchmark)]
        colors = ['#1f77b4' if e >= 0 else '#ff4b5c' for e in excess]
        ax2.bar(dates, excess, color=colors, alpha=0.6)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.set_title('超额收益', fontsize=14, fontweight='bold')
        ax2.set_ylabel('超额收益', fontsize=12)
        ax2.set_xlabel('日期', fontsize=12)
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, output_filename)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_csi300_composition_chart(self, csi300_trends: Dict[str, Any],
                                          output_filename: str = 'csi300_composition.png') -> str:
        yearly_counts = csi300_trends.get('yearly_counts', [])
        turnover = csi300_trends.get('turnover_analysis', {})
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        years = [y['year'] for y in yearly_counts]
        counts = [y['stock_count'] for y in yearly_counts]
        
        ax1.plot(years, counts, marker='o', color='#1f77b4', linewidth=2)
        ax1.set_title('沪深300成分股数量变化', fontsize=14, fontweight='bold')
        ax1.set_ylabel('成分股数量', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        for i, count in enumerate(counts):
            ax1.text(years[i], count, str(count), ha='center', va='bottom', fontsize=10)
        
        if turnover:
            periods = list(turnover.keys())
            turnover_rates = [t['turnover_rate'] * 100 for t in turnover.values()]
            added = [t['added'] for t in turnover.values()]
            removed = [t['removed'] for t in turnover.values()]
            
            x = np.arange(len(periods))
            width = 0.35
            
            bars1 = ax2.bar(x - width/2, added, width, label='新增', color='#2ca02c')
            bars2 = ax2.bar(x + width/2, removed, width, label='剔除', color='#ff4b5c')
            
            ax2.set_title('沪深300成分股周转率', fontsize=14, fontweight='bold')
            ax2.set_ylabel('数量', fontsize=12)
            ax2.set_xlabel('时间段', fontsize=12)
            ax2.set_xticks(x)
            ax2.set_xticklabels(periods)
            ax2.legend()
            ax2.grid(True, axis='y', alpha=0.3)
            
            for i, rate in enumerate(turnover_rates):
                ax2.text(x[i], max(added[i], removed[i]) + 5,
                        f'周转率: {rate:.1f}%', ha='center', fontsize=9)
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, output_filename)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_sector_distribution_chart(self, sector_distribution: List[Dict[str, Any]],
                                           output_filename: str = 'sector_distribution.png') -> str:
        if not sector_distribution:
            return ''
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        for i, year_data in enumerate(sector_distribution[:6]):
            ax = axes[i]
            year = year_data['year']
            sectors = year_data['sectors']
            
            labels = list(sectors.keys())
            values = list(sectors.values())
            
            colors = plt.cm.tab20.colors[:len(labels)]
            wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                               colors=colors, textprops={'fontsize': 8})
            
            ax.set_title(f'{year}年行业分布', fontsize=12, fontweight='bold')
        
        for j in range(len(sector_distribution), len(axes)):
            axes[j].axis('off')
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, output_filename)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_statistics_summary_table(self, stats: Dict[str, Any],
                                          output_filename: str = 'statistics_summary.png') -> str:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.axis('tight')
        ax.axis('off')
        
        data = [
            ['指标', '数值'],
            ['总交易日', f"{stats.get('total_days', 0)}"],
            ['起始日期', f"{stats.get('start_date', '')}"],
            ['结束日期', f"{stats.get('end_date', '')}"],
            ['总收益率', f"{stats.get('total_return', 0) * 100:.2f}%"],
            ['年化收益率', f"{stats.get('annualized_return', 0) * 100:.2f}%"],
            ['年化波动率', f"{stats.get('annualized_volatility', 0) * 100:.2f}%"],
            ['夏普比率', f"{stats.get('sharpe_ratio', 0):.2f}"],
            ['最大回撤', f"{stats.get('max_drawdown', 0) * 100:.2f}%"],
            ['偏度', f"{stats.get('skewness', 0):.2f}"],
            ['峰度', f"{stats.get('kurtosis', 0):.2f}"],
            ['胜率', f"{stats.get('win_rate', 0) * 100:.2f}%"]
        ]
        
        table = ax.table(cellText=data, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        plt.title('统计摘要', fontsize=14, fontweight='bold')
        
        output_path = os.path.join(self.output_dir, output_filename)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_all_charts(self, summary: Dict[str, Any], 
                            prices_df: pd.DataFrame = None,
                            predictions: List[Dict[str, float]] = None,
                            factor_results: List[Dict[str, Any]] = None,
                            backtest_result: Dict[str, Any] = None) -> List[str]:
        output_paths = []
        
        if 'period_analysis' in summary:
            path = self.generate_period_return_chart(summary['period_analysis'])
            output_paths.append(path)
        
        if prices_df is not None:
            path = self.generate_equity_curve(prices_df, predictions)
            output_paths.append(path)
        
        if factor_results:
            path = self.generate_factor_ic_chart(factor_results)
            output_paths.append(path)
        
        if backtest_result and 'cumulative_curve' in backtest_result:
            path = self.generate_backtest_chart(backtest_result)
            output_paths.append(path)
        
        if 'csi300_trends' in summary:
            path = self.generate_csi300_composition_chart(summary['csi300_trends'])
            output_paths.append(path)
            
            sector_dist = summary['csi300_trends'].get('sector_distribution', [])
            if sector_dist:
                path = self.generate_sector_distribution_chart(sector_dist)
                output_paths.append(path)
        
        if 'overall_stats' in summary:
            path = self.generate_statistics_summary_table(summary['overall_stats'])
            output_paths.append(path)
        
        return output_paths