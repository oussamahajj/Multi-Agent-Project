from agents.base_agent import BaseAgent
'''class ReportAgent(BaseAgent):
    def generate_report(self, decision, explanation):
        report = f"""
        RAPPORT INDUSTRIEL
        -------------------
        Décision : {decision}

        Explication :
        {explanation}
        """
        return report
'''


class ReportAgent(BaseAgent):
    def generate_report(self, summary, llm_text):

        return f"""
RAPPORT DE PERFORMANCE INDUSTRIELLE
=================================

KPI clés :
{summary}

Analyse experte :
{llm_text}

Conclusion :
La production peut être optimisée via un meilleur équilibrage des charges et une réduction
des dérives énergétiques et opérationnelles.
"""
