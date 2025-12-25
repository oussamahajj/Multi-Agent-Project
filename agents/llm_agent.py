from google import genai
from agents.base_agent import BaseAgent

class LLMInsightAgent(BaseAgent):
    def __init__(self, name="LLM Insights"):
        super().__init__(name)
        self.client = genai.Client()
    
    def interpret(self, summary, anomalies, df=None, top_n=10):
        self.send_message("Génération d'insights via LLM")
        
        # Machines critiques
        critical_machines = []
        if df is not None:
            critical_df = df[df['Utilization_Rate'] < 0.4]
            critical_machines = critical_df[['Machine_ID','Machine_Type']].head(top_n).to_dict(orient='records')
        
        # Prompt enrichi
        prompt = f"""
Tu es un expert en pilotage industriel. Analyse ces données:

KPI MOYENS:
- Utilisation: {summary['avg_utilization']:.2%}
- Efficacité énergétique: {summary['avg_energy_efficiency']:.2f} kW/h
- Stabilité: {summary['avg_stability']:.2f}
- Machines critiques: {summary['critical_machine_count']}/{summary['total_machines']}

ANOMALIES DÉTECTÉES:
- Température élevée: {len(anomalies['high_temperature'])} machines
- Vibrations élevées: {len(anomalies['high_vibration'])} machines
- Pics énergétiques: {len(anomalies['energy_spikes'])} machines

MACHINES CRITIQUES (top {top_n}):
"""
        if critical_machines:
            for m in critical_machines:
                prompt += f"- {m['Machine_ID']} ({m['Machine_Type']})\n"
        
        prompt += """
MISSION:
1. Identifie les 3 problèmes majeurs
2. Propose 3 actions concrètes et chiffrées
3. Estime l'impact potentiel sur la production
"""
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            self.send_message("✅ Insights LLM générés")
            return {
                "text": response.text,
                "status": "success"
            }
        except Exception as e:
            self.send_message(f"⚠️ Erreur LLM: {e}", "ERROR")
            return {
                "text": f"Analyse simplifiée: {summary['critical_machine_count']} machines nécessitent une attention urgente.",
                "status": "fallback"
            }

