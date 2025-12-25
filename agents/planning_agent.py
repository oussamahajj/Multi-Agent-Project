"""
Planning Agent - Strategic planning and task decomposition using LLM
This agent creates action plans and decomposes complex goals into actionable tasks.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from agents.base_agent import BaseAgent

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class PlanningAgent(BaseAgent):
    """
    Agent responsible for strategic planning and task decomposition.
    Creates detailed action plans based on analysis results.
    """
    
    def __init__(self, name: str = "PlanningAgent", api_key: str = None):
        super().__init__(name, role="Strategic Planning Specialist")
        self.api_key = api_key
        self.client = None
        self.model_name = "gemini-2.5-flash"
        self.plans = []
        
        if GENAI_AVAILABLE and api_key:
            try:
                self.client = genai.Client(api_key=api_key)
                self.send_message("✅ Planning Agent initialized with Gemini", "SUCCESS")
            except Exception as e:
                self.send_message(f"⚠️ Failed to initialize Gemini client: {e}", "WARNING")
    
    def create_action_plan(self, context: Dict[str, Any], goal: str) -> Dict[str, Any]:
        """
        Create a comprehensive action plan for a given goal.
        
        Args:
            context: Analysis context with data and insights
            goal: The strategic goal to plan for
            
        Returns:
            Dictionary containing the action plan
        """
        self.set_state("planning")
        self.send_message(f"📋 Creating action plan for: {goal}")
        
        prompt = self._build_planning_prompt(context, goal)
        
        try:
            if self.client:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                plan_text = response.text
            else:
                plan_text = self._fallback_plan(context, goal)
            
            # Parse the plan into structured format
            plan = self._parse_plan(plan_text, goal)
            
            self.plans.append(plan)
            self.set_state("planned")
            self.send_message("✅ Action plan created successfully", "SUCCESS")
            
            self.update_shared_context('action_plan', plan)
            
            return plan
            
        except Exception as e:
            self.send_message(f"❌ Planning error: {e}", "ERROR")
            return self._fallback_plan(context, goal)
    
    def _build_planning_prompt(self, context: Dict[str, Any], goal: str) -> str:
        """Build the planning prompt for LLM."""
        
        summary = context.get('summary', {})
        anomalies = context.get('anomalies', {})
        reasoning = context.get('reasoning', {})
        
        prompt = f"""You are an industrial operations planner creating an action plan.

## CURRENT SITUATION

### Key Metrics:
- Total Machines: {summary.get('total_machines', 'N/A')}
- Average Utilization: {summary.get('avg_utilization', 0):.2%}
- Average Health Score: {summary.get('avg_health_score', 'N/A')}/100
- Critical Machines: {summary.get('critical_machine_count', 0)}

### Active Issues:
- High Temperature Alerts: {len(anomalies.get('high_temperature', []))} machines
- High Vibration Alerts: {len(anomalies.get('high_vibration', []))} machines
- Maintenance Overdue: {len(anomalies.get('maintenance_overdue', []))} machines
- Zero Utilization: {len(anomalies.get('zero_utilization', []))} machines

### Previous Analysis Insights:
{reasoning.get('reasoning_text', 'No previous reasoning available.')[:500]}

## GOAL:
{goal}

## CREATE AN ACTION PLAN with the following structure:

### EXECUTIVE SUMMARY
Brief overview of the plan (2-3 sentences)

### PHASE 1: IMMEDIATE ACTIONS (0-7 days)
List 3-5 urgent actions with:
- Action description
- Priority (P1/P2/P3)
- Responsible party
- Expected outcome
- Resources needed

### PHASE 2: SHORT-TERM ACTIONS (1-4 weeks)
List 3-5 actions with same format

### PHASE 3: MEDIUM-TERM ACTIONS (1-3 months)
List 2-3 strategic actions

### SUCCESS METRICS
Define 3-5 KPIs to measure plan success

### RISKS AND MITIGATION
List 2-3 potential risks and mitigation strategies

### RESOURCE REQUIREMENTS
- Personnel
- Budget estimate
- Equipment/Tools

