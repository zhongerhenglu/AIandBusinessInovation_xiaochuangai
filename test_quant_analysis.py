import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quant.data_simulator import DataSimulator
from quant.quant_analyzer import QuantAnalyzer
from quant.chart_generator import ChartGenerator


def test_data_generation():
    print("=" * 80)
    print("测试1: 生成模拟实盘数据")
    print("=" * 80)
    
    simulator = DataSimulator()
    
    period_data = simulator.generate_period_comparison_data()
    
    for period_name, df in period_data.items():
        if period_name == 'all':
            continue
        print(f"\n--- {period_name} ---")
        print(f"  数据天数: {len(df)}")
        print(f"  开盘价范围: {df['open'].min():.2f} ~ {df['open'].max():.2f}")
        print(f"  收盘价范围: {df['close'].min():.2f} ~ {df['close'].max():.2f}")
        print(f"  最高价: {df['high'].max():.2f}")
        print(f"  最低价: {df['low'].min():.2f}")
        print(f"  平均成交量: {df['volume'].mean():,.0f}")
    
    return period_data


def test_period_analysis():
    print("\n" + "=" * 80)
    print("测试2: 各时间段量化分析")
    print("=" * 80)
    
    simulator = DataSimulator()
    analyzer = QuantAnalyzer()
    
    all_data = simulator.generate_csi300_prices('2024-07-01', '2026-06-30')
    
    periods = [
        ('2024-07-01', '2024-12-31'),
        ('2025-01-01', '2025-06-30'),
        ('2025-07-01', '2025-12-31'),
        ('2026-01-01', '2026-06-30')
    ]
    
    results = analyzer.analyze_periods(all_data, periods)
    
    print(f"\n{'时间段':<20} {'收益率':>10} {'年化收益':>10} {'夏普比率':>10} {'最大回撤':>10} {'波动率':>10}")
    print("-" * 80)
    
    for result in results:
        if 'error' in result:
            print(f"{result['period_label']:<20} {'错误':>10}")
        else:
            print(f"{result['period_label']:<20} "
                  f"{result['total_return']*100:>9.2f}% "
                  f"{result['annualized_return']*100:>9.2f}% "
                  f"{result['sharpe_ratio']:>9.2f} "
                  f"{result['max_drawdown']*100:>9.2f}% "
                  f"{result['volatility']*100:>9.2f}%")
    
    return all_data, results


def test_csi300_composition_analysis():
    print("\n" + "=" * 80)
    print("测试3: 沪深300成分股分析")
    print("=" * 80)
    
    analyzer = QuantAnalyzer()
    
    available_dates = analyzer.get_available_dates()
    print(f"\n可用数据年份: {available_dates}")
    
    trends = analyzer.analyze_csi300_composition_trend()
    
    print("\n--- 成分股数量变化 ---")
    print(f"{'年份':<10} {'数量':>10} {'总权重':>10}")
    print("-" * 30)
    for year_data in trends['yearly_counts']:
        print(f"{year_data['year']:<10} {year_data['stock_count']:>10} {year_data['total_weight']:>9.2f}")
    
    print("\n--- 成分股周转率 ---")
    print(f"{'时间段':<15} {'新增':>8} {'剔除':>8} {'保留':>8} {'周转率':>10}")
    print("-" * 50)
    for period, data in trends['turnover_analysis'].items():
        print(f"{period:<15} {data['added']:>8} {data['removed']:>8} "
              f"{data['retained']:>8} {data['turnover_rate']*100:>9.1f}%")
    
    if trends['top_weights']:
        print("\n--- 2025年权重最高的前5只股票 ---")
        for year_data in trends['top_weights'][-1:]:
            print(f"\n{year_data['year']}年:")
            for stock in year_data['top_stocks'][:5]:
                print(f"  {stock['code']} {stock['name']}: {stock['weight']:.4f}")
    
    return trends


