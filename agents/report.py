"""
Report Agent - Generates comprehensive reports from all analysis results
"""

from typing import Dict, Any, List
from datetime import datetime
from agents.base_agent import BaseAgent


class ReportAgent(BaseAgent):
    """
    Agent responsible for generating comprehensive reports.
    Synthesizes all analysis results into readable, actionable reports.
    """
    
    def __init__(self, name: str = "ReportGenerator"):
        super().__init__(name, role="Report Generation Specialist")
        self.report_history = []
    
    def generate_report(self, summary: Dict[str, Any], anomalies: Dict[str, Any],
                        llm_result: Dict[str, Any], decisions: Dict[str, Any],
                        validation_history: List[Dict[str, Any]],
                        reasoning: Dict[str, Any] = None,
                        debate: Dict[str, Any] = None,
                        action_plan: Dict[str, Any] = None) -> str:
        """
        Generate a comprehensive report from all analysis results.
        
        Args:
            summary: Analysis summary
            anomalies: Detected anomalies
            llm_result: LLM insights
            decisions: Strategic decisions
            validation_history: History of all validations
            reasoning: Optional reasoning output (Chain-of-Thought)
            debate: Optional debate output
            action_plan: Optional plan output
            
        Returns:
            Formatted report string
        """
        self.set_state("generating")
        self.send_message("📄 Generating comprehensive report...")
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        priority = decisions.get('priority', 'NORMAL')
        
        # Build report sections
        report_parts = []
        
        # Header
        report_parts.append(self._generate_header(priority, timestamp))
        
        # Executive Summary
        report_parts.append(self._generate_executive_summary(summary, decisions))
        
        # KPI Section
        report_parts.append(self._generate_kpi_section(summary))
        
        # Anomalies Section
        report_parts.append(self._generate_anomalies_section(anomalies))
        
        # AI Analysis Section
        report_parts.append(self._generate_ai_analysis_section(llm_result, reasoning))
        
        # Debate Section (if available)
        if debate:
            report_parts.append(self._generate_debate_section(debate))
        
        # Decisions Section
        report_parts.append(self._generate_decisions_section(decisions))
        
        # Action Plan Section (if available)
        if action_plan:
            report_parts.append(self._generate_plan_section(action_plan))
        
        # Validation/Traceability Section
        report_parts.append(self._generate_traceability_section(validation_history))
        
        # Footer
        report_parts.append(self._generate_footer(timestamp))
        
        report = "\n".join(report_parts)
        
        self.report_history.append({
            'timestamp': timestamp,
            'priority': priority,
            'length': len(report)
        })
        
        self.set_state("generated")
        self.send_message(f"✅ Report generated ({len(report)} characters)", "SUCCESS")
        
        return report
    
    def _generate_header(self, priority: str, timestamp: str) -> str:
        """Generate report header."""
        priority_indicator = {
            'URGENT': '🔴',
            'HIGH': '🟠',
            'NORMAL': '🟢'
        }.get(priority, '⚪')
        
        return f"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     🏭 RAPPORT DE PERFORMANCE INDUSTRIELLE                       ║
