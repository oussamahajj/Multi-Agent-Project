from agents.base_agent import BaseAgent
class FinalValidationAgent(BaseAgent):
    def validate_report(self, report, decisions):
        """Validation finale avant publication"""
        self.send_message("Validation finale du rapport")
        
        issues = []
        
        # Vérifier complétude
        required_sections = ["KPI CLÉS", "ANOMALIES", "DÉCISIONS", "TRAÇABILITÉ"]
        for section in required_sections:
            if section not in report:
                issues.append(f"Section manquante: {section}")
        
        # Vérifier cohérence décisions
        if decisions['action_needed'] and len(decisions['decisions']) == 0:
            issues.append("Actions urgentes requises mais aucune décision")
        
        if issues:
            self.send_message(f"❌ Validation finale échouée: {issues}", "ERROR")
            return {"valid": False, "issues": issues}
        
        self.send_message("✅ Rapport validé et prêt pour publication")
        return {"valid": True, "issues": []}
