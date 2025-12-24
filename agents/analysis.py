from agents.base_agent import BaseAgent




    

class AnalysisAgent(BaseAgent):
    def analyze(self, df):
        self.send_message("Analyse des KPI de production")

        summary = {
            "avg_utilization": round(df['Utilization_Rate'].mean(), 3),
            "avg_energy_efficiency": round(df['Energy_Efficiency'].mean(), 3),
            "avg_stability": round(df['Stability_Index'].mean(), 2),
            "machines_sous_utilisees": df[df['Utilization_Rate'] < 0.4]['Machine_ID'].tolist(),
            "machines_instables": df[df['Stability_Index'] > df['Stability_Index'].mean()]['Machine_ID'].tolist()
        }

        return summary