def test_factor_performance():
    print("\n" + "=" * 80)
    print("测试4: 因子表现分析")
    print("=" * 80)
    
    simulator = DataSimulator()
    analyzer = QuantAnalyzer()
    
    all_data = simulator.generate_csi300_prices('2024-07-01', '2026-06-30')
    momentum_data = simulator.generate_factor_data(all_data, 'momentum')
    
    periods = [
        ('2024-07-01', '2024-12-31'),
        ('2025-01-01', '2025-06-30'),
        ('2025-07-01', '2025-12-31'),
        ('2026-01-01', '2026-06-30')
    ]
    
    factor_results = analyzer.calculate_factor_performance(all_data, momentum_data, 'momentum', periods)
    
    print(f"\n{'时间段':<20} {'IC值':>10} {'ICIR':>10} {'样本量':>8} {'因子均值':>12}")
    print("-" * 70)
    
    for result in factor_results:
        if 'error' in result:
            print(f"{result['period']:<20} {'错误':>10}")
        else:
            print(f"{result['period']:<20} "
                  f"{result['ic']:>9.3f} "
                  f"{result['icir']:>9.2f} "
                  f"{result['sample_size']:>8} "
                  f"{result['factor_mean']:>11.4f}")
    
    return factor_results


def test_prediction():
    print("\n" + "=" * 80)
    print("测试5: 价格趋势预测")
    print("=" * 80)
    
    simulator = DataSimulator()
    analyzer = QuantAnalyzer()
    
    all_data = simulator.generate_csi300_prices('2024-07-01', '2026-06-30')
    
    prediction = analyzer.predict_market_trend(all_data, prediction_days=30)
    
    if 'error' in prediction:
        print(f"  ❌ 预测失败: {prediction['error']}")
        return None
    
    print(f"\n  趋势方向: {prediction['trend_direction']}")
    print(f"  趋势斜率: {prediction['trend_slope']:.4f}")
    print(f"  R²系数: {prediction['r_squared']:.4f}")
    
    print(f"\n  历史统计:")
    print(f"    平均价格: {prediction['historical_stats']['mean_price']:.2f}")
    print(f"    价格标准差: {prediction['historical_stats']['std_price']:.2f}")
    print(f"    近30日最高: {prediction['historical_stats']['recent_max']:.2f}")
    print(f"    近30日最低: {prediction['historical_stats']['recent_min']:.2f}")
    
    print(f"\n  未来7天预测:")
    for pred in prediction['predictions'][:7]:
        print(f"    {pred['date']}: {pred['price']:.2f} (置信度: {pred['confidence']*100:.0f}%)")
    
    return prediction


def test_backtest():
    print("\n" + "=" * 80)
    print("测试6: 策略回测")
    print("=" * 80)
    
    simulator = DataSimulator()
    analyzer = QuantAnalyzer()
    
    all_data = simulator.generate_csi300_prices('2024-07-01', '2026-06-30')
    signals = simulator.generate_trading_signals(all_data, 'moving_average')
    
    backtest = analyzer.create_backtest_summary(all_data, signals)
    
    if 'error' in backtest:
        print(f"  ❌ 回测失败: {backtest['error']}")
        return None
    
    print(f"\n  策略总收益: {backtest['strategy_total_return']*100:.2f}%")
    print(f"  基准总收益: {backtest['benchmark_total_return']*100:.2f}%")
    print(f"  超额收益: {backtest['excess_return']*100:.2f}%")
    print(f"  策略夏普比率: {backtest['strategy_sharpe']:.2f}")
    print(f"  基准夏普比率: {backtest['benchmark_sharpe']:.2f}")
    print(f"  策略最大回撤: {backtest['strategy_max_drawdown']*100:.2f}%")
    print(f"  基准最大回撤: {backtest['benchmark_max_drawdown']*100:.2f}%")
    print(f"  胜率: {backtest['win_rate']*100:.2f}%")
    print(f"  盈亏比: {backtest['profit_factor']:.2f}")
    print(f"  CAGR: {backtest['cagr']*100:.2f}%")
    
    return backtest


