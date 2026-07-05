from datetime import datetime
from typing import Optional


def get_timestamp() -> str:
    return datetime.now().isoformat()


def parse_time(time_str: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(time_str)
    except ValueError:
        return None