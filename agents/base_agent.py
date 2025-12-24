class BaseAgent:
    def __init__(self, name):
        self.name = name

    def send_message(self, message):
        print(f"[{self.name}] {message}")