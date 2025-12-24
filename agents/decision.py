from agents.base_agent import BaseAgent
class DecisionAgent(BaseAgent):
    def decide(self, llm_output):
        self.send_message("Prise de décision")
        if "risque" in llm_output.lower():
            return "Maintenance préventive recommandée"
        return "Situation normale"
