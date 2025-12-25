"""
Multi-Agent System for Industrial Machine Monitoring
Agent Package - Contains all specialized agents for the system
"""

from agents.base_agent import BaseAgent
from agents.data_collector import DataCollectorAgent
from agents.validation import ValidationAgent
from agents.preprocessing import PreprocessingAgent
from agents.kpi_agent import KPIAgent
from agents.analysis import AnalysisAgent
from agents.anomaly_detector import AnomalyDetectorAgent
from agents.reasoning_agent import ReasoningAgent
from agents.debate_agent import DebateAgent
from agents.planning_agent import PlanningAgent
from agents.llm_agent import LLMInsightAgent
from agents.quality_control import QualityControlAgent
from agents.decision import DecisionAgent
from agents.report import ReportAgent
from agents.final_validation import FinalValidationAgent

__all__ = [
    'BaseAgent',
    'DataCollectorAgent',
    'ValidationAgent',
    'PreprocessingAgent',
    'KPIAgent',
    'AnalysisAgent',
    'AnomalyDetectorAgent',
    'ReasoningAgent',
    'DebateAgent',
    'PlanningAgent',
    'LLMInsightAgent',
    'QualityControlAgent',
    'DecisionAgent',
    'ReportAgent',
    'FinalValidationAgent'
]
