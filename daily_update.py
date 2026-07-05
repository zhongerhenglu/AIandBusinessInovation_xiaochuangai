import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
import os
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from perception.data_providers import (
    OHLCDataProvider, FundamentalDataProvider, L2DataProvider,
    ETFDataProvider, SectionDataProvider
)
from data.cross_section import CrossSectionProcessor, SectionStatisticsAggregator
from data.data_archive import DataArchive, ArchiveCleaner
from data.l2_data_processor import L2DataProcessor, L2DataValidator
from data.etf_classifier import ETFClassifier, ETFDataAnalyzer
from factor_library.factor_library import FactorLibrary
from utils.logging_utils import setup_logger

logger = setup_logger("daily_update")


class DailyUpdateWorkflow:
    def __init__(self):
        self.data_providers = {
            'ohlc': OHLCDataProvider(),
            'fundamental': FundamentalDataProvider(),
            'l2': L2DataProvider(),
            'etf': ETFDataProvider(),
            'section': SectionDataProvider(),
        }
        
        self.factor_library = FactorLibrary()
        self.cross_section_processor = CrossSectionProcessor(self.factor_library)
        self.statistics_aggregator = SectionStatisticsAggregator()
        self.data_archive = DataArchive()
        self.archive_cleaner = ArchiveCleaner(self.data_archive)
        self.l2_processor = L2DataProcessor()
        self.l2_validator = L2DataValidator()
        self.etf_classifier = ETFClassifier()
        self.etf_analyzer = ETFDataAnalyzer(self.etf_classifier)
        
        self.results = {}
    
    async def run(self, date: str = None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Starting daily update workflow for {date}")
        
        try:
            await self._step_fetch_data(date)
            await self._step_process_section(date)
            await self._step_process_l2_data(date)
            await self._step_update_etf_classification(date)
            await self._step_archive_data(date)
            await self._step_generate_report(date)
            
            logger.info("Daily update workflow completed successfully")
            return self.results
        
        except Exception as e:
            logger.error(f"Daily update workflow failed: {str(e)}", exc_info=True)
            return {'error': str(e)}
    
    async def _step_fetch_data(self, date: str):
        logger.info(f"Step 1: Fetching data for {date}")
        
        tasks = []
        for provider_name, provider in self.data_providers.items():
            tasks.append(asyncio.create_task(self._fetch_with_timeout(provider, date, provider_name)))
        
        results = await asyncio.gather(*tasks)
        
        for provider_name, data in results:
            self.results[f'{provider_name}_data'] = data
            logger.info(f"Fetched {provider_name} data: {len(data) if isinstance(data, dict) else 'N/A'} items")
    
    async def _fetch_with_timeout(self, provider, date: str, provider_name: str):
        try:
            data = provider.fetch(date)
            return (provider_name, data)
        except Exception as e:
            logger.error(f"Failed to fetch {provider_name} data: {str(e)}")
            return (provider_name, {})
    
    async def _step_process_section(self, date: str):
        logger.info(f"Step 2: Processing cross-section data for {date}")
        
        section_data = self.results.get('section_data', {})
        
        if not section_data:
            logger.warning("No section data available, skipping section processing")
            return
        
        df = self.cross_section_processor.compute_daily_section(date, section_data)
        stats = self.cross_section_processor.compute_section_statistics(df)
        factor_ics = self.cross_section_processor.compute_all_factor_ics(df)
        
        self.results['section_df'] = df
        self.results['section_stats'] = stats
        self.results['factor_ics'] = factor_ics
        
        self.statistics_aggregator.aggregate_daily(stats)
        
        logger.info(f"Processed cross-section: {len(df)} stocks, {len(factor_ics)} factors analyzed")
    
    async def _step_process_l2_data(self, date: str):
        logger.info(f"Step 3: Processing L2 data for {date}")
        
        l2_data = self.results.get('l2_data', {})
        
        if not l2_data:
            logger.warning("No L2 data available, skipping L2 processing")
            return
        
        processed_results = {}
        validation_results = {}
        
        for symbol, data in l2_data.items():
            all_ticks = []
            
            if 'order_book' in data:
                all_ticks.append({'type': 'order_book', **data['order_book']})
            
            if 'trade_ticks' in data:
                for tick in data['trade_ticks']:
                    all_ticks.append({'type': 'trade', **tick})
            
            processed = self.l2_processor.process_tick_data(all_ticks)
            validation = self.l2_validator.validate_batch(all_ticks)
            
            processed_results[symbol] = processed
            validation_results[symbol] = validation
        
        self.results['l2_processed'] = processed_results
        self.results['l2_validation'] = validation_results
        
        total_valid = sum(v['valid_count'] for v in validation_results.values())
        total_ticks = sum(v['total_ticks'] for v in validation_results.values())
        logger.info(f"Processed L2 data: {total_ticks} ticks, {total_valid} valid")
    
    async def _step_update_etf_classification(self, date: str):
        logger.info(f"Step 4: Updating ETF classification for {date}")
        
        etf_data = self.results.get('etf_data', {}).get('etfs', [])
        
        if not etf_data:
            logger.warning("No ETF data available, skipping ETF classification")
            return
        
        self.etf_classifier.load_from_exchange_data(etf_data)
        category_stats = self.etf_classifier.get_category_statistics()
        validation = self.etf_classifier.validate_classification()
        
        self.results['etf_category_stats'] = category_stats
        self.results['etf_validation'] = validation
        
        logger.info(f"Updated ETF classification: {len(self.etf_classifier.get_all_etfs())} ETFs in {len(category_stats)} categories")
    
    async def _step_archive_data(self, date: str):
        logger.info(f"Step 5: Archiving data for {date}")
        
        archive_tasks = []
        
        if 'section_df' in self.results:
            archive_tasks.append({
                'data_type': 'sections',
                'date': date,
                'data': self.results['section_df'],
            })
        
        if 'ohlc_data' in self.results:
            archive_tasks.append({
                'data_type': 'ohlc',
                'date': date,
                'data': self.results['ohlc_data'],
            })
        
        if 'fundamental_data' in self.results:
            archive_tasks.append({
                'data_type': 'fundamental',
                'date': date,
                'data': self.results['fundamental_data'],
            })
        
        if 'l2_processed' in self.results:
            archive_tasks.append({
                'data_type': 'l2_data',
                'date': date,
                'data': self.results['l2_processed'],
            })
        
        if 'etf_data' in self.results:
            archive_tasks.append({
                'data_type': 'etf',
                'date': date,
                'data': self.results['etf_data'],
            })
        
        if archive_tasks:
            results = self.data_archive.batch_archive(archive_tasks, max_workers=4)
            self.results['archive_results'] = results
            
            success_count = sum(1 for r in results if r['status'] == 'success')
            logger.info(f"Archived {success_count}/{len(results)} data types")
        
        self.archive_cleaner.remove_duplicates('sections', date)
    
    async def _step_generate_report(self, date: str):
        logger.info(f"Step 6: Generating daily report for {date}")
        
        report = {
            'date': date,
            'generated_at': datetime.now().isoformat(),
            'section_statistics': self.results.get('section_stats', {}),
            'factor_ic_summary': self._summarize_factor_ics(),
            'l2_summary': self._summarize_l2_data(),
            'etf_summary': self._summarize_etf_data(),
            'archive_summary': self.data_archive.get_archive_summary(),
        }
        
        self.results['daily_report'] = report
        
        report_path = f'output/daily_report_{date}.json'
        os.makedirs('output', exist_ok=True)
        
        import json

        def serialize(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, pd.Series):
                return obj.to_dict()
            elif isinstance(obj, pd.DataFrame):
                return obj.to_dict(orient='records')
            elif isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize(item) for item in obj]
            else:
                return obj
        
        serialized_report = serialize(report)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(serialized_report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Generated daily report: {report_path}")
        self._print_report_summary(report)
    
    def _summarize_factor_ics(self) -> Dict[str, Any]:
        factor_ics = self.results.get('factor_ics', {})
        if not factor_ics:
            return {}
        
        ics_list = [v for v in factor_ics.values() if not isinstance(v, type(None)) and not np.isnan(v)]
        
        return {
            'total_factors': len(factor_ics),
            'avg_ic': float(np.mean(ics_list)) if ics_list else 0.0,
            'ic_std': float(np.std(ics_list)) if ics_list else 0.0,
            'positive_ic_count': sum(1 for v in ics_list if v > 0),
            'negative_ic_count': sum(1 for v in ics_list if v < 0),
            'high_quality_factors': [k for k, v in factor_ics.items() if v and abs(v) > 0.3],
        }
    
    def _summarize_l2_data(self) -> Dict[str, Any]:
        l2_processed = self.results.get('l2_processed', {})
        if not l2_processed:
            return {}
        
        summary = {
            'symbols_count': len(l2_processed),
            'total_ticks': 0,
            'avg_spread': [],
            'big_trade_ratio': [],
        }
        
        for symbol, data in l2_processed.items():
            stats = data.get('statistics', {})
            summary['total_ticks'] += len(data.get('trade_ticks', []))
            if 'avg_spread' in stats:
                summary['avg_spread'].append(stats['avg_spread'])
            if 'big_trade_volume_ratio' in stats:
                summary['big_trade_ratio'].append(stats['big_trade_volume_ratio'])
        
        if summary['avg_spread']:
            summary['avg_spread'] = float(np.mean(summary['avg_spread']))
        if summary['big_trade_ratio']:
            summary['big_trade_ratio'] = float(np.mean(summary['big_trade_ratio']))
        
        return summary
    
    def _summarize_etf_data(self) -> Dict[str, Any]:
        category_stats = self.results.get('etf_category_stats', {})
        if not category_stats:
            return {}
        
        return {
            'total_categories': len(category_stats),
            'total_etfs': sum(v['count'] for v in category_stats.values()),
            'categories': list(category_stats.keys()),
        }
    
    def _print_report_summary(self, report: Dict[str, Any]):
        print("\n" + "=" * 60)
        print(f"DAILY UPDATE REPORT - {report['date']}")
        print("=" * 60)
        
        stats = report.get('section_statistics', {})
        print(f"\n[截面统计]")
        print(f"  股票数量: {stats.get('stock_count', 0)}")
        print(f"  平均日收益: {stats.get('avg_return', 0):.4f}")
        print(f"  收益标准差: {stats.get('return_std', 0):.4f}")
        print(f"  上涨股票: {stats.get('positive_count', 0)}")
        print(f"  下跌股票: {stats.get('negative_count', 0)}")
        
        factor_summary = report.get('factor_ic_summary', {})
        print(f"\n[因子IC分析]")
        print(f"  因子总数: {factor_summary.get('total_factors', 0)}")
        print(f"  平均IC: {factor_summary.get('avg_ic', 0):.4f}")
        print(f"  高质量因子: {len(factor_summary.get('high_quality_factors', []))}")
        
        l2_summary = report.get('l2_summary', {})
        print(f"\n[L2数据统计]")
        print(f"  标的数量: {l2_summary.get('symbols_count', 0)}")
        print(f"  成交笔数: {l2_summary.get('total_ticks', 0)}")
        print(f"  平均买卖价差: {l2_summary.get('avg_spread', 0):.4f}")
        
        etf_summary = report.get('etf_summary', {})
        print(f"\n[ETF分类]")
        print(f"  分类数量: {etf_summary.get('total_categories', 0)}")
        print(f"  ETF总数: {etf_summary.get('total_etfs', 0)}")
        
        archive_summary = report.get('archive_summary', {})
        print(f"\n[数据归档]")
        print(f"  总条目数: {archive_summary.get('total_entries', 0)}")
        print(f"  数据类型: {list(archive_summary.get('data_types', {}).keys())}")
        
        print("\n" + "=" * 60)


async def run_historical_update(start_date: str, end_date: str):
    workflow = DailyUpdateWorkflow()
    
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    current = start
    while current <= end:
        date_str = current.strftime('%Y-%m-%d')
        
        if current.weekday() < 5:
            logger.info(f"Processing historical data for {date_str}")
            await workflow.run(date_str)
        
        current += timedelta(days=1)


if __name__ == '__main__':
    import argparse
    import numpy as np
    
    parser = argparse.ArgumentParser(description='Daily Update Workflow')
    parser.add_argument('--date', type=str, default=None, help='Date to process (YYYY-MM-DD)')
    parser.add_argument('--historical', action='store_true', help='Run historical update')
    parser.add_argument('--start-date', type=str, default=None, help='Start date for historical update')
    parser.add_argument('--end-date', type=str, default=None, help='End date for historical update')
    
    args = parser.parse_args()
    
    if args.historical and args.start_date and args.end_date:
        asyncio.run(run_historical_update(args.start_date, args.end_date))
    else:
        asyncio.run(DailyUpdateWorkflow().run(args.date))