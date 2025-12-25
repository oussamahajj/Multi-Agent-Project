from agents.base_agent import BaseAgent
from datetime import datetime

class ReportAgent(BaseAgent):
    def generate_report(self, summary, anomalies, llm_result, decisions, validation_history):
        """Génère un rapport complet avec traçabilité"""
        self.send_message("Génération du rapport final")
        
        report = f"""
╔═══════════════════════════════════════════════════════╗
║     RAPPORT DE PERFORMANCE INDUSTRIELLE               ║
║     Priorité: {decisions['priority']}                              ║
╚═══════════════════════════════════════════════════════╝

📊 KPI CLÉS
-----------
• Utilisation moyenne: {summary['avg_utilization']:.2%}
• Efficacité énergétique: {summary['avg_energy_efficiency']:.2f} kW/h
• Stabilité moyenne: {summary['avg_stability']:.2f}
• Machines totales: {summary['total_machines']}
• Machines critiques: {summary['critical_machine_count']}

🔍 ANOMALIES DÉTECTÉES
---------------------
• Températures élevées: {len(anomalies['high_temperature'])} machines
• Vibrations élevées: {len(anomalies['high_vibration'])} machines
• Pics énergétiques: {len(anomalies['energy_spikes'])} machines
• Machines à l'arrêt: {len(anomalies['zero_utilization'])}

🤖 ANALYSE EXPERTE (LLM)
-----------------------
{llm_result['text']}

⚡ DÉCISIONS RECOMMANDÉES
------------------------
"""
        for i, decision in enumerate(decisions['decisions'], 1):
            report += f"{i}. {decision}\n"
        
        report += f"""

🔄 TRAÇABILITÉ
-------------
Validations effectuées: {len(validation_history)}
"""
        for val in validation_history:
            status = "✅" if val['valid'] else "❌"
            report += f"{status} {val['agent']}: {val['message']}\n"
        
        report += f"""

{'='*60}
Rapport généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return report