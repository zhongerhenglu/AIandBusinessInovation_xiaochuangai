from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class PositionManager:
    def __init__(self):
        self.positions = {}
    
    def calculate(self, decision: Dict[str, Any], max_position: float) -> Dict[str, Any]:
        action = decision.get('action', 'HOLD')
        if action == 'HOLD':
            return {}
        
        return {
            'symbol': decision.get('symbol', 'AAPL'),
            'action': action,
            'size': min(decision.get('position_size', 0.1), max_position),
            'stop_loss': decision.get('stop_loss', 0.05),
            'take_profit': decision.get('take_profit', 0.15)
        }
    
    def update(self, order_result: Dict[str, Any]):
        symbol = order_result.get('symbol')
        if symbol:
            self.positions[symbol] = {
                'size': order_result.get('filled_size', 0),
                'avg_price': order_result.get('avg_price', 0),
                'side': order_result.get('side', '')
            }
            logger.info(f"Position updated: {symbol} - {self.positions[symbol]}")
    
    def get_positions(self) -> Dict[str, Any]:
        return self.positions
    
    def get_position(self, symbol: str) -> Dict[str, Any]:
        return self.positions.get(symbol, {})