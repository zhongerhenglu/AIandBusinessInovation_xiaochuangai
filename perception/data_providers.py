import pandas as pd
import numpy as np
from typing import Dict, Any, List
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class DataProvider(ABC):
    @abstractmethod
    def fetch(self, timestamp) -> Dict[str, Any]:
        pass


class OHLCDataProvider(DataProvider):
    def __init__(self):
        self.symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
    
    def fetch(self, timestamp) -> Dict[str, Any]:
        logger.debug(f"Fetching OHLC data for {timestamp}")
        data = {}
        for symbol in self.symbols:
            data[symbol] = {
                "open": np.random.uniform(100, 500),
                "high": np.random.uniform(100, 500),
                "low": np.random.uniform(100, 500),
                "close": np.random.uniform(100, 500),
                "volume": np.random.randint(1000000, 10000000),
                "timestamp": timestamp
            }
        return data


class NewsDataProvider(DataProvider):
    def __init__(self):
        self.news_topics = ["earnings", "market", "technology", "policy", "economy"]
    
    def fetch(self, timestamp) -> Dict[str, Any]:
        logger.debug(f"Fetching news data for {timestamp}")
        news_items = []
        for topic in self.news_topics:
            news_items.append({
                "title": f"Market update for {topic}",
                "content": f"Latest news about {topic} sector. Market sentiment is positive.",
                "topic": topic,
                "sentiment": np.random.uniform(-1, 1),
                "timestamp": timestamp
            })
        return {"news": news_items}


class FundamentalDataProvider(DataProvider):
    def __init__(self):
        self.metrics = ["pe_ratio", "pb_ratio", "roe", "revenue_growth", "debt_ratio"]
    
    def fetch(self, timestamp) -> Dict[str, Any]:
        logger.debug(f"Fetching fundamental data for {timestamp}")
        fundamentals = {}
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
        for symbol in symbols:
            fundamentals[symbol] = {metric: np.random.uniform(0.1, 50) for metric in self.metrics}
        return fundamentals


class OnChainDataProvider(DataProvider):
    def fetch(self, timestamp) -> Dict[str, Any]:
        logger.debug(f"Fetching on-chain data for {timestamp}")
        return {
            "total_value_locked": np.random.uniform(50, 200),
            "transaction_count": np.random.randint(100000, 1000000),
            "active_addresses": np.random.randint(10000, 100000)
        }


class SentimentDataProvider(DataProvider):
    def fetch(self, timestamp) -> Dict[str, Any]:
        logger.debug(f"Fetching sentiment data for {timestamp}")
        return {
            "twitter_sentiment": np.random.uniform(-1, 1),
            "news_sentiment": np.random.uniform(-1, 1),
            "market_sentiment": np.random.uniform(-1, 1)
        }


class L2DataProvider(DataProvider):
    def __init__(self):
        self.symbols = ["510300", "510050", "512760", "159915", "510500"]
    
    def fetch(self, timestamp) -> Dict[str, Any]:
        logger.debug(f"Fetching L2 data for {timestamp}")
        data = {}
        
        for symbol in self.symbols:
            order_book = self._generate_order_book(symbol, timestamp)
            trade_ticks = self._generate_trade_ticks(symbol, timestamp)
            
            data[symbol] = {
                'order_book': order_book,
                'trade_ticks': trade_ticks,
                'timestamp': timestamp,
            }
        
        return data
    
    def _generate_order_book(self, symbol: str, timestamp: str) -> Dict[str, Any]:
        base_price = np.random.uniform(2, 10)
        
        asks = []
        bids = []
        
        for i in range(5):
            asks.append({
                'price': round(base_price * (1 + 0.001 * (i + 1)), 2),
                'volume': np.random.randint(1000, 50000),
                'order_count': np.random.randint(1, 50),
            })
            
            bids.append({
                'price': round(base_price * (1 - 0.001 * (i + 1)), 2),
                'volume': np.random.randint(1000, 50000),
                'order_count': np.random.randint(1, 50),
            })
        
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'asks': asks,
            'bids': bids,
        }
    
    def _generate_trade_ticks(self, symbol: str, timestamp: str) -> List[Dict[str, Any]]:
        ticks = []
        base_price = np.random.uniform(2, 10)
        
        for i in range(np.random.randint(5, 20)):
            ticks.append({
                'symbol': symbol,
                'timestamp': f"{timestamp} {np.random.randint(930, 1500):04d}",
                'price': round(base_price * np.random.uniform(0.999, 1.001), 2),
                'volume': np.random.randint(100, 10000),
                'amount': round(base_price * np.random.randint(100, 10000), 2),
                'trade_type': np.random.choice(['buy', 'sell']),
                'buy_order_id': f"BO{np.random.randint(1000000, 9999999)}",
                'sell_order_id': f"SO{np.random.randint(1000000, 9999999)}",
            })
        
        return ticks


