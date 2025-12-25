"""
Debate Agent - Implements multi-perspective debate for complex decision making
This agent simulates debates between different expert perspectives using Gemini LLM.
"""

import json
from typing import Dict, Any, List, Tuple
from agents.base_agent import BaseAgent

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class DebateAgent(BaseAgent):
    """
    Agent that facilitates debates between multiple expert perspectives.
    Uses Gemini LLM to simulate different viewpoints and reach consensus.
    """
    
    def __init__(self, name: str = "DebateAgent", api_key: str = None):
        super().__init__(name, role="Multi-Perspective Debate Facilitator")
        self.api_key = api_key
        self.client = None
        self.model_name = "gemini-2.5-flash"
        self.debate_history = []
        
        # Define expert perspectives
        self.experts = {
            'operations_manager': {
                'name': 'Operations Manager',
                'focus': 'Production efficiency, uptime, and throughput',
                'bias': 'Prioritizes keeping machines running'
            },
            'maintenance_engineer': {
                'name': 'Maintenance Engineer',
                'focus': 'Equipment health, preventive maintenance, reliability',
                'bias': 'Prioritizes machine longevity and safety'
            },
            'financial_analyst': {
                'name': 'Financial Analyst',
                'focus': 'Cost optimization, ROI, budget constraints',
                'bias': 'Prioritizes cost-effective solutions'
            },
            'safety_officer': {
                'name': 'Safety Officer',
                'focus': 'Worker safety, compliance, risk mitigation',
                'bias': 'Prioritizes safety over productivity'
            }
        }
        
        if GENAI_AVAILABLE and api_key:
            try:
                self.client = genai.Client(api_key=api_key)
                self.send_message("✅ Debate Agent initialized with Gemini", "SUCCESS")
            except Exception as e:
                self.send_message(f"⚠️ Failed to initialize Gemini client: {e}", "WARNING")
    
    def conduct_debate(self, context: Dict[str, Any], topic: str, rounds: int = 2) -> Dict[str, Any]:
        """
        Conduct a multi-round debate between expert perspectives.
        
        Args:
            context: Dictionary containing relevant data and analysis
            topic: The topic/question to debate
            rounds: Number of debate rounds
            
        Returns:
            Dictionary containing debate transcript, arguments, and consensus
        """
        self.set_state("debating")
        self.send_message(f"🎭 Starting debate on: {topic}")
        
        debate_log = []
        expert_arguments = {expert: [] for expert in self.experts.keys()}
        
        # Round 1: Initial positions
        self.send_message("📢 Round 1: Initial Positions", "DEBUG")
        for expert_id, expert_info in self.experts.items():
            argument = self._get_expert_argument(context, topic, expert_info, round_num=1)
            expert_arguments[expert_id].append(argument)
            debate_log.append({
                'round': 1,
                'expert': expert_info['name'],
                'argument': argument
            })
            self.send_message(f"  💬 {expert_info['name']}: Position stated", "DEBUG")
        
        # Round 2+: Rebuttals and refinements
        for round_num in range(2, rounds + 1):
            self.send_message(f"📢 Round {round_num}: Rebuttals", "DEBUG")
            
            for expert_id, expert_info in self.experts.items():
                # Get other experts' arguments from previous round
                other_arguments = [
                    {'expert': self.experts[eid]['name'], 'argument': args[-1]}
                    for eid, args in expert_arguments.items()
                    if eid != expert_id and args
                ]
                
                argument = self._get_expert_rebuttal(
                    context, topic, expert_info, other_arguments, round_num
                )
                expert_arguments[expert_id].append(argument)
                debate_log.append({
                    'round': round_num,
                    'expert': expert_info['name'],
                    'argument': argument
                })
        
        # Synthesis: Find consensus
        self.send_message("🤝 Synthesizing debate conclusions...", "DEBUG")
        consensus = self._synthesize_consensus(context, topic, expert_arguments)
        
        self.set_state("completed")
        self.send_message("✅ Debate completed and consensus reached", "SUCCESS")
        
        result = {
            'topic': topic,
            'rounds': rounds,
            'debate_log': debate_log,
            'expert_arguments': expert_arguments,
            'consensus': consensus,
            'status': 'success'
        }
        
        self.debate_history.append(result)
        self.update_shared_context('last_debate', result)
        
        return result
    
    def _get_expert_argument(self, context: Dict[str, Any], topic: str, 
                             expert: Dict[str, str], round_num: int) -> str:
        """Generate an expert's initial argument."""
        
        summary = context.get('summary', {})
        anomalies = context.get('anomalies', {})
        
        prompt = f"""You are a {expert['name']} in an industrial facility.
Your focus area: {expert['focus']}
Your typical bias: {expert['bias']}

## FACILITY DATA:
- Total Machines: {summary.get('total_machines', 'N/A')}
- Average Utilization: {summary.get('avg_utilization', 0):.2%}
- Critical Machines: {summary.get('critical_machine_count', 0)}
- High Temperature Alerts: {len(anomalies.get('high_temperature', []))}
- Maintenance Overdue: {len(anomalies.get('maintenance_overdue', []))}

## DEBATE TOPIC:
{topic}

## YOUR TASK:
Present your position on this topic from your expert perspective.
- State your main argument clearly
- Provide 2-3 supporting points based on the data
- Explain the implications from your perspective
- Keep response under 200 words

YOUR ARGUMENT:"""
        
        try:
            if self.client:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                return response.text
            else:
                return self._fallback_argument(expert, topic, context)
        except Exception as e:
            self.send_message(f"⚠️ Error generating argument: {e}", "WARNING")
            return self._fallback_argument(expert, topic, context)
    
    def _get_expert_rebuttal(self, context: Dict[str, Any], topic: str,
                             expert: Dict[str, str], other_arguments: List[Dict],
                             round_num: int) -> str:
        """Generate an expert's rebuttal to other arguments."""
        
        summary = context.get('summary', {})
        
        others_text = "\n\n".join([
            f"**{arg['expert']}**: {arg['argument']}"
            for arg in other_arguments
        ])
        
        prompt = f"""You are a {expert['name']} in an industrial facility.
Your focus area: {expert['focus']}

## DEBATE TOPIC:
{topic}

## OTHER EXPERTS' ARGUMENTS:
{others_text}

## YOUR TASK (Round {round_num}):
Respond to the other experts' arguments:
- Acknowledge valid points from others
- Counter arguments that conflict with your perspective
- Refine your position based on new information
- Propose potential compromises where possible
- Keep response under 150 words

YOUR REBUTTAL:"""
        
        try:
            if self.client:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                return response.text
            else:
                return f"[{expert['name']}] Acknowledges other perspectives while maintaining focus on {expert['focus']}."
        except Exception as e:
            return f"[{expert['name']}] Technical response focused on {expert['focus']}."
    
    def _synthesize_consensus(self, context: Dict[str, Any], topic: str,
                              expert_arguments: Dict[str, List[str]]) -> Dict[str, Any]:
        """Synthesize debate into consensus conclusions."""
        
        # Prepare arguments summary
        args_summary = ""
        for expert_id, arguments in expert_arguments.items():
            expert_name = self.experts[expert_id]['name']
            args_summary += f"\n**{expert_name}**:\n"
            for i, arg in enumerate(arguments, 1):
                args_summary += f"Round {i}: {arg[:200]}...\n"
        
        prompt = f"""You are a neutral moderator synthesizing a debate.

## DEBATE TOPIC:
{topic}

## EXPERT ARGUMENTS SUMMARY:
{args_summary}

## YOUR TASK:
Synthesize the debate into actionable conclusions:

1. **AREAS OF AGREEMENT**: What do all experts agree on?

2. **KEY TENSIONS**: What are the main disagreements?

3. **RECOMMENDED ACTIONS**: List 3-5 prioritized actions that balance all perspectives

4. **DECISION RATIONALE**: Explain why these recommendations balance competing needs

5. **RISK ACKNOWLEDGMENT**: What risks remain even with these recommendations?

FORMAT your response with these exact headers."""
        
        try:
            if self.client:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                consensus_text = response.text
            else:
                consensus_text = self._fallback_consensus(topic, expert_arguments)
            
            return {
                'text': consensus_text,
                'status': 'success'
            }
        except Exception as e:
            return {
                'text': self._fallback_consensus(topic, expert_arguments),
                'status': 'fallback'
            }
    
    def _fallback_argument(self, expert: Dict[str, str], topic: str, 
                           context: Dict[str, Any]) -> str:
        """Generate fallback argument when LLM unavailable."""
        summary = context.get('summary', {})
        
        templates = {
            'operations_manager': f"From an operations standpoint, we need to prioritize uptime. With {summary.get('critical_machine_count', 0)} critical machines, we should focus on quick fixes to restore production capacity.",
            'maintenance_engineer': f"Maintenance data shows {len(context.get('anomalies', {}).get('maintenance_overdue', []))} machines overdue for maintenance. We need scheduled downtime for proper repairs.",
            'financial_analyst': f"Budget considerations require cost-effective solutions. ROI analysis should guide which machines get priority attention.",
            'safety_officer': f"Safety must come first. High temperature and vibration anomalies indicate potential hazards that need immediate attention."
        }
        
        for key, template in templates.items():
            if key in expert['name'].lower().replace(' ', '_'):
                return template
        
        return f"[{expert['name']}] Analysis focused on {expert['focus']}."
    
    def _fallback_consensus(self, topic: str, expert_arguments: Dict) -> str:
        """Generate fallback consensus when LLM unavailable."""
        return f"""
CONSENSUS SUMMARY (Fallback Mode)

Topic: {topic}

AREAS OF AGREEMENT:
• All experts agree that data-driven decisions are essential
• Machine health monitoring is critical
• Balance between productivity and safety is needed

RECOMMENDED ACTIONS:
1. Address critical safety issues immediately
2. Schedule maintenance for overdue machines
3. Implement monitoring for high-risk equipment
4. Review budget allocation for maintenance
5. Develop preventive maintenance schedule

RATIONALE:
These recommendations balance operational needs with safety and cost considerations.
"""
    
    def get_debate_summary(self) -> str:
        """Get a summary of all debates conducted."""
        if not self.debate_history:
            return "No debates conducted yet."
        
        summary = ["📊 DEBATE HISTORY SUMMARY", "=" * 40]
        for i, debate in enumerate(self.debate_history, 1):
            summary.append(f"\nDebate {i}: {debate['topic']}")
            summary.append(f"Rounds: {debate['rounds']}")
            summary.append(f"Status: {debate['status']}")
        
        return "\n".join(summary)
