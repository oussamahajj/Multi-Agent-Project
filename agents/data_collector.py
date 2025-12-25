import pandas as pd
from agents.base_agent import BaseAgent
from datetime import datetime

class DataCollectorAgent(BaseAgent):
    def load_data(self, path):
        self.send_message("Chargement des données industrielles")
        df = pd.read_csv(path)
        
        return {
            "data": df,
            "status": "loaded",
            "row_count": len(df),
            "columns": list(df.columns)
        }