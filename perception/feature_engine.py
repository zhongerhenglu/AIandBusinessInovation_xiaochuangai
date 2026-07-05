import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class FeatureEngine:
    def __init__(self):
        self.technical_indicators = ["ma", "rsi", "macd", "bollinger", "kdj", "atr", "cci"]
        self.statistical_features = ["volatility", "skewness", "kurtosis", "autocorrelation"]
    
    def extract(self, raw_state: Dict[str, Any]) -> Dict[str, Any]:
        features = {}
        
        if "ohlc" in raw_state:
            features["technical"] = self._calculate_technical(raw_state["ohlc"])
            features["statistical"] = self._calculate_statistical(raw_state["ohlc"])
        
        if "news" in raw_state:
            features["sentiment"] = self._analyze_sentiment(raw_state["news"])
        
        if "fundamental" in raw_state:
            features["fundamental"] = self._extract_fundamental(raw_state["fundamental"])
        
        return features
    
    def _calculate_technical(self, ohlc_data: Dict[str, Any]) -> Dict[str, Any]:
        indicators = {}
        for symbol, data in ohlc_data.items():
            df = pd.DataFrame([data])
            indicators[symbol] = {}
            indicators[symbol]["ma"] = df["close"].mean()
            indicators[symbol]["rsi"] = self._compute_rsi(df["close"])
            indicators[symbol]["macd"] = self._compute_macd(df)
            indicators[symbol]["bollinger"] = self._compute_bollinger(df)
        return indicators
    
    def _compute_rsi(self, prices: pd.Series, period: int = 14) -> float:
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if not rsi.empty else 50.0
    
    def _compute_macd(self, df: pd.DataFrame) -> float:
        ema12 = df["close"].ewm(span=12).mean()
        ema26 = df["close"].ewm(span=26).mean()
        macd = ema12 - ema26
        return float(macd.iloc[-1]) if not macd.empty else 0.0
    
    def _compute_bollinger(self, df: pd.DataFrame, period: int = 20) -> Dict[str, float]:
        sma = df["close"].rolling(window=period).mean()
        std = df["close"].rolling(window=period).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        return {
            "upper": float(upper_band.iloc[-1]) if not upper_band.empty else 0.0,
            "middle": float(sma.iloc[-1]) if not sma.empty else 0.0,
            "lower": float(lower_band.iloc[-1]) if not lower_band.empty else 0.0
        }
    
    def _calculate_statistical(self, ohlc_data: Dict[str, Any]) -> Dict[str, Any]:
        stats = {}
        for symbol, data in ohlc_data.items():
            returns = np.log(data["close"] / data["open"])
            stats[symbol] = {
                "volatility": np.std(returns),
                "skewness": 0.0,
                "kurtosis": 0.0,
                "autocorrelation": 0.0
            }
        return stats
    
    def _analyze_sentiment(self, news_data: Dict[str, Any]) -> Dict[str, float]:
        news_items = news_data.get("news", [])
        if not news_items:
            return {"overall": 0.0}
        
        avg_sentiment = np.mean([item.get("sentiment", 0) for item in news_items])
        return {"overall": avg_sentiment, "count": len(news_items)}
    
    def _extract_fundamental(self, fundamental_data: Dict[str, Any]) -> Dict[str, Any]:
        return fundamental_data
    
    def generate_text(self, raw_state: Dict[str, Any]) -> str:
        text_parts = []
        
        if "ohlc" in raw_state:
            for symbol, data in raw_state["ohlc"].items():
                text_parts.append(f"{symbol}: close={data['close']:.2f}, volume={data['volume']:,}")
        
        if "news" in raw_state:
            news_items = raw_state["news"].get("news", [])
            if news_items:
                text_parts.append(f"News count: {len(news_items)}, sentiment: {news_items[0].get('sentiment', 0):.2f}")
        
        return "; ".join(text_parts)