def test_chart_generation(all_data, period_results, csi300_trends, 
                         factor_results, prediction, backtest):
    print("\n" + "=" * 80)
    print("测试7: 生成统计图表")
    print("=" * 80)
    
    chart_generator = ChartGenerator()
    
    summary = {
        'period_analysis': period_results,
        'overall_stats': {},
        'csi300_trends': csi300_trends
    }
    
    all_returns = all_data['close'].pct_change().dropna()
    summary['overall_stats'] = {
        'total_days': len(all_data),
        'start_date': all_data['date'].iloc[0],
        'end_date': all_data['date'].iloc[-1],
        'total_return': float((all_data['close'].iloc[-1] - all_data['close'].iloc[0]) / all_data['close'].iloc[0]),
        'avg_daily_return': float(all_returns.mean()),
        'std_daily_return': float(all_returns.std()),
        'annualized_return': float((1 + all_returns.mean()) ** 252 - 1),
        'annualized_volatility': float(all_returns.std() * np.sqrt(252)),
        'sharpe_ratio': float((all_returns.mean() - 0.02/252) / all_returns.std() * np.sqrt(252)),
        'max_drawdown': float(((all_data['close'].cummax() - all_data['close']) / all_data['close'].cummax()).min()),
        'skewness': float(all_returns.skew()),
        'kurtosis': float(all_returns.kurt()),
        'positive_days': int((all_returns > 0).sum()),
        'negative_days': int((all_returns < 0).sum()),
        'win_rate': float((all_returns > 0).sum() / len(all_returns))
    }
    
    charts = chart_generator.generate_all_charts(
        summary=summary,
        prices_df=all_data,
        predictions=prediction.get('predictions', None) if prediction else None,
        factor_results=factor_results,
        backtest_result=backtest
    )
    
    print(f"\n  生成图表数量: {len(charts)}")
    for chart_path in charts:
        print(f"    - {os.path.basename(chart_path)}")
    
    return charts


def test_statistical_summary(all_data):
    print("\n" + "=" * 80)
    print("测试8: 完整统计摘要")
    print("=" * 80)
    
    analyzer = QuantAnalyzer()
    
    periods = [
        ('2024-07-01', '2024-12-31'),
        ('2025-01-01', '2025-06-30'),
        ('2025-07-01', '2025-12-31'),
        ('2026-01-01', '2026-06-30')
    ]
    
    summary = analyzer.generate_statistical_summary(all_data, periods)
    
    stats = summary['overall_stats']
    
    print("\n  📊 整体统计:")
    print(f"    总交易日: {stats['total_days']}")
    print(f"    时间范围: {stats['start_date']} ~ {stats['end_date']}")
    print(f"    总收益率: {stats['total_return']*100:.2f}%")
    print(f"    年化收益率: {stats['annualized_return']*100:.2f}%")
    print(f"    年化波动率: {stats['annualized_volatility']*100:.2f}%")
    print(f"    夏普比率: {stats['sharpe_ratio']:.2f}")
    print(f"    最大回撤: {stats['max_drawdown']*100:.2f}%")
    print(f"    偏度: {stats['skewness']:.2f}")
    print(f"    峰度: {stats['kurtosis']:.2f}")
    print(f"    胜率: {stats['win_rate']*100:.2f}%")
    
    return summary


if __name__ == '__main__':
    import numpy as np
    
    print("=" * 80)
    print("量化分析系统综合测试")
    print("=" * 80)
    
    period_data = test_data_generation()
    all_data, period_results = test_period_analysis()
    csi300_trends = test_csi300_composition_analysis()
    factor_results = test_factor_performance()
    prediction = test_prediction()
    backtest = test_backtest()
    summary = test_statistical_summary(all_data)
    charts = test_chart_generation(all_data, period_results, csi300_trends, 
                                   factor_results, prediction, backtest)
    
    print("\n" + "=" * 80)
    print("所有测试完成!")
    print(f"  生成图表: {len(charts)} 张")
    print(f"  输出目录: {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')}")
    print("=" * 80)