class ETFDataProvider(DataProvider):
    def __init__(self):
        self.etf_list = [
            {'symbol': '510300', 'name': '沪深300ETF', 'category': 'index/CSI300', 'issuer': '华泰柏瑞'},
            {'symbol': '510050', 'name': '上证50ETF', 'category': 'index/SSE50', 'issuer': '华夏基金'},
            {'symbol': '159915', 'name': '创业板ETF', 'category': 'index/ChiNext', 'issuer': '易方达'},
            {'symbol': '510500', 'name': '中证500ETF', 'category': 'index/CSI500', 'issuer': '南方基金'},
            {'symbol': '512760', 'name': '半导体ETF', 'category': 'equity/sector/technology', 'issuer': '国联安'},
            {'symbol': '512880', 'name': '证券ETF', 'category': 'equity/sector/finance', 'issuer': '华宝基金'},
            {'symbol': '512000', 'name': '券商ETF', 'category': 'equity/sector/finance', 'issuer': '国泰基金'},
            {'symbol': '159995', 'name': '芯片ETF', 'category': 'equity/theme/chip', 'issuer': '华夏基金'},
            {'symbol': '513050', 'name': '中概互联ETF', 'category': 'cross_border/US_tech', 'issuer': '易方达'},
            {'symbol': '513100', 'name': '纳指ETF', 'category': 'cross_border/US_tech', 'issuer': '国泰基金'},
            {'symbol': '518880', 'name': '黄金ETF', 'category': 'commodity/gold', 'issuer': '华安基金'},
            {'symbol': '511010', 'name': '国债ETF', 'category': 'bond/government', 'issuer': '国泰基金'},
            {'symbol': '516160', 'name': '新能源ETF', 'category': 'equity/theme/new_energy', 'issuer': '华夏基金'},
            {'symbol': '588000', 'name': '科创50ETF', 'category': 'index/STAR', 'issuer': '华夏基金'},
            {'symbol': '512170', 'name': '医疗ETF', 'category': 'equity/sector/healthcare', 'issuer': '华宝基金'},
        ]
    
    def fetch(self, timestamp) -> Dict[str, Any]:
        logger.debug(f"Fetching ETF data for {timestamp}")
        
        etf_data = []
        for etf in self.etf_list:
            etf_data.append({
                'symbol': etf['symbol'],
                'name': etf['name'],
                'category': etf['category'].split('/')[0],
                'sub_category': etf['category'].split('/')[1] if '/' in etf['category'] else None,
                'issuer': etf['issuer'],
                'price': round(np.random.uniform(1, 5), 2),
                'volume': np.random.randint(1000000, 100000000),
                'scale': round(np.random.uniform(10, 500), 2),
                'fee_rate': round(np.random.uniform(0.15, 0.5), 2),
                'creation_date': f"20{np.random.randint(15, 24)}-{np.random.randint(1, 12):02d}-{np.random.randint(1, 28):02d}",
                'tracking_index': self._get_tracking_index(etf['symbol']),
                'timestamp': timestamp,
            })
        
        return {"etfs": etf_data}
    
    def _get_tracking_index(self, symbol: str) -> str:
        index_map = {
            '510300': '沪深300指数',
            '510050': '上证50指数',
            '159915': '创业板指',
            '510500': '中证500指数',
            '512760': '中证半导体指数',
            '512880': '中证全指证券公司指数',
            '512000': '中证全指证券公司指数',
            '159995': '国证芯片指数',
            '513050': '中证海外中国互联网指数',
            '513100': '纳斯达克100指数',
            '518880': '上海黄金交易所Au99.99',
            '511010': '上证5年期国债指数',
            '516160': '中证新能源指数',
            '588000': '科创50指数',
            '512170': '中证医疗指数',
        }
        return index_map.get(symbol, '未知指数')


class SectionDataProvider(DataProvider):
    def __init__(self):
        self.stock_symbols = [
            '600519', '000858', '601318', '600036', '600030',
            '000001', '601328', '601899', '600048', '000651',
            '601888', '600887', '000333', '601628', '601398',
            '600000', '600585', '002594', '002415', '601166',
        ]
    
    def fetch(self, timestamp) -> Dict[str, Any]:
        logger.debug(f"Fetching section data for {timestamp}")
        
        section_data = {}
        for symbol in self.stock_symbols:
            close_price = np.random.uniform(5, 500)
            section_data[symbol] = {
                'symbol': symbol,
                'date': timestamp,
                'open': round(np.random.uniform(close_price * 0.99, close_price * 1.01), 2),
                'high': round(np.random.uniform(close_price, close_price * 1.02), 2),
                'low': round(np.random.uniform(close_price * 0.98, close_price), 2),
                'close': close_price,
                'volume': np.random.randint(100000, 10000000),
                'vwap': round(np.random.uniform(close_price * 0.995, close_price * 1.005), 2),
                'pe_ratio': round(np.random.uniform(5, 50), 2),
                'pb_ratio': round(np.random.uniform(0.5, 10), 2),
                'roe': round(np.random.uniform(-5, 30), 2),
                'roa': round(np.random.uniform(-3, 20), 2),
                'revenue_growth': round(np.random.uniform(-20, 50), 2),
                'debt_ratio': round(np.random.uniform(20, 80), 2),
                'dividend_yield': round(np.random.uniform(0, 10), 2),
                'ev_ebitda': round(np.random.uniform(5, 40), 2),
            }
        
        return section_data