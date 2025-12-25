"""
System Orchestrator - Central coordinator for the Multi-Agent System
Manages workflow, agent communication, feedback loops, and reasoning integration.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class SystemOrchestrator:
    """
    Central orchestrator that coordinates all agents in the multi-agent system.
    Implements feedback loops, validation chains, and reasoning integration.
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the orchestrator with all agents."""
        self.api_key = api_key
        self.validation_history = []
        self.agent_messages = []
        self.max_retries = 3
        self.pipeline_status = "idle"
        
        # Import and initialize all agents
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
        from agents.reasoning_agent import ReasoningAgent
        from agents.debate_agent import DebateAgent
        from agents.planning_agent import PlanningAgent
        
        # Initialize base agents
        self.agents = {
            "collector": DataCollectorAgent("DataCollector"),
            "validator": ValidationAgent("Validator"),
            "preprocessor": PreprocessingAgent("Preprocessor"),
            "kpi": KPIAgent("KPIAgent"),
            "analyzer": AnalysisAgent("Analyzer"),
            "anomaly": AnomalyDetectorAgent("AnomalyDetector"),
            "llm": LLMInsightAgent("LLMInsight", api_key=api_key),
            "quality": QualityControlAgent("QualityControl"),
            "decision": DecisionAgent("DecisionMaker"),
            "reporter": ReportAgent("Reporter"),
            "final_validator": FinalValidationAgent("FinalValidator"),
        }
        
        # Initialize reasoning agents
        self.reasoning_agents = {
            "reasoning": ReasoningAgent("ChainOfThought", api_key=api_key),
            "debate": DebateAgent("DebateAgent", api_key=api_key),
            "planning": PlanningAgent("PlanningAgent", api_key=api_key),
        }
        
        self._log("🚀 System Orchestrator initialized with all agents", "SUCCESS")
    
    def _log(self, message: str, level: str = "INFO"):
        """Log orchestrator messages."""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "agent": "Orchestrator",
            "message": message,
            "level": level
        }
        self.agent_messages.append(log_entry)
        print(f"[{level}][Orchestrator] {message}")
    
    def _record_validation(self, agent: str, valid: bool, message: str, details: Dict = None):
        """Record validation result for traceability."""
        self.validation_history.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "valid": valid,
            "message": message,
            "details": details or {}
        })
    
    def run_pipeline(self, data_source, enable_reasoning: bool = True, 
                     enable_debate: bool = True, enable_planning: bool = True,
                     progress_callback=None) -> Dict[str, Any]:
        """
        Execute the full multi-agent pipeline.
        
        Args:
            data_source: Path to CSV file or pandas DataFrame
            enable_reasoning: Enable Chain-of-Thought reasoning
            enable_debate: Enable multi-perspective debate
            enable_planning: Enable strategic planning
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary containing all analysis results
        """
        self.pipeline_status = "running"
        self.validation_history = []
        self.agent_messages = []
        
        results = {
            "status": "running",
            "stages_completed": [],
            "errors": [],
            "timestamp": datetime.now().isoformat()
        }
        
        def update_progress(stage: str, progress: int, message: str):
            if progress_callback:
                progress_callback(stage, progress, message)
            self._log(f"[{progress}%] {stage}: {message}")
        
        try:
            # ═══════════════════════════════════════════════════════════════
            # STAGE 1: DATA COLLECTION
            # ═══════════════════════════════════════════════════════════════
            update_progress("Data Collection", 5, "Loading data...")
            
            if isinstance(data_source, str):
                data_package = self.agents["collector"].load_data(data_source)
            else:
                data_package = self.agents["collector"].load_from_dataframe(data_source)
            
            results["data_profile"] = data_package.get("profile", {})
            results["row_count"] = data_package.get("row_count", 0)
            results["columns"] = data_package.get("columns", [])
            results["stages_completed"].append("data_collection")
            
            self._record_validation("DataCollector", True, 
                                   f"Loaded {data_package['row_count']} rows")
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 2: DATA VALIDATION (RAW)
            # ═══════════════════════════════════════════════════════════════
            update_progress("Validation", 10, "Validating raw data...")
            
            validation1 = self.agents["validator"].validate_raw_data(data_package)
            self._record_validation("Validator", validation1["valid"],
                                   "Raw data validation", 
                                   {"issues": validation1.get("issues", [])})
            
            if not validation1["valid"]:
                results["status"] = "failed"
                results["errors"].append({
                    "stage": "validation",
                    "issues": validation1["issues"]
                })
                return results
            
            results["stages_completed"].append("raw_validation")
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 3: PREPROCESSING
            # ═══════════════════════════════════════════════════════════════
            update_progress("Preprocessing", 20, "Cleaning and transforming data...")
            
            cleaned_package = self.agents["preprocessor"].clean_data(validation1)
            results["cleaning_report"] = cleaned_package.get("cleaning_report", {})
            results["stages_completed"].append("preprocessing")
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 4: POST-PROCESSING VALIDATION
            # ═══════════════════════════════════════════════════════════════
            update_progress("Validation", 25, "Validating processed data...")
            
            validation2 = self.agents["validator"].validate_processed_data(
                cleaned_package["data"]
            )
            self._record_validation("Validator", validation2["valid"],
                                   "Post-processing validation",
                                   {"issues": validation2.get("issues", [])})
            
            if not validation2["valid"]:
                self._log("⚠️ Post-processing validation warnings", "WARNING")
            
            results["stages_completed"].append("post_validation")
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 5: KPI CALCULATION
            # ═══════════════════════════════════════════════════════════════
            update_progress("KPI Calculation", 35, "Computing KPIs...")
            
            df = self.agents["kpi"].compute_kpis(validation2["data"])
            results["kpi_summary"] = self.agents["kpi"].get_kpi_summary(df)
            results["stages_completed"].append("kpi_calculation")
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 6: ANALYSIS
            # ═══════════════════════════════════════════════════════════════
            update_progress("Analysis", 45, "Analyzing patterns...")
            
            summary = self.agents["analyzer"].analyze(df)
            results["summary"] = summary
            results["stages_completed"].append("analysis")
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 7: ANOMALY DETECTION
            # ═══════════════════════════════════════════════════════════════
            update_progress("Anomaly Detection", 50, "Detecting anomalies...")
            
            anomalies = self.agents["anomaly"].detect_anomalies(df)
            results["anomalies"] = anomalies
            results["anomaly_count"] = sum(len(v) for v in anomalies.values())
            results["priority_list"] = self.agents["anomaly"].get_priority_list(anomalies)
            results["stages_completed"].append("anomaly_detection")
            
            # Build context for reasoning agents
            context = {
                "summary": summary,
                "anomalies": anomalies,
                "df": df,
                "kpi_summary": results.get("kpi_summary", {}),
            }
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 8: CHAIN-OF-THOUGHT REASONING
            # ═══════════════════════════════════════════════════════════════
            if enable_reasoning:
                update_progress("Reasoning", 55, "Applying Chain-of-Thought reasoning...")
                
                reasoning_result = self.reasoning_agents["reasoning"].reason(
                    context,
                    "What are the critical issues in this industrial facility and what are the root causes?"
                )
                results["reasoning"] = reasoning_result
                context["reasoning"] = reasoning_result
                results["stages_completed"].append("reasoning")
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 9: MULTI-PERSPECTIVE DEBATE
            # ═══════════════════════════════════════════════════════════════
            if enable_debate:
                update_progress("Debate", 60, "Conducting expert debate...")
                
                debate_result = self.reasoning_agents["debate"].conduct_debate(
                    context,
                    "What should be the priority actions to improve facility performance?",
                    rounds=2
                )
                results["debate"] = debate_result
                context["debate"] = debate_result
                results["stages_completed"].append("debate")
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 10: STRATEGIC PLANNING
            # ═══════════════════════════════════════════════════════════════
            if enable_planning:
                update_progress("Planning", 65, "Creating action plan...")
                
                plan_result = self.reasoning_agents["planning"].create_action_plan(
                    context,
                    "Optimize facility performance and reduce critical machine count"
                )
                results["action_plan"] = plan_result
                context["action_plan"] = plan_result
                results["stages_completed"].append("planning")
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 11: LLM INSIGHTS (with retry loop)
            # ═══════════════════════════════════════════════════════════════
            update_progress("LLM Analysis", 70, "Generating AI insights...")
            
            retry_count = 0
            llm_result = None
            qc_result = None
            
            while retry_count < self.max_retries:
                llm_result = self.agents["llm"].interpret(summary, anomalies, df)
                qc_result = self.agents["quality"].validate_llm_output(llm_result, summary)
                
                self._record_validation("QualityControl", qc_result["valid"],
                                       f"LLM validation (attempt {retry_count + 1})",
                                       {"issues": qc_result.get("issues", [])})
                
                if qc_result["valid"] or not qc_result.get("retry_needed", False):
                    break
                
                retry_count += 1
                self._log(f"🔄 LLM retry {retry_count}/{self.max_retries}", "WARNING")
            
            results["llm_insight"] = llm_result
            results["quality_control"] = qc_result
            results["stages_completed"].append("llm_analysis")
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 12: DECISION MAKING
            # ═══════════════════════════════════════════════════════════════
            update_progress("Decision", 80, "Making strategic decisions...")
            
            decisions = self.agents["decision"].decide(
                summary, anomalies, llm_result, qc_result
            )
            results["decisions"] = decisions
            results["stages_completed"].append("decision")
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 13: REPORT GENERATION
            # ═══════════════════════════════════════════════════════════════
            update_progress("Reporting", 85, "Generating report...")
            
            report = self.agents["reporter"].generate_report(
                summary=summary,
                anomalies=anomalies,
                llm_result=llm_result,
                decisions=decisions,
                validation_history=self.validation_history,
                reasoning=results.get("reasoning"),
                debate=results.get("debate"),
                action_plan=results.get("action_plan")
            )
            results["report"] = report
            results["stages_completed"].append("report_generation")
            
            # ═══════════════════════════════════════════════════════════════
            # STAGE 14: FINAL VALIDATION (with retry loop)
            # ═══════════════════════════════════════════════════════════════
            update_progress("Final Validation", 95, "Validating report...")
            
            final_retry = 0
            while final_retry < self.max_retries:
                final_validation = self.agents["final_validator"].validate_report(
                    report, decisions
                )
                
                self._record_validation("FinalValidator", final_validation["valid"],
                                       f"Final validation (attempt {final_retry + 1})",
                                       {"issues": final_validation.get("issues", [])})
                
                if final_validation["valid"]:
                    break
                
                final_retry += 1
                self._log(f"🔄 Report correction {final_retry}/{self.max_retries}", "WARNING")
            
            results["final_validation"] = final_validation
            results["stages_completed"].append("final_validation")
            
            # ═══════════════════════════════════════════════════════════════
            # COMPLETE
            # ═══════════════════════════════════════════════════════════════
            update_progress("Complete", 100, "Pipeline completed successfully!")
            
            results["status"] = "success"
            results["df"] = df
            results["validation_history"] = self.validation_history
            results["agent_messages"] = self.agent_messages
            self.pipeline_status = "completed"
            
            self._log("✅ Pipeline completed successfully!", "SUCCESS")
            
        except Exception as e:
            results["status"] = "error"
            results["errors"].append({
                "stage": "pipeline",
                "message": str(e)
            })
            self.pipeline_status = "error"
            self._log(f"❌ Pipeline error: {e}", "ERROR")
            
            import traceback
            results["traceback"] = traceback.format_exc()
        
        return results
    
    def get_agent_status(self) -> Dict[str, str]:
        """Get status of all agents."""
        status = {}
        for name, agent in self.agents.items():
            status[name] = getattr(agent, 'state', 'unknown')
        for name, agent in self.reasoning_agents.items():
            status[f"reasoning_{name}"] = getattr(agent, 'state', 'unknown')
        return status
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of all validations."""
        if not self.validation_history:
            return {"total": 0, "passed": 0, "failed": 0, "rate": 0}
        
        passed = sum(1 for v in self.validation_history if v["valid"])
        total = len(self.validation_history)
        
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "rate": (passed / total) * 100 if total > 0 else 0,
            "history": self.validation_history
        }
    
    def get_message_log(self) -> List[Dict]:
        """Get all agent messages."""
        all_messages = self.agent_messages.copy()
        
        # Collect messages from all agents
        for agent in self.agents.values():
            if hasattr(agent, 'get_history'):
                all_messages.extend(agent.get_history())
        
        for agent in self.reasoning_agents.values():
            if hasattr(agent, 'get_history'):
                all_messages.extend(agent.get_history())
        
        # Sort by timestamp
        all_messages.sort(key=lambda x: x.get('timestamp', ''))
        
        return all_messages
