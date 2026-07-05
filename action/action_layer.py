from typing import Dict, Any
from .risk_manager import RiskManager
from .position_manager import PositionManager
from .execution_logger import ExecutionLogger
import logging

logger = logging.getLogger(__name__)


class MockBrokerAPI:
    def place_order(self, position: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Placing order: {position}")
        return {
            'order_id': 'ORD-' + str(hash(str(position))),
            'symbol': position.get('symbol'),
            'side': position.get('action'),
            'filled_size': position.get('size'),
            'avg_price': 100.0,
            'status': 'filled'
        }


class ActionLayer:
    def __init__(self):
        self.broker_api = MockBrokerAPI()
        self.risk_manager = RiskManager()
        self.position_manager = PositionManager()
        self.execution_logger = ExecutionLogger()
    
    def execute(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        risk_result = self.risk_manager.check(decision)
        if not risk_result['approved']:
            return {'status': 'rejected', 'reason': risk_result['reason']}
        
        position = self.position_manager.calculate(
            decision, 
            risk_result['max_position']
        )
        
        if not position:
            return {'status': 'no_action', 'reason': 'HOLD decision'}
        
        order_result = self.broker_api.place_order(position)
        self.position_manager.update(order_result)
        
        self.execution_logger.log({
            'decision': decision,
            'risk_check': risk_result,
            'position': position,
            'order_result': order_result,
            'timestamp': datetime.now().isoformat()
        })
        
        return order_result