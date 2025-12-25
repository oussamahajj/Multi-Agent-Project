"""
LLM Insight Agent - Generates expert insights using Gemini LLM
"""

import json
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class LLMInsightAgent(BaseAgent):
    """
    Agent that generates expert insights using Google's Gemini LLM.
    Provides intelligent analysis and recommendations based on data.
    """
    
    def __init__(self, name: str = "LLM Insights", api_key: str = None):
        super().__init__(name, role="AI Analysis Specialist")
        self.api_key = api_key
        self.client = None
        self.model_name = "gemini-2.5-flash"
        self.insights_history = []
        
        if GENAI_AVAILABLE and api_key:
            try:
                self.client = genai.Client(api_key=api_key)
                self.send_message("✅ Gemini LLM client initialized", "SUCCESS")
            except Exception as e:
                self.send_message(f"⚠️ Failed to initialize Gemini: {e}", "WARNING")
        elif not api_key:
            self.send_message("⚠️ No API key provided - will use fallback mode", "WARNING")
    
    def interpret(self, summary: Dict[str, Any], anomalies: Dict[str, Any], 
                  df=None, top_n: int = 10) -> Dict[str, Any]:
        """
        Generate expert insights based on analysis results.
        
        Args:
            summary: Analysis summary from AnalysisAgent
            anomalies: Detected anomalies from AnomalyDetectorAgent
            df: Optional DataFrame for detailed machine info
            top_n: Number of top machines to include in analysis
            
        Returns:
            Dictionary containing insights and recommendations
        """
        self.set_state("interpreting")
        self.send_message("🤖 Generating expert insights via LLM...")
        
        # Build the analysis prompt
        prompt = self._build_insight_prompt(summary, anomalies, df, top_n)
        
        try:
            if self.client:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                insight_text = response.text
                status = "success"
                self.send_message("✅ LLM insights generated successfully", "SUCCESS")
            else:
                insight_text = self._generate_fallback_insights(summary, anomalies)
                status = "fallback"
                self.send_message("⚠️ Using fallback insights (no LLM)", "WARNING")
            
            result = {
                "text": insight_text,
                "status": status,
                "model": self.model_name if status == "success" else "fallback"
            }
            
            self.insights_history.append(result)
            self.set_state("completed")
            self.update_shared_context("llm_insights", result)
            
            return result
            
        except Exception as e:
            self.send_message(f"❌ LLM error: {e}", "ERROR")
            fallback = self._generate_fallback_insights(summary, anomalies)
            return {
                "text": fallback,
                "status": "fallback",
                "error": str(e)
            }
    
    def _build_insight_prompt(self, summary: Dict, anomalies: Dict, 
                               df, top_n: int) -> str:
        """Build the prompt for LLM insight generation."""
        
        # Get critical machines info
        critical_machines = []
        if df is not None and 'Utilization_Rate' in df.columns:
            critical_df = df[df['Utilization_Rate'] < 0.4]
            cols = ['Machine_ID', 'Machine_Type']
            if 'Health_Score' in df.columns:
                cols.append('Health_Score')
            critical_machines = critical_df[cols].head(top_n).to_dict(orient='records')
        
        prompt = f"""Tu es un expert en pilotage industriel et maintenance prédictive. Analyse ces données de production et fournis des insights actionnables.

## DONNÉES DE PERFORMANCE

### KPI Globaux:
- Nombre total de machines: {summary.get('total_machines', 'N/A')}
- Taux d'utilisation moyen: {summary.get('avg_utilization', 0):.2%}
- Efficacité énergétique moyenne: {summary.get('avg_energy_efficiency', 'N/A'):.2f} kW/h
- Score de santé moyen: {summary.get('avg_health_score', 'N/A')}/100
- Machines critiques: {summary.get('critical_machine_count', 0)}/{summary.get('total_machines', 0)}

### Anomalies Détectées:
- 🌡️ Températures élevées: {len(anomalies.get('high_temperature', []))} machines
- 📳 Vibrations élevées: {len(anomalies.get('high_vibration', []))} machines
- ⚡ Pics énergétiques: {len(anomalies.get('energy_spikes', []))} machines
- 🔧 Machines à l'arrêt: {len(anomalies.get('zero_utilization', []))} machines
- 🔨 Maintenance en retard: {len(anomalies.get('maintenance_overdue', []))} machines

### Distribution des Risques:
{json.dumps(summary.get('risk_distribution', {}), indent=2, default=str)}

### Top {top_n} Machines Critiques:
"""
        
        if critical_machines:
            for m in critical_machines:
                health = m.get('Health_Score', 'N/A')
                prompt += f"- {m['Machine_ID']} ({m['Machine_Type']}) - Santé: {health}\n"
        else:
            prompt += "Aucune machine critique identifiée\n"
        
        prompt += """
## MISSION D'ANALYSE:

Fournis une analyse structurée avec:

### 1. DIAGNOSTIC GLOBAL (2-3 phrases)
Résume l'état général de la flotte de machines.

### 2. PROBLÈMES MAJEURS (3 problèmes prioritaires)
Pour chaque problème:
- Description du problème
- Impact estimé sur la production
- Machines concernées

### 3. ACTIONS RECOMMANDÉES (5 actions concrètes)
Pour chaque action:
- Action spécifique et mesurable
- Priorité (URGENTE/HAUTE/MOYENNE)
- Impact attendu (chiffré si possible)
- Délai de mise en œuvre

### 4. PRÉVISIONS ET RISQUES
- Risques à court terme (7 jours)
- Risques à moyen terme (30 jours)
- Indicateurs à surveiller

### 5. CONCLUSION
Synthèse en 2-3 phrases avec le message clé pour la direction.

Sois précis, actionnable et utilise des données chiffrées."""
        
        return prompt
    
    def _generate_fallback_insights(self, summary: Dict, anomalies: Dict) -> str:
        """Generate fallback insights when LLM is unavailable."""
        
        total = summary.get('total_machines', 0)
        critical = summary.get('critical_machine_count', 0)
        utilization = summary.get('avg_utilization', 0)
        health = summary.get('avg_health_score', 50)
        
        # Determine severity
        severity = "NORMAL"
        if critical > total * 0.3 or health < 50:
            severity = "CRITIQUE"
        elif critical > total * 0.15 or health < 70:
            severity = "ATTENTION REQUISE"
        
        insights = f"""
═══════════════════════════════════════════════════════════
         ANALYSE DE PERFORMANCE INDUSTRIELLE
                   (Mode Simplifié)
═══════════════════════════════════════════════════════════

📊 DIAGNOSTIC GLOBAL
--------------------
État du parc: {severity}
- {total} machines analysées
- {critical} machines en situation critique ({critical/total*100:.1f}% du parc)
- Taux d'utilisation moyen: {utilization:.1%}
- Score de santé moyen: {health:.1f}/100

🚨 PROBLÈMES IDENTIFIÉS
-----------------------
"""
        
        problems = []
        if len(anomalies.get('high_temperature', [])) > 0:
            problems.append(f"1. SURCHAUFFE: {len(anomalies['high_temperature'])} machines avec température anormale")
        if len(anomalies.get('high_vibration', [])) > 0:
            problems.append(f"2. VIBRATIONS: {len(anomalies['high_vibration'])} machines avec vibrations excessives")
        if len(anomalies.get('maintenance_overdue', [])) > 0:
            problems.append(f"3. MAINTENANCE: {len(anomalies['maintenance_overdue'])} machines en retard de maintenance")
        if len(anomalies.get('zero_utilization', [])) > 0:
            problems.append(f"4. ARRÊT: {len(anomalies['zero_utilization'])} machines à l'arrêt complet")
        
        if problems:
            insights += "\n".join(problems)
        else:
            insights += "Aucun problème majeur détecté."
        
        insights += f"""

⚡ ACTIONS RECOMMANDÉES
----------------------
1. [URGENTE] Inspecter immédiatement les machines avec anomalies thermiques
2. [HAUTE] Planifier la maintenance des {len(anomalies.get('maintenance_overdue', []))} machines en retard
3. [HAUTE] Diagnostiquer les machines avec vibrations anormales
4. [MOYENNE] Investiguer les causes des faibles taux d'utilisation
5. [MOYENNE] Mettre en place un monitoring renforcé

📈 INDICATEURS À SURVEILLER
---------------------------
• Évolution du taux d'utilisation (objectif: >70%)
• Nombre de machines critiques (objectif: <10%)
• Délai moyen de maintenance
• Consommation énergétique par machine

💡 CONCLUSION
-------------
Le parc nécessite une attention {"IMMÉDIATE" if severity == "CRITIQUE" else "soutenue"}.
Priorité: adresser les {critical} machines critiques pour restaurer la capacité de production.
Impact estimé: amélioration potentielle de {min(20, critical/total*50):.0f}% de la productivité.

═══════════════════════════════════════════════════════════
                    Rapport généré automatiquement
═══════════════════════════════════════════════════════════
"""
        
        return insights
    
    def ask_question(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ask a specific question about the data.
        
        Args:
            question: The question to ask
            context: Analysis context
            
        Returns:
            LLM response
        """
        self.send_message(f"❓ Processing question: {question[:50]}...")
        
        summary = context.get('summary', {})
        anomalies = context.get('anomalies', {})
        
        prompt = f"""Based on this industrial data:
- Total Machines: {summary.get('total_machines', 'N/A')}
- Average Utilization: {summary.get('avg_utilization', 0):.2%}
- Critical Machines: {summary.get('critical_machine_count', 0)}
- Temperature Anomalies: {len(anomalies.get('high_temperature', []))}
- Vibration Anomalies: {len(anomalies.get('high_vibration', []))}

Question: {question}

Provide a concise, data-driven answer."""
        
        try:
            if self.client:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                return {"answer": response.text, "status": "success"}
            else:
                return {"answer": "LLM not available. Please check API key.", "status": "error"}
        except Exception as e:
            return {"answer": f"Error: {str(e)}", "status": "error"}
