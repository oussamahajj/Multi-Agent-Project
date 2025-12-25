from agents.base_agent import BaseAgent
class AnomalyDetectorAgent(BaseAgent):
    def detect_anomalies(self, df, summary):
        """Détecte les anomalies statistiques"""
        self.send_message("Détection des anomalies")
        
        anomalies = {
            "high_temperature": df[df['Temperature_C'] > df['Temperature_C'].quantile(0.95)]['Machine_ID'].tolist(),
            "high_vibration": df[df['Vibration_mms'] > df['Vibration_mms'].quantile(0.95)]['Machine_ID'].tolist(),
            "energy_spikes": df[df['Energy_Efficiency'] > df['Energy_Efficiency'].quantile(0.95)]['Machine_ID'].tolist(),
            "zero_utilization": df[df['Utilization_Rate'] == 0]['Machine_ID'].tolist()
        }
        
        total_anomalies = sum(len(v) for v in anomalies.values())
        self.send_message(f"🔍 {total_anomalies} anomalies détectées")
        
        return anomalies