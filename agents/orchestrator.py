from agents.base_agent import BaseAgent
from agents.data_collector import DataCollectorAgent
from agents.validation import ValidationAgent
from agents.preprocessing import PreprocessingAgent
from agents.kpi_agent import KPIAgent
from agents.analysis import AnalysisAgent
from agents.anomaly_detector import AnomalyDetectorAgent
from agents.llm_agent import LLMInsightAgent
from agents.quality_control import QualityControlAgent
from agents.decision import DecisionAgent
from agents.report import ReportAgent
from agents.final_validation import FinalValidationAgent
from agents.base_agent import BaseAgent


class SystemOrchestrator:
    def __init__(self):
        self.agents = {
            "collector": DataCollectorAgent("Collecteur"),
            "validator": ValidationAgent("Validateur"),
            "preprocessor": PreprocessingAgent("Prétraitement"),
            "kpi": KPIAgent("Agent KPI"),
            "analyzer": AnalysisAgent("Analyseur"),
            "anomaly": AnomalyDetectorAgent("Détecteur Anomalies"),
            "llm": LLMInsightAgent("LLM Insights"),
            "quality": QualityControlAgent("Contrôle Qualité"),
            "decision": DecisionAgent("Décisionnaire"),
            "reporter": ReportAgent("Rapporteur"),
            "final_validator": FinalValidationAgent("Validateur Final")
        }
        self.validation_history = []
        self.max_retries = 3
    
    def run_pipeline(self, data_path):
        """Exécute le pipeline avec boucles de validation"""
        print("\n" + "="*60)
        print("🚀 DÉMARRAGE DU SYSTÈME MULTI-AGENT")
        print("="*60 + "\n")
        
        # ÉTAPE 1: Chargement
        data_package = self.agents["collector"].load_data(data_path)
        
        # ÉTAPE 2: Validation brute
        validation1 = self.agents["validator"].validate_raw_data(data_package)
        self.validation_history.append({
            "agent": "Validator",
            "valid": validation1["valid"],
            "message": "Validation données brutes"
        })
        
        if not validation1["valid"]:
            return {"error": "Données brutes invalides", "issues": validation1["issues"]}
        
        # ÉTAPE 3: Preprocessing
        cleaned_package = self.agents["preprocessor"].clean_data(validation1)
        
        # ÉTAPE 4: Revalidation post-nettoyage
        validation2 = self.agents["validator"].validate_processed_data(cleaned_package["data"])
        self.validation_history.append({
            "agent": "Validator",
            "valid": validation2["valid"],
            "message": "Validation post-traitement"
        })
        
        if not validation2["valid"]:
            print("⚠️ Retraitement nécessaire...")
            # Ici on pourrait implémenter une boucle de retraitement
        
        # ÉTAPE 5: KPI
        df = self.agents["kpi"].compute_kpis(validation2["data"])
        
        # ÉTAPE 6: Analyse
        summary = self.agents["analyzer"].analyze(df)
        
        # ÉTAPE 7: Détection anomalies
        anomalies = self.agents["anomaly"].detect_anomalies(df, summary)
        
        # ÉTAPE 8-9: LLM avec boucle de retry
        retry_count = 0
        llm_result = None
        qc_result = None
        
        while retry_count < self.max_retries:
            llm_result = self.agents["llm"].interpret(summary, anomalies, df)
            qc_result = self.agents["quality"].validate_llm_output(llm_result, summary)
            
            self.validation_history.append({
                "agent": "QualityControl",
                "valid": qc_result["valid"],
                "message": f"Validation LLM (tentative {retry_count + 1})"
            })
            
            if qc_result["valid"] or not qc_result["retry_needed"]:
                break
            
            retry_count += 1
            print(f"🔄 Retry LLM {retry_count}/{self.max_retries}")
        
        # ÉTAPE 10: Décisions
        decisions = self.agents["decision"].decide(summary, anomalies, llm_result, qc_result)
        
        # ÉTAPE 11: Rapport
        report = self.agents["reporter"].generate_report(
            summary, anomalies, llm_result, decisions, self.validation_history
        )
        
        # ÉTAPE 12: Validation finale avec boucle
        final_retry = 0
        while final_retry < self.max_retries:
            final_validation = self.agents["final_validator"].validate_report(report, decisions)
            
            self.validation_history.append({
                "agent": "FinalValidator",
                "valid": final_validation["valid"],
                "message": f"Validation finale (tentative {final_retry + 1})"
            })
            
            if final_validation["valid"]:
                break
            
            final_retry += 1
            print(f"🔄 Correction rapport {final_retry}/{self.max_retries}")
            # Ici on pourrait régénérer le rapport
        
        print("\n" + "="*60)
        print("✅ PIPELINE TERMINÉ")
        print("="*60 + "\n")
        
        return {
            "report": report,
            "summary": summary,
            "anomalies": anomalies,
            "decisions": decisions,
            "df": df,
            "validation_history": self.validation_history
        }