Please be specific and actionable."""
        
        return prompt
    
    def _parse_plan(self, plan_text: str, goal: str) -> Dict[str, Any]:
        """Parse LLM response into structured plan."""
        
        today = datetime.now()
        
        plan = {
            'goal': goal,
            'created_at': today.isoformat(),
            'raw_plan': plan_text,
            'phases': [],
            'metrics': [],
            'risks': [],
            'status': 'success'
        }
        
        # Extract phases from text
        lines = plan_text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line_upper = line.upper().strip()
            
            if 'PHASE 1' in line_upper or 'IMMEDIATE' in line_upper:
                if current_section and current_content:
                    plan['phases'].append({
                        'name': current_section,
                        'content': '\n'.join(current_content)
                    })
                current_section = 'Phase 1: Immediate (0-7 days)'
                current_content = []
            elif 'PHASE 2' in line_upper or 'SHORT-TERM' in line_upper:
                if current_section and current_content:
                    plan['phases'].append({
                        'name': current_section,
                        'content': '\n'.join(current_content)
                    })
                current_section = 'Phase 2: Short-term (1-4 weeks)'
                current_content = []
            elif 'PHASE 3' in line_upper or 'MEDIUM-TERM' in line_upper:
                if current_section and current_content:
                    plan['phases'].append({
                        'name': current_section,
                        'content': '\n'.join(current_content)
                    })
                current_section = 'Phase 3: Medium-term (1-3 months)'
                current_content = []
            elif 'SUCCESS METRIC' in line_upper or 'KPI' in line_upper:
                if current_section and current_content:
                    plan['phases'].append({
                        'name': current_section,
                        'content': '\n'.join(current_content)
                    })
                current_section = 'Success Metrics'
                current_content = []
            elif 'RISK' in line_upper and 'MITIGATION' in line_upper:
                if current_section and current_content:
                    if 'Metric' in current_section:
                        plan['metrics'] = current_content
                    else:
                        plan['phases'].append({
                            'name': current_section,
                            'content': '\n'.join(current_content)
                        })
                current_section = 'Risks'
                current_content = []
            elif current_section:
                if line.strip():
                    current_content.append(line.strip())
        
        # Add last section
        if current_section and current_content:
            if 'Metric' in current_section:
                plan['metrics'] = current_content
            elif 'Risk' in current_section:
                plan['risks'] = current_content
            else:
                plan['phases'].append({
                    'name': current_section,
                    'content': '\n'.join(current_content)
                })
        
        return plan
    
    def _fallback_plan(self, context: Dict[str, Any], goal: str) -> Dict[str, Any]:
        """Generate fallback plan when LLM unavailable."""
        
        summary = context.get('summary', {})
        anomalies = context.get('anomalies', {})
        
        today = datetime.now()
        
        plan = {
            'goal': goal,
            'created_at': today.isoformat(),
            'phases': [],
            'metrics': [],
            'risks': [],
            'status': 'fallback'
        }
        
        # Phase 1: Immediate
        phase1_actions = []
        if anomalies.get('high_temperature'):
            phase1_actions.append("• Inspect cooling systems on high-temperature machines")
        if anomalies.get('maintenance_overdue'):
            phase1_actions.append("• Schedule emergency maintenance for overdue machines")
        if anomalies.get('zero_utilization'):
            phase1_actions.append("• Investigate and restart idle machines")
        if not phase1_actions:
            phase1_actions.append("• Conduct routine system checks")
        
        plan['phases'].append({
            'name': 'Phase 1: Immediate (0-7 days)',
            'content': '\n'.join(phase1_actions)
        })
        
        # Phase 2: Short-term
        plan['phases'].append({
            'name': 'Phase 2: Short-term (1-4 weeks)',
            'content': """• Implement preventive maintenance schedule
• Train staff on anomaly detection procedures
• Review and update safety protocols
• Optimize machine utilization patterns"""
        })
        
        # Phase 3: Medium-term
        plan['phases'].append({
            'name': 'Phase 3: Medium-term (1-3 months)',
            'content': """• Deploy predictive maintenance system
• Upgrade monitoring infrastructure
• Establish KPI dashboards for real-time tracking"""
        })
        
        # Metrics
        plan['metrics'] = [
            "Machine uptime > 85%",
            "Zero safety incidents",
            "Maintenance compliance > 95%",
            "Energy efficiency improvement > 10%"
        ]
        
        # Risks
        plan['risks'] = [
            "Budget constraints may delay equipment upgrades",
            "Staff training may impact short-term productivity",
            "Legacy system integration challenges"
        ]
        
        plan['raw_plan'] = self._format_plan_text(plan)
        
        return plan
    
    def _format_plan_text(self, plan: Dict[str, Any]) -> str:
        """Format plan dictionary as readable text."""
        text = [f"ACTION PLAN: {plan['goal']}", "=" * 50, ""]
        
        for phase in plan.get('phases', []):
            text.append(f"\n### {phase['name']}")
            text.append(phase['content'])
        
        if plan.get('metrics'):
            text.append("\n### SUCCESS METRICS")
            text.extend(plan['metrics'])
        
        if plan.get('risks'):
            text.append("\n### RISKS")
            text.extend(plan['risks'])
        
        return '\n'.join(text)
    
    def decompose_task(self, task: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Decompose a complex task into subtasks.
        
        Args:
            task: The task to decompose
            context: Analysis context
            
        Returns:
            List of subtasks with details
        """
        self.send_message(f"🔧 Decomposing task: {task}")
        
        prompt = f"""Decompose this industrial task into 3-7 specific subtasks:

TASK: {task}

For each subtask provide:
1. Subtask description
2. Prerequisites (what must be done first)
3. Estimated duration
4. Required resources
5. Success criteria

Format as a numbered list."""
        
        try:
            if self.client:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                subtasks_text = response.text
            else:
                subtasks_text = """
1. Assess current state - No prerequisites - 2 hours - Analysis tools - Clear baseline established
2. Identify priorities - After assessment - 1 hour - Team input - Priority list created
3. Plan resources - After priorities - 2 hours - Budget data - Resource plan approved
4. Execute changes - After planning - Variable - As specified - Changes implemented
5. Validate results - After execution - 1 hour - Testing tools - Results meet criteria
"""
            
            # Parse subtasks
            subtasks = []
            lines = subtasks_text.strip().split('\n')
            
            for line in lines:
                if line.strip() and line[0].isdigit():
                    subtasks.append({
                        'description': line.strip(),
                        'status': 'pending'
                    })
            
            return subtasks
            
        except Exception as e:
            self.send_message(f"⚠️ Error decomposing task: {e}", "WARNING")
            return [{'description': task, 'status': 'pending'}]
    
    def get_plans_summary(self) -> str:
        """Get summary of all created plans."""
        if not self.plans:
            return "No plans created yet."
        
        summary = ["📋 PLANS SUMMARY", "=" * 40]
        for i, plan in enumerate(self.plans, 1):
            summary.append(f"\nPlan {i}: {plan['goal']}")
            summary.append(f"Created: {plan['created_at']}")
            summary.append(f"Phases: {len(plan.get('phases', []))}")
            summary.append(f"Status: {plan['status']}")
        
        return '\n'.join(summary)
