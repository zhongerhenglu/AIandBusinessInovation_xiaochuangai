from typing import Dict, Any
from datetime import datetime
import json
import os
import logging

logger = logging.getLogger(__name__)


class ExecutionLogger:
    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.logs = []
    
    def log(self, data: Dict[str, Any]):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            **data
        }
        self.logs.append(log_entry)
        
        log_file = os.path.join(self.log_dir, f"execution_{datetime.now().strftime('%Y%m%d')}.json")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        logger.info(f"Execution logged: {log_entry.get('decision', {}).get('action')}")
    
    def get_logs(self) -> list:
        return self.logs
    
    def get_logs_by_date(self, date: str) -> list:
        return [log for log in self.logs if date in log.get('timestamp', '')]