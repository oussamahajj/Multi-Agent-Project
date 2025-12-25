from agents.base_agent import BaseAgent
class DecisionAgent(BaseAgent):
    def decide(self, summary, anomalies, llm_result, qc_result):
        """Prend des décisions basées sur toutes les analyses"""
        self.send_message("Prise de décision stratégique")
        
        decisions = []
        priority = "NORMAL"
        
        # Décisions basées sur KPI
        if summary['critical_machine_count'] > summary['total_machines'] * 0.3:
            decisions.append("⚠️ MAINTENANCE MASSIVE requise (>30% machines critiques)")
            priority = "URGENT"
        
        # Décisions basées sur anomalies
        if len(anomalies['high_temperature']) > 5:
            decisions.append("🌡️ Refroidissement urgent nécessaire")
            priority = "URGENT"
        
        if len(anomalies['zero_utilization']) > 0:
            decisions.append("🔧 Vérifier machines à l'arrêt")
        
        # Décisions basées sur LLM
        if not qc_result['valid']:
            decisions.append("⚠️ Analyse LLM nécessite révision")
        
        if "risque" in llm_result["text"].lower():
            decisions.append("📊 Audit approfondi recommandé")
        
        self.send_message(f"Priorité: {priority} | {len(decisions)} décisions")
        
        return {
            "priority": priority,
            "decisions": decisions,
            "action_needed": priority == "URGENT"
        }
