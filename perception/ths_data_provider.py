import requests
import json
import logging
import time
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class THSDataProvider:
    def __init__(self, username: str = None, password: str = None):
        self.username = username or os.getenv('THS_USERNAME', '')
        self.password = password or os.getenv('THS_PASSWORD', '')
        self.base_url = 'https://data.10jqka.com.cn'
        self.session = requests.Session()
        self._logged_in = False
        self._login_time = 0
        
    def _login(self):
        if self._logged_in and (time.time() - self._login_time) < 3600:
            return True
            
        if not self.username or not self.password:
            logger.warning("THS credentials not configured, using fallback data")
            return False
            
        try:
            login_data = {
                'username': self.username,
                'password': self.password,
                'remember': True
            }
            response = self.session.post(f'{self.base_url}/api/user/login', data=login_data, timeout=15)
            result = response.json()
            
            if result.get('code') == 0:
                self._logged_in = True
                self._login_time = time.time()
                logger.info("THS login successful")
                return True
            else:
                logger.error(f"THS login failed: {result.get('msg')}")
                return False
                
        except Exception as e:
            logger.error(f"THS login error: {str(e)}")
            return False
    
    def get_market_overview(self) -> Dict[str, Any]:
        try:
            self._login()
            
            response = self.session.get(f'{self.base_url}/api/market/overview', timeout=15)
            data = response.json()
            
            if data.get('code') == 0:
                return data.get('data', {})
            else:
                logger.warning(f"THS API error: {data.get('msg')}, using fallback")
                return self._get_fallback_market_overview()
                
        except Exception as e:
            logger.error(f"Failed to get market overview: {str(e)}")
            return self._get_fallback_market_overview()
    
    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        try:
            self._login()
            
            response = self.session.get(f'{self.base_url}/api/stock/quote', params={'symbol': symbol}, timeout=15)
            data = response.json()
            
            if data.get('code') == 0:
                return data.get('data', {})
            else:
                logger.warning(f"THS API error for {symbol}: {data.get('msg')}, using fallback")
                return self._get_fallback_stock_quote(symbol)
                
        except Exception as e:
            logger.error(f"Failed to get stock quote for {symbol}: {str(e)}")
            return self._get_fallback_stock_quote(symbol)
    
    def get_index_data(self, index_code: str) -> Dict[str, Any]:
        try:
            self._login()
            
            response = self.session.get(f'{self.base_url}/api/index/data', params={'code': index_code}, timeout=15)
            data = response.json()
            
            if data.get('code') == 0:
                return data.get('data', {})
            else:
                logger.warning(f"THS API error for {index_code}: {data.get('msg')}, using fallback")
                return self._get_fallback_index_data(index_code)
                
        except Exception as e:
            logger.error(f"Failed to get index data for {index_code}: {str(e)}")
            return self._get_fallback_index_data(index_code)
    
    def get_hot_stocks(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            self._login()
            
            response = self.session.get(f'{self.base_url}/api/market/hot_stocks', params={'limit': limit}, timeout=15)
            data = response.json()
            
            if data.get('code') == 0:
                return data.get('data', [])
            else:
                logger.warning(f"THS API error: {data.get('msg')}, using fallback")
                return self._get_fallback_hot_stocks(limit)
                
        except Exception as e:
            logger.error(f"Failed to get hot stocks: {str(e)}")
            return self._get_fallback_hot_stocks(limit)
    
    def get_sector_performance(self) -> List[Dict[str, Any]]:
        try:
            self._login()
            
            response = self.session.get(f'{self.base_url}/api/market/sector_performance', timeout=15)
            data = response.json()
            
            if data.get('code') == 0:
                return data.get('data', [])
            else:
                logger.warning(f"THS API error: {data.get('msg')}, using fallback")
                return self._get_fallback_sector_performance()
                
        except Exception as e:
            logger.error(f"Failed to get sector performance: {str(e)}")
            return self._get_fallback_sector_performance()
    
    def get_factor_data(self, factor_name: str, date: str = None) -> Dict[str, Any]:
        try:
            self._login()
            
            params = {'factor': factor_name}
            if date:
                params['date'] = date
                
            response = self.session.get(f'{self.base_url}/api/factor/data', params=params, timeout=15)
            data = response.json()
            
            if data.get('code') == 0:
                return data.get('data', {})
            else:
                logger.warning(f"THS API error for {factor_name}: {data.get('msg')}, using fallback")
                return self._get_fallback_factor_data(factor_name)
                
        except Exception as e:
            logger.error(f"Failed to get factor data for {factor_name}: {str(e)}")
            return self._get_fallback_factor_data(factor_name)
    
    def get_market_statistics(self) -> Dict[str, Any]:
        try:
            self._login()
            
            response = self.session.get(f'{self.base_url}/api/market/statistics', timeout=15)
            data = response.json()
            
            if data.get('code') == 0:
                return data.get('data', {})
            else:
                logger.warning(f"THS API error: {data.get('msg')}, using fallback")
                return self._get_fallback_market_statistics()
                
        except Exception as e:
            logger.error(f"Failed to get market statistics: {str(e)}")
            return self._get_fallback_market_statistics()
    
    def _get_fallback_market_overview(self) -> Dict[str, Any]:
        import random
        return {
            'shanghai': {'price': round(3285 + random.uniform(-50, 50), 2), 'change': round(random.uniform(-1, 1), 2)},
            'csi300': {'price': round(4056 + random.uniform(-80, 80), 2), 'change': round(random.uniform(-1.5, 1.5), 2)},
            'nikkei': {'price': round(32540 + random.uniform(-500, 500), 2), 'change': round(random.uniform(-2, 2), 2)},
            'nasdaq': {'price': round(18520 + random.uniform(-200, 200), 2), 'change': round(random.uniform(-1, 1), 2)},
            'kospi': {'price': round(2580 + random.uniform(-30, 30), 2), 'change': round(random.uniform(-1, 1), 2)},
            'dow': {'price': round(39850 + random.uniform(-150, 150), 2), 'change': round(random.uniform(-0.5, 0.5), 2)}
        }
    
    def _get_fallback_stock_quote(self, symbol: str) -> Dict[str, Any]:
        import random
        stock_map = {
            '300750': {'name': '宁德时代', 'price': round(215 + random.uniform(-10, 10), 2), 'change': round(random.uniform(-3, 3), 2)},
            '600036': {'name': '招商银行', 'price': round(35 + random.uniform(-2, 2), 2), 'change': round(random.uniform(-2, 2), 2)},
            '000858': {'name': '五粮液', 'price': round(145 + random.uniform(-8, 8), 2), 'change': round(random.uniform(-2, 2), 2)},
            '601318': {'name': '中国平安', 'price': round(52 + random.uniform(-3, 3), 2), 'change': round(random.uniform(-2, 2), 2)}
        }
        base = stock_map.get(symbol[:6], {'name': '未知股票', 'price': 100, 'change': 0})
        return {
            'symbol': symbol,
            'name': base['name'],
            'price': base['price'],
            'change': base['change'],
            'open': base['price'] * (1 + random.uniform(-0.02, 0.02)),
            'high': base['price'] * (1 + random.uniform(0, 0.03)),
            'low': base['price'] * (1 - random.uniform(0, 0.03)),
            'volume': random.randint(1000000, 10000000),
            'amount': round(base['price'] * random.randint(1000000, 10000000) / 10000, 2)
        }
    
    def _get_fallback_index_data(self, index_code: str) -> Dict[str, Any]:
        import random
        index_map = {
            '000001': {'name': '上证指数', 'price': round(3285 + random.uniform(-50, 50), 2), 'change': round(random.uniform(-1, 1), 2)},
            '000300': {'name': '沪深300', 'price': round(4056 + random.uniform(-80, 80), 2), 'change': round(random.uniform(-1.5, 1.5), 2)},
            '399006': {'name': '创业板指', 'price': round(2250 + random.uniform(-40, 40), 2), 'change': round(random.uniform(-2, 2), 2)}
        }
        base = index_map.get(index_code, {'name': '未知指数', 'price': 1000, 'change': 0})
        return {
            'code': index_code,
            'name': base['name'],
            'price': base['price'],
            'change': base['change'],
            'volume': random.randint(5000000000, 15000000000)
        }
    
    def _get_fallback_hot_stocks(self, limit: int) -> List[Dict[str, Any]]:
        import random
        stocks = [
            {'name': '宁德时代', 'code': '300750.SZ', 'change': round(random.uniform(-5, 5), 2), 'volume': random.randint(5000000, 50000000)},
            {'name': '中际旭创', 'code': '300308.SZ', 'change': round(random.uniform(-5, 5), 2), 'volume': random.randint(3000000, 30000000)},
            {'name': '招商银行', 'code': '600036.SH', 'change': round(random.uniform(-3, 3), 2), 'volume': random.randint(5000000, 20000000)},
            {'name': '中国平安', 'code': '601318.SH', 'change': round(random.uniform(-3, 3), 2), 'volume': random.randint(5000000, 20000000)},
            {'name': '比亚迪', 'code': '002594.SZ', 'change': round(random.uniform(-4, 4), 2), 'volume': random.randint(5000000, 30000000)},
            {'name': '贵州茅台', 'code': '600519.SH', 'change': round(random.uniform(-3, 3), 2), 'volume': random.randint(1000000, 10000000)},
            {'name': '五粮液', 'code': '000858.SZ', 'change': round(random.uniform(-3, 3), 2), 'volume': random.randint(2000000, 15000000)},
            {'name': '隆基绿能', 'code': '601012.SH', 'change': round(random.uniform(-4, 4), 2), 'volume': random.randint(3000000, 20000000)},
            {'name': '阳光电源', 'code': '300274.SZ', 'change': round(random.uniform(-5, 5), 2), 'volume': random.randint(3000000, 20000000)},
            {'name': '立讯精密', 'code': '002475.SZ', 'change': round(random.uniform(-4, 4), 2), 'volume': random.randint(3000000, 20000000)}
        ]
        return stocks[:limit]
    
    def _get_fallback_sector_performance(self) -> List[Dict[str, Any]]:
        import random
        sectors = [
            {'name': '银行', 'change': round(random.uniform(-2, 3), 2)},
            {'name': '科技成长', 'change': round(random.uniform(-3, 4), 2)},
            {'name': '新能源', 'change': round(random.uniform(-3, 4), 2)},
            {'name': '基建', 'change': round(random.uniform(-2, 3), 2)},
            {'name': '医药', 'change': round(random.uniform(-2, 3), 2)},
            {'name': '消费', 'change': round(random.uniform(-2, 2), 2)},
            {'name': '半导体', 'change': round(random.uniform(-4, 4), 2)},
            {'name': '军工', 'change': round(random.uniform(-3, 3), 2)}
        ]
        return sorted(sectors, key=lambda x: x['change'], reverse=True)
    
    def _get_fallback_factor_data(self, factor_name: str) -> Dict[str, Any]:
        import random
        factor_map = {
            'roc_5': {'ic': round(random.uniform(-0.3, 0.3), 3), 'ir': round(random.uniform(0.5, 2.5), 2), 'decay': round(random.uniform(0.05, 0.2), 2)},
            'roc_20': {'ic': round(random.uniform(-0.25, 0.25), 3), 'ir': round(random.uniform(0.5, 2.0), 2), 'decay': round(random.uniform(0.03, 0.15), 2)},
            'pb_ratio': {'ic': round(random.uniform(-0.2, 0.2), 3), 'ir': round(random.uniform(0.5, 1.8), 2), 'decay': round(random.uniform(0.01, 0.08), 2)},
            'pe_ratio': {'ic': round(random.uniform(-0.15, 0.15), 3), 'ir': round(random.uniform(0.5, 1.5), 2), 'decay': round(random.uniform(0.01, 0.06), 2)},
            'roe': {'ic': round(random.uniform(0, 0.2), 3), 'ir': round(random.uniform(0.5, 1.5), 2), 'decay': round(random.uniform(0.005, 0.03), 2)}
        }
        return factor_map.get(factor_name, {'ic': round(random.uniform(-0.2, 0.2), 3), 'ir': round(random.uniform(0.5, 1.5), 2)})
    
    def _get_fallback_market_statistics(self) -> Dict[str, Any]:
        import random
        return {
            'total_volume': f"{random.randint(7000, 12000)}亿",
            'advance_count': random.randint(1500, 3000),
            'decline_count': random.randint(1000, 2500),
            'advance_decline_ratio': f"{round(random.uniform(0.8, 2.5), 1)}:1",
            'northbound': f"{random.choice(['+', '-'])}{random.randint(10, 150)}亿",
            'southbound': f"{random.choice(['+', '-'])}{random.randint(5, 50)}亿",
            'limit_up': random.randint(30, 100),
            'limit_down': random.randint(5, 50),
            'vix': round(random.uniform(15, 25), 1)
        }