║        Système Multi-Agent Intelligent                           ║
║                                                                  ║
║     {priority_indicator} Priorité: {priority:<10}                               ║
║     📅 Date: {timestamp}                            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
    
    def _generate_executive_summary(self, summary: Dict, decisions: Dict) -> str:
        """Generate executive summary section."""
        total = summary.get('total_machines', 0)
        critical = summary.get('critical_machine_count', 0)
        utilization = summary.get('avg_utilization', 0)
        health = summary.get('avg_health_score', 0)
        
        status = "✅ OPÉRATIONNEL" if critical < total * 0.1 else "⚠️ ATTENTION REQUISE" if critical < total * 0.3 else "🚨 CRITIQUE"
        
        return f"""
┌──────────────────────────────────────────────────────────────────┐
│                    📊 RÉSUMÉ EXÉCUTIF                            │
└──────────────────────────────────────────────────────────────────┘

État Global: {status}

• Parc de {total} machines analysé
• Taux d'utilisation moyen: {utilization:.1%}
• Score de santé global: {health:.1f}/100
• Machines nécessitant intervention: {critical} ({critical/total*100:.1f}%)
• Décisions générées: {len(decisions.get('decisions', []))}
• Actions prioritaires: {sum(1 for d in decisions.get('decisions', []) if d.get('priority') == 'P1')}
"""
    
    def _generate_kpi_section(self, summary: Dict) -> str:
        """Generate KPI section."""
        return f"""
┌──────────────────────────────────────────────────────────────────┐
│                    📈 INDICATEURS CLÉS (KPI)                     │
└──────────────────────────────────────────────────────────────────┘

Performance Opérationnelle:
  • Utilisation moyenne: {summary.get('avg_utilization', 0):.2%}
  • Utilisation médiane: {summary.get('median_utilization', 0):.2%}
  • Machines bien utilisées (>70%): {len(summary.get('machines_well_utilized', []))}

Efficacité Énergétique:
  • Efficacité moyenne: {summary.get('avg_energy_efficiency', 0):.2f} kW/h
  • Écart-type: {summary.get('energy_efficiency_std', 0):.2f}

Santé du Parc:
  • Score moyen: {summary.get('avg_health_score', 0):.1f}/100
  • Score minimum: {summary.get('min_health_score', 0):.1f}/100
  • Machines en bonne santé (>80): {len(summary.get('machines_good_health', []))}
  • Machines critiques (<50): {len(summary.get('machines_critical_health', []))}

Stabilité:
  • Indice moyen: {summary.get('avg_stability', 0):.2f}
  • Machines instables: {len(summary.get('machines_instables', []))}
"""
    
    def _generate_anomalies_section(self, anomalies: Dict) -> str:
        """Generate anomalies section."""
        sections = []
        sections.append("""
┌──────────────────────────────────────────────────────────────────┐
│                    🔍 ANOMALIES DÉTECTÉES                        │
└──────────────────────────────────────────────────────────────────┘
""")
        
        anomaly_types = [
            ('high_temperature', '🌡️ Températures élevées'),
            ('high_vibration', '📳 Vibrations élevées'),
            ('energy_spikes', '⚡ Pics énergétiques'),
            ('zero_utilization', '⏸️ Machines à l\'arrêt'),
            ('very_low_utilization', '📉 Utilisation très faible'),
            ('high_sound', '🔊 Niveaux sonores élevés'),
            ('maintenance_overdue', '🔧 Maintenance en retard'),
            ('maintenance_critical', '🚨 Maintenance critique'),
            ('high_error_rate', '❌ Taux d\'erreur élevé'),
            ('high_ai_override', '🤖 Interventions IA fréquentes'),
            ('multi_factor_critical', '⚠️ Multi-facteurs critiques')
        ]
        
        for key, label in anomaly_types:
            machines = anomalies.get(key, [])
            if machines:
                count = len(machines)
                preview = ', '.join(machines[:5])
                if count > 5:
                    preview += f'... (+{count - 5})'
                sections.append(f"  {label}: {count} machines")
                sections.append(f"    → {preview}")
        
        total_anomalies = sum(len(v) for v in anomalies.values() if isinstance(v, list))
        sections.append(f"\n  📊 Total anomalies détectées: {total_anomalies}")
        
        return '\n'.join(sections)
    
    def _generate_ai_analysis_section(self, llm_result: Dict, reasoning_result: Dict = None) -> str:
        """Generate AI analysis section."""
        sections = []
        sections.append("""
┌──────────────────────────────────────────────────────────────────┐
│                    🤖 ANALYSE INTELLIGENCE ARTIFICIELLE           │
└──────────────────────────────────────────────────────────────────┘
""")
        
        status = llm_result.get('status', 'unknown')
        status_icon = '✅' if status == 'success' else '⚠️'
        sections.append(f"Statut LLM: {status_icon} {status.upper()}")
        sections.append("")
        
        # Add LLM insights (truncated if too long)
        llm_text = llm_result.get('text', 'Aucune analyse disponible')
        if len(llm_text) > 2000:
            llm_text = llm_text[:2000] + "\n... [Analyse tronquée - voir version complète]"
        sections.append(llm_text)
        
        # Add reasoning if available
        if reasoning_result:
            sections.append("\n--- Raisonnement Chain-of-Thought ---")
            confidence = reasoning_result.get('confidence', 'N/A')
            sections.append(f"Confiance: {confidence}")
            
            for step in reasoning_result.get('steps', [])[:3]:
                sections.append(f"\n{step.get('step', '')}")
        
        return '\n'.join(sections)
    
    def _generate_debate_section(self, debate_result: Dict) -> str:
        """Generate debate section."""
        consensus = debate_result.get('consensus', {}).get('text', 'Pas de consensus')
        
        return f"""
┌──────────────────────────────────────────────────────────────────┐
│                    🎭 DÉBAT MULTI-PERSPECTIVES                    │
└──────────────────────────────────────────────────────────────────┘

Rounds de débat: {debate_result.get('rounds', 0)}
Statut: {debate_result.get('status', 'unknown')}

CONSENSUS:
{consensus[:1500]}
"""
    
    def _generate_decisions_section(self, decisions: Dict) -> str:
        """Generate decisions section."""
        sections = []
        sections.append("""
┌──────────────────────────────────────────────────────────────────┐
│                    ⚡ DÉCISIONS STRATÉGIQUES                      │
└──────────────────────────────────────────────────────────────────┘
""")
        
        priority = decisions.get('priority', 'NORMAL')
        sections.append(f"Niveau d'urgence global: {priority}")
        sections.append(f"Action immédiate requise: {'OUI' if decisions.get('action_needed') else 'NON'}")
        sections.append("")
        
        for i, decision in enumerate(decisions.get('decisions', []), 1):
            priority_badge = {'P1': '🔴', 'P2': '🟠', 'P3': '🟢'}.get(decision.get('priority', ''), '⚪')
            sections.append(f"{i}. {priority_badge} [{decision.get('priority', 'P3')}] {decision.get('action', '')}")
            sections.append(f"   Catégorie: {decision.get('category', 'N/A')} | Impact: {decision.get('impact', 'N/A')}")
        
        if decisions.get('risk_factors'):
            sections.append("\nFacteurs de risque identifiés:")
            for risk in decisions['risk_factors']:
                sections.append(f"  ⚠️ {risk}")
        
        return '\n'.join(sections)
    
    def _generate_plan_section(self, plan_result: Dict) -> str:
        """Generate action plan section."""
        sections = []
        sections.append("""
┌──────────────────────────────────────────────────────────────────┐
│                    📋 PLAN D'ACTION                               │
└──────────────────────────────────────────────────────────────────┘
""")
        
        sections.append(f"Objectif: {plan_result.get('goal', 'N/A')}")
        sections.append(f"Statut: {plan_result.get('status', 'N/A')}")
        sections.append("")
        
        for phase in plan_result.get('phases', []):
            sections.append(f"\n### {phase.get('name', 'Phase')}")
            sections.append(phase.get('content', '')[:500])
        
        if plan_result.get('metrics'):
            sections.append("\nMétriques de succès:")
            for metric in plan_result['metrics'][:5]:
                sections.append(f"  ✓ {metric}")
        
        return '\n'.join(sections)
    
    def _generate_traceability_section(self, validation_history: List[Dict]) -> str:
        """Generate traceability section."""
        sections = []
        sections.append("""
┌──────────────────────────────────────────────────────────────────┐
│                    🔄 TRAÇABILITÉ & VALIDATIONS                   │
└──────────────────────────────────────────────────────────────────┘
""")
        
        sections.append(f"Validations effectuées: {len(validation_history)}")
        sections.append("")
        
        for val in validation_history:
            status_icon = '✅' if val.get('valid', True) else '❌'
            sections.append(f"  {status_icon} [{val.get('agent', 'Unknown')}] {val.get('message', '')}")
        
        return '\n'.join(sections)
    
    def _generate_footer(self, timestamp: str) -> str:
        """Generate report footer."""
        return f"""
══════════════════════════════════════════════════════════════════
                    FIN DU RAPPORT
        
        Généré le: {timestamp}
        Système: Multi-Agent Intelligent avec LLM
        Version: 2.0
        
        Ce rapport a été généré automatiquement par le système
        d'analyse multi-agent. Pour toute question, veuillez
        contacter l'équipe de maintenance.
══════════════════════════════════════════════════════════════════
"""
