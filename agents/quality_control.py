"""
Quality Control Agent - Validates LLM outputs and ensures response quality
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class QualityControlAgent(BaseAgent):
    """
    Agent responsible for validating the quality of LLM-generated outputs.
    Ensures consistency, completeness, and accuracy of insights.
    """
    
    def __init__(self, name: str = "QualityControl"):
        super().__init__(name, role="Quality Assurance Specialist")
        
        # Quality criteria
        self.criteria = {
            'min_length': 100,           # Minimum characters
            'max_length': 10000,         # Maximum characters
            'required_sections': ['problème', 'action', 'recommand'],  # Key terms
            'forbidden_terms': ['erreur', 'impossible', 'échec'],      # Warning terms
            'consistency_checks': True
        }
    
    def validate_llm_output(self, llm_result: Dict[str, Any], 
                            summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate LLM output for quality and consistency.
        
        Args:
            llm_result: Result from LLMInsightAgent
            summary: Analysis summary for consistency checking
            
        Returns:
            Validation result with issues and recommendations
        """
        self.set_state("validating")
        self.send_message("🔍 Validating LLM output quality...")
        
        text = llm_result.get("text", "")
        status = llm_result.get("status", "unknown")
        issues = []
        warnings = []
        
        # 1. Check response length
        if len(text) < self.criteria['min_length']:
            issues.append(f"Response too short: {len(text)} chars (min: {self.criteria['min_length']})")
        elif len(text) > self.criteria['max_length']:
            warnings.append(f"Response very long: {len(text)} chars")
        
        # 2. Check for fallback mode
        if status == "fallback":
            warnings.append("LLM response in fallback mode - may be less accurate")
        
        # 3. Check for required content sections
        text_lower = text.lower()
        missing_sections = []
        for section in self.criteria['required_sections']:
            if section not in text_lower:
                missing_sections.append(section)
        
        if missing_sections:
            warnings.append(f"Missing expected content: {missing_sections}")
        
        # 4. Check for warning terms
        found_forbidden = []
        for term in self.criteria['forbidden_terms']:
            if term in text_lower:
                found_forbidden.append(term)
        
        if found_forbidden:
            warnings.append(f"Contains concerning terms: {found_forbidden}")
        
        # 5. Consistency checks with data
        if self.criteria['consistency_checks']:
            consistency_issues = self._check_consistency(text, summary)
            issues.extend(consistency_issues)
        
        # 6. Check for actionable content
        actionable_terms = ['recommand', 'action', 'priorit', 'urgent', 'immédiat']
        has_actionable = any(term in text_lower for term in actionable_terms)
        
        if not has_actionable:
            warnings.append("Response may lack actionable recommendations")
        
        # Determine overall validity
        is_valid = len(issues) == 0
        retry_needed = len(issues) > 0 and status != "fallback"
        
        if is_valid:
            self.send_message(f"✅ LLM output validated ({len(warnings)} warnings)", "SUCCESS")
        else:
            self.send_message(f"⚠️ LLM output has issues: {issues}", "WARNING")
        
        self.set_state("validated")
        
        result = {
            "valid": is_valid,
            "issues": issues,
            "warnings": warnings,
            "retry_needed": retry_needed,
            "quality_score": self._calculate_quality_score(text, issues, warnings),
            "validation_details": {
                "length": len(text),
                "has_actionable_content": has_actionable,
                "missing_sections": missing_sections,
                "status_ok": status == "success"
            }
        }
        
        self.update_shared_context("quality_validation", result)
        
        return result
    
    def _check_consistency(self, text: str, summary: Dict[str, Any]) -> List[str]:
        """Check if LLM response is consistent with the data."""
        issues = []
        
        critical_count = summary.get('critical_machine_count', 0)
        total_machines = summary.get('total_machines', 1)
        
        # If many critical machines, response should mention urgency
        if critical_count > total_machines * 0.2:
            urgency_terms = ['urgent', 'critique', 'immédiat', 'priorit']
            text_lower = text.lower()
            if not any(term in text_lower for term in urgency_terms):
                issues.append(f"Response understates criticality ({critical_count} critical machines)")
        
        # If low average health, should mention health concerns
        avg_health = summary.get('avg_health_score', 100)
        if avg_health < 60:
            health_terms = ['santé', 'health', 'état', 'dégradé']
            text_lower = text.lower()
            if not any(term in text_lower for term in health_terms):
                issues.append(f"Response doesn't address low health scores (avg: {avg_health})")
        
        return issues
    
    def _calculate_quality_score(self, text: str, issues: List, warnings: List) -> float:
        """Calculate an overall quality score (0-100)."""
        score = 100.0
        
        # Deduct for issues
        score -= len(issues) * 20
        
        # Deduct for warnings
        score -= len(warnings) * 5
        
        # Length bonus/penalty
        length = len(text)
        if 500 <= length <= 3000:
            score += 5  # Ideal length bonus
        elif length < 200:
            score -= 10
        
        return max(0, min(100, score))
    
    def validate_reasoning(self, reasoning_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate reasoning agent output."""
        self.send_message("🔍 Validating reasoning output...")
        
        issues = []
        warnings = []
        
        steps = reasoning_result.get('steps', [])
        confidence = reasoning_result.get('confidence', 'LOW')
        
        # Check if reasoning has sufficient steps
        if len(steps) < 3:
            warnings.append(f"Reasoning lacks depth: only {len(steps)} steps")
        
        # Check confidence level
        if confidence == 'LOW':
            warnings.append("Low confidence in reasoning output")
        
        # Check for conclusions
        has_conclusion = any('conclusion' in step.get('step', '').lower() for step in steps)
        if not has_conclusion:
            issues.append("Reasoning lacks clear conclusion")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "confidence": confidence
        }
    
    def validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate planning agent output."""
        self.send_message("🔍 Validating action plan...")
        
        issues = []
        warnings = []
        
        phases = plan.get('phases', [])
        
        # Check if plan has phases
        if len(phases) < 2:
            issues.append("Plan lacks sufficient phases")
        
        # Check for metrics
        if not plan.get('metrics'):
            warnings.append("Plan lacks success metrics")
        
        # Check for risks
        if not plan.get('risks'):
            warnings.append("Plan doesn't address risks")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
