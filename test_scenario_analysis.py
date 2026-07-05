import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quant.data_simulator import DataSimulator
from quant.quant_analyzer import QuantAnalyzer
from quant.chart_generator import ChartGenerator
from quant.macro_scenario_analyzer import MacroScenarioAnalyzer


def test_scenario_data_generation():
    print("=" * 80)
    print("测试1: 2026下半年情景模拟数据生成")
    print("=" * 80)
    
    scenario_params = {
        'fed_rate_unchanged': True,
        'japan_korea_crash': True,
        'china_rescue_amount': 2
    }
    
    simulator = DataSimulator()
    
    period_data = simulator.generate_period_comparison_data(scenario_params)
    
    for period_name, df in period_data.items():
        if period_name == 'all':
            continue
        print(f"\n--- {period_name} ---")
        print(f"  数据天数: {len(df)}")
        if not df.empty:
            print(f"  收盘价范围: {df['close'].min():.2f} ~ {df['close'].max():.2f}")
            start_price = df['close'].iloc[0]
            end_price = df['close'].iloc[-1]
            return_pct = (end_price - start_price) / start_price * 100
            print(f"  区间收益率: {return_pct:.2f}%")
    
    return period_data


def test_scenario_period_analysis(period_data):
    print("\n" + "=" * 80)
    print("测试2: 各时间段量化分析（含2026下半年）")
    print("=" * 80)
    
    analyzer = QuantAnalyzer()
    
    all_data = period_data['all']
    
    periods = [
        ('2024-07-01', '2024-12-31'),
        ('2025-01-01', '2025-06-30'),
        ('2025-07-01', '2025-12-31'),
        ('2026-01-01', '2026-06-30'),
        ('2026-07-01', '2026-12-31')
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


def test_macro_scenario_analysis():
    print("\n" + "=" * 80)
    print("测试3: 宏观情景分析")
    print("=" * 80)
    
    analyzer = MacroScenarioAnalyzer()
    
    scenario_params = {
        'fed_rate_unchanged': True,
        'japan_korea_crash': True,
        'china_rescue_amount': 2,
        'start_date': '2026-07-01',
        'end_date': '2026-12-31'
    }
    
    analysis = analyzer.analyze_scenario(scenario_params)
    
    print(f"\n  📋 情景描述: {analysis['scenario_description']}")
    
    print("\n  💰 市场影响分析:")
    for factor in analysis['market_impact']['factors']:
        impact_str = f"+{factor['impact']*100:.1f}%" if factor['impact'] > 0 else f"{factor['impact']*100:.1f}%"
        print(f"    • {factor['factor']}: {impact_str}")
        print(f"      原因: {factor['reason']}")
    
    print(f"\n  预期总收益: {analysis['market_impact']['total_expected_return']*100:.2f}%")
    print(f"  波动率变化: {analysis['market_impact']['net_volatility_change']*100:.2f}%")
    
    print("\n  📈 行业评级:")
    top_sectors = sorted(analysis['sector_impact'].items(), key=lambda x: x[1]['score'], reverse=True)[:6]
    for sector, info in top_sectors:
        return_str = f"+{info['expected_return']*100:.1f}%" if info['expected_return'] > 0 else f"{info['expected_return']*100:.1f}%"
        print(f"    {sector:>10}: {info['rating']:<8} 预期收益: {return_str:>8} 评分: {info['score']:.2f}")
    
    print("\n  🎯 股票推荐（前10）:")
    print(f"    {'行业':<8} {'代码':<12} {'名称':<10} {'评级':<8} {'预期收益'}")
    print("    " + "-" * 50)
    for rec in analysis['stock_recommendations'][:10]:
        return_str = f"+{rec['expected_return']*100:.1f}%" if rec['expected_return'] > 0 else f"{rec['expected_return']*100:.1f}%"
        print(f"    {rec['sector']:<8} {rec['code']:<12} {rec['name']:<10} {rec['rating']:<8} {return_str}")
    
    print("\n  ⚠️ 风险评估:")
    for risk in analysis['risk_assessment']['key_risks']:
        print(f"    • {risk['risk']}")
        print(f"      概率: {risk['probability']*100:.0f}%, 影响: {risk['impact']*100:.0f}%, 等级: {risk['level']}")
    
    return analysis


def test_chart_generation(all_data, period_results):
    print("\n" + "=" * 80)
    print("测试4: 生成2026下半年预测图表")
    print("=" * 80)
    
    chart_generator = ChartGenerator()
    
    summary = {
        'period_analysis': period_results,
        'overall_stats': {},
        'csi300_trends': {}
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
    
    charts = chart_generator.generate_all_charts(summary=summary, prices_df=all_data)
    
    print(f"\n  生成图表数量: {len(charts)}")
    for chart_path in charts:
        print(f"    - {os.path.basename(chart_path)}")
    
    return charts


def test_scenario_comparison():
    print("\n" + "=" * 80)
    print("测试5: 多情景对比分析")
    print("=" * 80)
    
    analyzer = MacroScenarioAnalyzer()
    
    scenarios = [
        {
            'name': '基准情景',
            'fed_rate_unchanged': True,
            'japan_korea_crash': False,
            'china_rescue_amount': 0
        },
        {
            'name': '日韩崩盘',
            'fed_rate_unchanged': True,
            'japan_korea_crash': True,
            'china_rescue_amount': 0
        },
        {
            'name': '2万亿救市',
            'fed_rate_unchanged': True,
            'japan_korea_crash': False,
            'china_rescue_amount': 2
        },
        {
            'name': '极端情景',
            'fed_rate_unchanged': True,
            'japan_korea_crash': True,
            'china_rescue_amount': 2
        }
    ]
    
    comparison = analyzer.generate_scenario_comparison(scenarios)
    
    print(f"\n  {'情景名称':<10} {'描述':<35} {'预期收益':>10} {'波动率变化':>12} {'风险等级'}")
    print("  " + "-" * 80)
    for scenario in comparison['scenarios']:
        return_str = f"+{scenario['expected_return']*100:.1f}%" if scenario['expected_return'] > 0 else f"{scenario['expected_return']*100:.1f}%"
        vol_str = f"+{scenario['volatility_change']*100:.1f}%" if scenario['volatility_change'] > 0 else f"{scenario['volatility_change']*100:.1f}%"
        print(f"  {scenario['scenario_name']:<10} {scenario['description']:<35} {return_str:>10} {vol_str:>12} {scenario['risk_level']}")
    
    print(f"\n  {comparison['summary']}")
    
    return comparison


if __name__ == '__main__':
    import numpy as np
    
    print("=" * 80)
    print("2026下半年情景分析系统测试")
    print("情景假设: 美联储利率不变 + 日韩股市崩盘 + 中国央行2万亿救市")
    print("=" * 80)
    
    period_data = test_scenario_data_generation()
    all_data, period_results = test_scenario_period_analysis(period_data)
    scenario_analysis = test_macro_scenario_analysis()
    charts = test_chart_generation(all_data, period_results)
    scenario_comparison = test_scenario_comparison()
    
    print("\n" + "=" * 80)
    print("所有测试完成!")
    print(f"  生成图表: {len(charts)} 张")
    print("=" * 80)