"""
Configuration Management for Multi-Agent Industrial Monitoring System
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class LLMConfig:
    """Configuration for LLM (Gemini) integration"""
    api_key: Optional[str] = None
    model_name: str = "gemini-2.5-flash"
    max_tokens: int = 2048
    temperature: float = 0.7
    timeout: int = 30
    
    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.environ.get("GEMINI_API_KEY", "")


@dataclass
class ValidationConfig:
    """Configuration for data validation thresholds"""
    min_rows: int = 10
    max_null_percentage: float = 0.5
    required_columns: list = field(default_factory=lambda: [
        "Machine_ID", "Machine_Type", "Temperature_C", 
        "Vibration_mms", "Power_Consumption_kW"
    ])
    value_ranges: Dict[str, tuple] = field(default_factory=lambda: {
        "Temperature_C": (0, 150),
        "Vibration_mms": (0, 50),
        "Sound_dB": (0, 150),
        "Oil_Level_pct": (0, 100),
        "Coolant_Level_pct": (0, 100),
        "Power_Consumption_kW": (0, 1000)
    })


@dataclass
class AnomalyConfig:
    """Configuration for anomaly detection"""
    percentile_high: float = 0.95
    percentile_low: float = 0.05
    z_score_threshold: float = 3.0
    maintenance_overdue_days: int = 90
    maintenance_critical_days: int = 180
    low_utilization_threshold: float = 0.20
    high_error_rate_threshold: int = 5


@dataclass
class DecisionConfig:
    """Configuration for decision making thresholds"""
    critical_machine_ratio: float = 0.30
    high_temp_count: int = 5
    maintenance_overdue_ratio: float = 0.20
    low_health_threshold: float = 50.0
    min_utilization: float = 0.40


@dataclass
class UIConfig:
    """Configuration for Streamlit UI"""
    page_title: str = "🏭 Système Multi-Agent Industriel"
    page_icon: str = "🏭"
    layout: str = "wide"
    theme_primary_color: str = "#1f77b4"
    theme_secondary_color: str = "#ff7f0e"
    sidebar_state: str = "expanded"


@dataclass 
class SystemConfig:
    """Main system configuration aggregating all configs"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    anomaly: AnomalyConfig = field(default_factory=AnomalyConfig)
    decision: DecisionConfig = field(default_factory=DecisionConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    
    # Feature flags
    enable_reasoning: bool = True
    enable_debate: bool = True
    enable_planning: bool = True
    enable_advanced_viz: bool = True
    
    # Performance settings
    max_concurrent_agents: int = 5
    cache_results: bool = True
    verbose_logging: bool = True


def load_config() -> SystemConfig:
    """Load configuration with environment variable overrides"""
    config = SystemConfig()
    
    # Override with environment variables if present
    if os.environ.get("GEMINI_API_KEY"):
        config.llm.api_key = os.environ["GEMINI_API_KEY"]
    
    if os.environ.get("DEBUG"):
        config.verbose_logging = True
    
    return config


# Global configuration instance
CONFIG = load_config()
