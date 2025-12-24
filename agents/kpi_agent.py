from datetime import datetime
from agents.base_agent import BaseAgent
import numpy as np


class KPIAgent(BaseAgent):
    def compute_kpis(self, df):
        self.send_message("Calcul des KPI de production")

        current_year = datetime.now().year

        df['Machine_Age'] = current_year - df['Installation_Year']

        # Éviter divisions invalides
        df['Utilization_Rate'] = df['Operational_Hours'] / (24 * 365)

        df['Energy_Efficiency'] = np.where(
            df['Operational_Hours'] > 0,
            df['Power_Consumption_kW'] / df['Operational_Hours'],
            np.nan
        )

        df['Stability_Index'] = (
            df['Temperature_C'] +
            df['Vibration_mms'] +
            df['Sound_dB']
        ) / 3

        df['AI_Override_Rate'] = np.where(
            df['Operational_Hours'] > 0,
            df['AI_Override_Events'] / df['Operational_Hours'],
            0
        )

        return df
