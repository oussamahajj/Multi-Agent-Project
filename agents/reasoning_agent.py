"""
Reasoning Agent - Implements Chain-of-Thought reasoning using Gemini LLM
This agent provides structured reasoning capabilities for complex analysis tasks.
"""

import json
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class ReasoningAgent(BaseAgent):
    """
    Agent that implements Chain-of-Thought (CoT) reasoning using Gemini LLM.
    Breaks down complex problems into reasoning steps and provides structured analysis.
    """
    
    def __init__(self, name: str = "ReasoningAgent", api_key: str = None):
        super().__init__(name, role="Chain-of-Thought Reasoning Specialist")
        self.api_key = api_key
        self.client = None
        self.model_name = "gemini-2.5-flash"
        self.reasoning_history = []
        
        if GENAI_AVAILABLE and api_key:
            try:
                self.client = genai.Client(api_key=api_key)
                self.send_message("✅ Gemini client initialized successfully", "SUCCESS")
            except Exception as e:
                self.send_message(f"⚠️ Failed to initialize Gemini client: {e}", "WARNING")
    
    def reason(self, context: Dict[str, Any], question: str) -> Dict[str, Any]:
        """
        Apply Chain-of-Thought reasoning to analyze a question given context.
        
        Args:
            context: Dictionary containing relevant data and analysis results
            question: The question or problem to reason about
            
        Returns:
            Dictionary containing reasoning steps, conclusion, and confidence
        """
        self.set_state("reasoning")
        self.send_message(f"🧠 Starting Chain-of-Thought reasoning...")
        
        # Build the CoT prompt
        prompt = self._build_cot_prompt(context, question)
        
        try:
            if self.client:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                reasoning_text = response.text
            else:
                reasoning_text = self._fallback_reasoning(context, question)
            
            # Parse the reasoning into structured format
            result = self._parse_reasoning(reasoning_text, context)
            
            self.reasoning_history.append({
                'question': question,
                'result': result
            })
            
            self.set_state("completed")
            self.send_message("✅ Chain-of-Thought reasoning completed", "SUCCESS")
            
            return result
            
        except Exception as e:
            self.send_message(f"❌ Reasoning error: {e}", "ERROR")
            return self._fallback_reasoning(context, question)
    
    def _build_cot_prompt(self, context: Dict[str, Any], question: str) -> str:
        """Build a Chain-of-Thought prompt for the LLM."""
        
        # Extract key metrics from context
        summary = context.get('summary', {})
        anomalies = context.get('anomalies', {})
        
        prompt = f"""You are an expert industrial analyst applying Chain-of-Thought reasoning.

## CONTEXT DATA

### Key Performance Indicators:
- Total Machines: {summary.get('total_machines', 'N/A')}
- Average Utilization: {summary.get('avg_utilization', 0):.2%}
- Average Energy Efficiency: {summary.get('avg_energy_efficiency', 'N/A')} kW/h
- Average Health Score: {summary.get('avg_health_score', 'N/A')}/100
- Critical Machines (Low Utilization): {summary.get('critical_machine_count', 0)}

### Detected Anomalies:
- High Temperature: {len(anomalies.get('high_temperature', []))} machines
- High Vibration: {len(anomalies.get('high_vibration', []))} machines
- Energy Spikes: {len(anomalies.get('energy_spikes', []))} machines
- Zero Utilization: {len(anomalies.get('zero_utilization', []))} machines
- Maintenance Overdue: {len(anomalies.get('maintenance_overdue', []))} machines

### Risk Distribution:
{json.dumps(summary.get('risk_distribution', {}), indent=2)}

## QUESTION TO ANALYZE:
{question}

## INSTRUCTIONS:
Apply Chain-of-Thought reasoning by following these steps:

**STEP 1 - UNDERSTAND THE PROBLEM:**
Clearly state what we need to determine and what information is relevant.

**STEP 2 - GATHER EVIDENCE:**
List the specific data points from the context that are relevant to this question.

**STEP 3 - ANALYZE PATTERNS:**
Identify patterns, correlations, or concerning trends in the data.

**STEP 4 - CONSIDER IMPLICATIONS:**
What do these patterns mean for operations? What are the risks?

**STEP 5 - FORM HYPOTHESIS:**
Based on the analysis, what is the most likely conclusion?

**STEP 6 - VALIDATE:**
Check if the conclusion is consistent with all the evidence.

**STEP 7 - FINAL CONCLUSION:**
State your final conclusion with confidence level (HIGH/MEDIUM/LOW).

**STEP 8 - RECOMMENDATIONS:**
Provide 3-5 specific, actionable recommendations.

Please format your response clearly following each step."""
        
        return prompt
    
    def _parse_reasoning(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into structured reasoning result."""
        
        # Extract key sections
        steps = []
        conclusion = ""
        recommendations = []
        confidence = "MEDIUM"
        
        lines = text.split('\n')
        current_step = ""
        current_content = []
        
        for line in lines:
            line = line.strip()
            
            # Detect step markers
            if any(marker in line.upper() for marker in ['STEP 1', 'STEP 2', 'STEP 3', 'STEP 4', 'STEP 5', 'STEP 6', 'STEP 7', 'STEP 8']):
                if current_step and current_content:
                    steps.append({
                        'step': current_step,
                        'content': '\n'.join(current_content)
                    })
                current_step = line
                current_content = []
            elif 'FINAL CONCLUSION' in line.upper():
                current_step = "CONCLUSION"
                current_content = []
            elif 'RECOMMENDATION' in line.upper():
                current_step = "RECOMMENDATIONS"
                current_content = []
            elif current_step:
                current_content.append(line)
        
        # Add last section
        if current_step and current_content:
            steps.append({
                'step': current_step,
                'content': '\n'.join(current_content)
            })
        
        # Extract confidence level
        if 'HIGH' in text.upper():
            confidence = 'HIGH'
        elif 'LOW' in text.upper():
            confidence = 'LOW'
        
        return {
            'reasoning_text': text,
            'steps': steps,
            'confidence': confidence,
            'status': 'success'
        }
    
    def _fallback_reasoning(self, context: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Provide fallback reasoning when LLM is unavailable."""
        
        summary = context.get('summary', {})
        anomalies = context.get('anomalies', {})
        
        # Basic rule-based reasoning
        issues = []
        recommendations = []
        
        # Analyze utilization
        avg_util = summary.get('avg_utilization', 0.5)
        if avg_util < 0.4:
            issues.append("Critical: Average utilization below 40%")
            recommendations.append("Investigate causes of low machine utilization")
        
        # Analyze anomalies
        critical_machines = summary.get('critical_machine_count', 0)
        if critical_machines > summary.get('total_machines', 1) * 0.3:
            issues.append(f"Alert: {critical_machines} machines need immediate attention")
            recommendations.append("Prioritize maintenance for critical machines")
        
        # Temperature issues
        temp_anomalies = len(anomalies.get('high_temperature', []))
        if temp_anomalies > 5:
            issues.append(f"Warning: {temp_anomalies} machines with high temperature")
            recommendations.append("Check cooling systems on affected machines")
        
        conclusion = f"Analysis identified {len(issues)} key issues requiring attention."
        
        return {
            'reasoning_text': f"""
FALLBACK ANALYSIS (LLM unavailable)

Issues Identified:
{chr(10).join('• ' + issue for issue in issues)}

Recommendations:
{chr(10).join('• ' + rec for rec in recommendations)}

Conclusion: {conclusion}
""",
            'steps': [{'step': 'Fallback Analysis', 'content': conclusion}],
            'confidence': 'LOW',
            'status': 'fallback'
        }
    
    def analyze_root_cause(self, context: Dict[str, Any], anomaly_type: str) -> Dict[str, Any]:
        """
        Perform root cause analysis for a specific anomaly type.
        
        Args:
            context: Analysis context
            anomaly_type: Type of anomaly to analyze
            
        Returns:
            Root cause analysis results
        """
        question = f"""
        Perform a root cause analysis for the {anomaly_type} anomalies detected.
        What are the most likely causes? What factors correlate with these anomalies?
        How can we prevent them in the future?
        """
        
        return self.reason(context, question)
