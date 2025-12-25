from agents.base_agent import BaseAgent
class QualityControlAgent(BaseAgent):
    def validate_llm_output(self, llm_result, summary):
        """Vérifie la cohérence de l'analyse LLM"""
        self.send_message("Contrôle qualité de l'analyse LLM")
        
        text = llm_result["text"]
        issues = []
        
        # Vérifications basiques
        if len(text) < 100:
            issues.append("Réponse LLM trop courte")
        
        if llm_result["status"] == "fallback":
            issues.append("LLM en mode dégradé")
        
        # Vérifier cohérence avec les KPI
        if summary['critical_machine_count'] > 10 and "urgent" not in text.lower():
            issues.append("Sous-estimation de la criticité")
        
        if issues:
            self.send_message(f"⚠️ Problèmes détectés: {issues}", "WARNING")
            return {
                "valid": False,
                "issues": issues,
                "retry_needed": True
            }
        
        self.send_message("✅ Analyse LLM validée")
        return {
            "valid": True,
            "issues": [],
            "retry_needed": False
        }