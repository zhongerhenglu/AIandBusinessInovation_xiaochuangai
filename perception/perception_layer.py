from typing import Dict, Any
from .data_providers import (
    OHLCDataProvider, NewsDataProvider, FundamentalDataProvider,
    OnChainDataProvider, SentimentDataProvider
)
from .feature_engine import FeatureEngine
from .vector_store import VectorStore
import logging

logger = logging.getLogger(__name__)


class PerceptionLayer:
    def __init__(self):
        self.data_providers = {
            'ohlc': OHLCDataProvider(),
            'news': NewsDataProvider(),
            'fundamental': FundamentalDataProvider(),
            'onchain': OnChainDataProvider(),
            'sentiment': SentimentDataProvider()
        }
        self.feature_engine = FeatureEngine()
        self.vector_store = VectorStore()
    
    def collect_state(self, timestamp) -> Dict[str, Any]:
        state = {}
        for provider_name, provider in self.data_providers.items():
            try:
                state[provider_name] = provider.fetch(timestamp)
            except Exception as e:
                logger.error(f"Error fetching data from {provider_name}: {e}")
        
        return self.normalize(state)
    
    def normalize(self, raw_state: Dict[str, Any]) -> Dict[str, Any]:
        features = self.feature_engine.extract(raw_state)
        text_description = self.feature_engine.generate_text(raw_state)
        embedding = self.vector_store.encode(text_description)
        
        return {
            'features': features,
            'text': text_description,
            'embedding': embedding,
            'raw': raw_state
        }