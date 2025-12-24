import pandas as pd
from agents.base_agent import BaseAgent

class DataCollectorAgent(BaseAgent):
    def load_data(self, path):
        self.send_message("Chargement des données industrielles")
        return pd.read_csv(path)
