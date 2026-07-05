import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LLMConfig:
    default_model: str = "gpt-4o"
    api_keys: Dict[str, str] = field(default_factory=dict)
    temperature: float = 0.3
    max_tokens: int = 2000


@dataclass
class DataConfig:
    data_sources: List[str] = field(default_factory=lambda: ["ohlc", "news", "fundamental", "l2", "etf", "section"])
    cache_dir: str = "./data/cache"
    history_period: int = 252
    archive_dir: str = "./data/archive"
    section_output_dir: str = "./data/sections"
    max_workers: int = 4


@dataclass
class SectionConfig:
    winsorize_lower: float = 0.01
    winsorize_upper: float = 0.99
    factor_ic_period: int = 5
    standardize: bool = True
    include_zscore: bool = True
    include_rank: bool = True


@dataclass
class ArchiveConfig:
    max_versions: int = 3
    batch_size: int = 100
    validate_on_write: bool = True
    clean_up_duplicates: bool = True
    compression: str = "parquet"


@dataclass
class RiskConfig:
    max_position_per_stock: float = 0.1
    max_sector_exposure: float = 0.3
    max_daily_loss: float = 0.02
    max_drawdown: float = 0.15
    max_leverage: float = 1.5


@dataclass
class AgentConfig:
    agent_timeout: int = 300
    max_retries: int = 3
    logging_level: str = "INFO"


@dataclass
class SystemConfig:
    llm: LLMConfig = field(default_factory=LLMConfig)
    data: DataConfig = field(default_factory=DataConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    section: SectionConfig = field(default_factory=SectionConfig)
    archive: ArchiveConfig = field(default_factory=ArchiveConfig)
    output_dir: str = "./output"
    log_dir: str = "./logs"


def load_config() -> SystemConfig:
    config = SystemConfig()
    
    config.llm.api_keys = {
        "openai": os.getenv("OPENAI_API_KEY", ""),
        "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
        "kimi": os.getenv("KIMI_API_KEY", ""),
        "glm": os.getenv("GLM_API_KEY", "")
    }
    
    return config


CONFIG = load_config()