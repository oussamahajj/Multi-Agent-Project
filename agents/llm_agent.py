'''from google import genai





class LLMInsightAgent:
    def __init__(self):
        # Initialisation du client Gemini
        self.client = genai.Client()

    def interpret(self, summary):
        prompt = f"""
Tu es un expert en pilotage de production industrielle.

Voici les KPI calculés :
{summary}

1. Analyse la performance globale de la production.
2. Identifie les dérives ou déséquilibres.
3. Propose des actions d’optimisation.
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text
'''

from google import genai

class LLMInsightAgent:
    def __init__(self):
        # Initialisation du client Gemini
        self.client = genai.Client()

    def interpret(self, summary, df=None, top_n=10):
        """
        summary : dictionnaire avec KPI agrégés
        df : DataFrame complet (optionnel), utilisé pour machines critiques
        top_n : nombre maximum de machines individuelles à inclure dans le prompt
        """

        # 1️⃣ Sélection des machines critiques si df fourni
        critical_machines = []
        if df is not None:
            critical_machines_df = df[df['Utilization_Rate'] < 0.4]
            critical_machines = critical_machines_df[['Machine_ID','Machine_Type']].head(top_n).to_dict(orient='records')

        # 2️⃣ Générer un prompt compact
        prompt = f"""
Tu es un expert en pilotage industriel. Voici un résumé des KPI :

KPI moyens :
- Utilisation moyenne : {summary.get('avg_utilization', 'N/A')}
- Energie moyenne : {summary.get('avg_energy_efficiency', 'N/A')}
- Stabilité moyenne : {summary.get('avg_stability', 'N/A')}

Machines critiques (top {top_n}) :
"""
        if critical_machines:
            for m in critical_machines:
                prompt += f"- {m['Machine_ID']} ({m['Machine_Type']})\n"
        else:
            prompt += "Aucune machine critique détectée.\n"

        prompt += "\nAnalyse la performance globale et propose des actions d'optimisation concises."

        # 3️⃣ Appel Gemini avec gestion d'erreur
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            # Fallback si quota dépassé
            print("⚠️ Erreur Gemini, retour fallback :", e)
            return "LLM non disponible, résumé simple : " + str(summary)
