"""
Base Agent Class - Foundation for all agents in the multi-agent system
Implements core agent functionality: messaging, history tracking, and inter-agent communication
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import json


class BaseAgent:
    """
    Base class for all agents in the multi-agent system.
    Provides common functionality for communication, logging, and state management.
    """
    
    def __init__(self, name: str, role: str = "Generic Agent"):
        self.name = name
        self.role = role
        self.message_history: List[Dict] = []
        self.shared_context: Dict[str, Any] = {}
        self.state = "idle"
        self.created_at = datetime.now()
        
    def send_message(self, message: str, level: str = "INFO", target_agent: str = None) -> Dict:
        """
        Send a message and log it to history.
        
        Args:
            message: The message content
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            target_agent: Optional target agent for directed communication
        """
        msg = {
            "agent": self.name,
            "role": self.role,
            "message": message,
            "level": level,
            "target": target_agent,
            "timestamp": datetime.now().isoformat(),
            "state": self.state
        }
        self.message_history.append(msg)
        
        # Console logging with color coding
        level_colors = {
            "INFO": "\033[94m",    # Blue
            "WARNING": "\033[93m", # Yellow
            "ERROR": "\033[91m",   # Red
            "DEBUG": "\033[92m",   # Green
            "SUCCESS": "\033[96m"  # Cyan
        }
        color = level_colors.get(level, "\033[0m")
        reset = "\033[0m"
        
        target_str = f" → {target_agent}" if target_agent else ""
        print(f"{color}[{level}][{self.name}]{target_str}{reset} {message}")
        
        return msg
    
    def receive_message(self, message: Dict) -> None:
        """Process an incoming message from another agent."""
        self.message_history.append({
            **message,
            "received_at": datetime.now().isoformat(),
            "received_by": self.name
        })
    
    def update_shared_context(self, key: str, value: Any) -> None:
        """Update the shared context that can be accessed by other agents."""
        self.shared_context[key] = {
            "value": value,
            "updated_by": self.name,
            "updated_at": datetime.now().isoformat()
        }
    
    def get_from_context(self, key: str) -> Optional[Any]:
        """Retrieve a value from shared context."""
        if key in self.shared_context:
            return self.shared_context[key]["value"]
        return None
    
    def set_state(self, new_state: str) -> None:
        """Update agent state and log the transition."""
        old_state = self.state
        self.state = new_state
        self.send_message(f"State transition: {old_state} → {new_state}", "DEBUG")
    
    def get_history(self) -> List[Dict]:
        """Return the complete message history."""
        return self.message_history
    
    def get_recent_history(self, n: int = 10) -> List[Dict]:
        """Return the n most recent messages."""
        return self.message_history[-n:]
    
    def summarize_activity(self) -> Dict:
        """Generate a summary of the agent's activity."""
        return {
            "agent_name": self.name,
            "role": self.role,
            "current_state": self.state,
            "total_messages": len(self.message_history),
            "created_at": self.created_at.isoformat(),
            "context_keys": list(self.shared_context.keys())
        }
    
    def to_dict(self) -> Dict:
        """Serialize agent state to dictionary."""
        return {
            "name": self.name,
            "role": self.role,
            "state": self.state,
            "message_count": len(self.message_history),
            "context": self.shared_context
        }
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', role='{self.role}', state='{self.state}')>"
