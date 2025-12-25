from datetime import datetime
class BaseAgent:
    def __init__(self, name):
        self.name = name
        self.message_history = []
    
    def send_message(self, message, level="INFO"):
        msg = {
            "agent": self.name,
            "message": message,
            "level": level,
            "timestamp": datetime.now()
        }
        self.message_history.append(msg)
        print(f"[{level}][{self.name}] {message}")
    
    def get_history(self):
        return self.message_history