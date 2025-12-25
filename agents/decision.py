"""
Decision Agent - Makes strategic decisions based on all analysis inputs
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime
from agents.base_agent import BaseAgent


class DecisionAgent(BaseAgent):
    """
    Agent responsible for making strategic decisions based on all analysis inputs.
    Synthesizes information from multiple agents to produce actionable decisions.
    """
    
    def __init__(self, name: str = "DecisionMaker"):
        super().__init__(name, role="Strategic Decision Specialist")
        self.decision_history = []
        
        # Decision thresholds
        self.thresholds = {
            'critical_machine_ratio': 0.30,      # >30% machines critical = URGENT
            'high_temp_count': 5,                 # >5 high temp = URGENT
            'maintenance_overdue_ratio': 0.20,    # >20% overdue = HIGH
            'low_health_threshold': 50,           # Health < 50 = CRITICAL
            'min_utilization': 0.40               # <40% utilization = concerning
        }
    
    def decide(self, summary: Dict[str, Any], anomalies: Dict[str, Any],
               llm_result: Dict[str, Any], qc_result: Dict[str, Any],
               reasoning_result: Dict[str, Any] = None,
               debate_result: Dict[str, Any] = None,
               plan_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make strategic decisions based on all analysis inputs.
        
        Args:
            summary: Analysis summary
            anomalies: Detected anomalies
            llm_result: LLM insights
            qc_result: Quality control validation
            reasoning_result: Optional reasoning agent output
            debate_result: Optional debate agent output
            plan_result: Optional planning agent output
            
        Returns:
            Dictionary containing decisions and priority
        """
        self.set_state("deciding")
        self.send_message("⚡ Synthesizing all inputs for strategic decisions...")
        
        decisions = []
        priority = "NORMAL"
        risk_factors = []
        
        # Analyze critical machine ratio
        total_machines = summary.get('total_machines', 1)
        critical_count = summary.get('critical_machine_count', 0)
        critical_ratio = critical_count / total_machines
        
        if critical_ratio > self.thresholds['critical_machine_ratio']:
            decisions.append({
                'action': f"⚠️ MAINTENANCE MASSIVE requise ({critical_count} machines critiques, {critical_ratio:.0%} du parc)",
                'priority': 'P1',
                'category': 'maintenance',
                'impact': 'HIGH'
            })
            priority = "URGENT"
            risk_factors.append(f"Critical machine ratio: {critical_ratio:.0%}")
        
        # Analyze temperature anomalies
        high_temp_count = len(anomalies.get('high_temperature', []))
        if high_temp_count > self.thresholds['high_temp_count']:
            decisions.append({
                'action': f"🌡️ Intervention refroidissement urgente ({high_temp_count} machines en surchauffe)",
                'priority': 'P1',
                'category': 'safety',
                'impact': 'HIGH'
            })
            priority = "URGENT"
            risk_factors.append(f"High temperature anomalies: {high_temp_count}")
        elif high_temp_count > 0:
            decisions.append({
                'action': f"🌡️ Surveiller températures ({high_temp_count} machines)",
                'priority': 'P2',
                'category': 'monitoring',
                'impact': 'MEDIUM'
            })
        
        # Analyze vibration anomalies
        high_vib_count = len(anomalies.get('high_vibration', []))
        if high_vib_count > 3:
            decisions.append({
                'action': f"📳 Diagnostic vibrations requis ({high_vib_count} machines)",
                'priority': 'P2',
                'category': 'diagnostic',
                'impact': 'MEDIUM'
            })
            risk_factors.append(f"Vibration anomalies: {high_vib_count}")
        
        # Analyze idle machines
        zero_util = anomalies.get('zero_utilization', [])
        if len(zero_util) > 0:
            decisions.append({
                'action': f"🔧 Vérifier machines à l'arrêt: {', '.join(zero_util[:5])}{'...' if len(zero_util) > 5 else ''}",
                'priority': 'P2',
                'category': 'operations',
                'impact': 'MEDIUM'
            })
        
        # Analyze maintenance overdue
        maint_overdue = anomalies.get('maintenance_overdue', [])
        if len(maint_overdue) > total_machines * self.thresholds['maintenance_overdue_ratio']:
            decisions.append({
                'action': f"🔨 Planifier maintenance urgente ({len(maint_overdue)} machines en retard)",
                'priority': 'P1',
                'category': 'maintenance',
                'impact': 'HIGH'
            })
            if priority != "URGENT":
                priority = "HIGH"
        elif len(maint_overdue) > 0:
            decisions.append({
                'action': f"🔨 Programmer maintenance ({len(maint_overdue)} machines)",
                'priority': 'P3',
                'category': 'maintenance',
                'impact': 'LOW'
            })
        
        # Analyze LLM quality and insights
        if not qc_result.get('valid', True):
            decisions.append({
                'action': "⚠️ Analyse LLM nécessite vérification manuelle",
                'priority': 'P3',
                'category': 'quality',
                'impact': 'LOW'
            })
        
        # Check for risk keywords in LLM response
        llm_text = llm_result.get("text", "").lower()
        if any(word in llm_text for word in ['risque majeur', 'danger', 'urgence', 'critique']):
            if priority == "NORMAL":
                priority = "HIGH"
            decisions.append({
                'action': "📊 Audit approfondi recommandé suite à l'analyse IA",
                'priority': 'P2',
                'category': 'audit',
                'impact': 'MEDIUM'
            })
        
        # Incorporate reasoning agent insights if available
        if reasoning_result:
            confidence = reasoning_result.get('confidence', 'LOW')
            if confidence == 'HIGH':
                decisions.append({
                    'action': "✅ Recommandations du raisonnement IA validées avec haute confiance",
                    'priority': 'P2',
                    'category': 'ai_recommendation',
                    'impact': 'MEDIUM'
                })
        
        # Incorporate debate conclusions if available
        if debate_result and debate_result.get('consensus'):
            decisions.append({
                'action': "🎭 Intégrer les conclusions du débat multi-perspectives",
                'priority': 'P2',
                'category': 'strategy',
                'impact': 'MEDIUM'
            })
        
        # Incorporate plan if available
        if plan_result and plan_result.get('phases'):
            decisions.append({
                'action': f"📋 Suivre le plan d'action en {len(plan_result['phases'])} phases",
                'priority': 'P2',
                'category': 'planning',
                'impact': 'HIGH'
            })
        
        # Health score analysis
        avg_health = summary.get('avg_health_score', 100)
        if avg_health < self.thresholds['low_health_threshold']:
            decisions.append({
                'action': f"❤️ Alerte santé globale du parc (score: {avg_health:.1f}/100)",
                'priority': 'P1',
                'category': 'health',
                'impact': 'HIGH'
            })
            priority = "URGENT"
        
        # Sort decisions by priority
        priority_order = {'P1': 0, 'P2': 1, 'P3': 2}
        decisions.sort(key=lambda x: priority_order.get(x['priority'], 99))
        
        self.set_state("decided")
        self.send_message(f"✅ {len(decisions)} décisions générées | Priorité: {priority}", "SUCCESS")
        
        # Create decision record
        decision_record = {
            "timestamp": datetime.now().isoformat(),
            "priority": priority,
            "decisions": decisions,
            "action_needed": priority in ["URGENT", "HIGH"],
            "risk_factors": risk_factors,
            "summary_stats": {
                "total_machines": total_machines,
                "critical_machines": critical_count,
                "anomaly_count": sum(len(v) for v in anomalies.values() if isinstance(v, list)),
                "llm_quality_valid": qc_result.get('valid', True)
            }
        }
        
        self.decision_history.append(decision_record)
        self.update_shared_context("decisions", decision_record)
        
        return decision_record
    
    def get_priority_actions(self, decision_record: Dict[str, Any], 
                             max_actions: int = 5) -> List[Dict[str, Any]]:
        """Get top priority actions from decisions."""
        decisions = decision_record.get('decisions', [])
        return decisions[:max_actions]
    
    def get_decision_summary(self) -> str:
        """Generate a summary of all decisions made."""
        if not self.decision_history:
            return "No decisions made yet."
        
        summary = ["📋 DECISION HISTORY", "=" * 40]
        
        for i, record in enumerate(self.decision_history, 1):
            summary.append(f"\nDecision Set {i} - {record['timestamp']}")
            summary.append(f"Priority: {record['priority']}")
            summary.append(f"Actions: {len(record['decisions'])}")
            
            for dec in record['decisions'][:3]:
                summary.append(f"  • [{dec['priority']}] {dec['action'][:50]}...")
        
        return "\n".join(summary)
