"""
Final Validation Agent - Performs final validation before report publication
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class FinalValidationAgent(BaseAgent):
    """
    Agent responsible for final validation of reports before publication.
    Ensures completeness, consistency, and quality standards.
    """
    
    def __init__(self, name: str = "FinalValidator"):
        super().__init__(name, role="Final Quality Assurance Specialist")
        
        # Required sections in the report
        self.required_sections = [
            "KPI",
            "ANOMALIES",
            "DÉCISIONS",
            "TRAÇABILITÉ"
        ]
        
        # Minimum content requirements
        self.min_requirements = {
            'min_length': 1000,           # Minimum characters
            'min_decisions': 1,           # At least one decision
            'max_critical_without_urgent': 5  # If >5 critical issues, priority should be URGENT
        }
    
    def validate_report(self, report: str, decisions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform final validation on the report before publication.
        
        Args:
            report: The generated report string
            decisions: Decision record for consistency checking
            
        Returns:
            Validation result with issues and recommendations
        """
        self.set_state("validating")
        self.send_message("🔍 Performing final report validation...")
        
        issues = []
        warnings = []
        
        # 1. Check minimum length
        if len(report) < self.min_requirements['min_length']:
            issues.append(f"Report too short: {len(report)} chars (min: {self.min_requirements['min_length']})")
        
        # 2. Check required sections
        report_upper = report.upper()
        missing_sections = []
        for section in self.required_sections:
            if section not in report_upper:
                missing_sections.append(section)
        
        if missing_sections:
            issues.append(f"Missing required sections: {missing_sections}")
        
        # 3. Check decision consistency
        decision_list = decisions.get('decisions', [])
        priority = decisions.get('priority', 'NORMAL')
        action_needed = decisions.get('action_needed', False)
        
        # If action needed but no decisions
        if action_needed and len(decision_list) == 0:
            issues.append("Action marked as needed but no decisions provided")
        
        # If many P1 decisions but not URGENT
        p1_count = sum(1 for d in decision_list if d.get('priority') == 'P1')
        if p1_count >= 3 and priority != "URGENT":
            warnings.append(f"Multiple P1 decisions ({p1_count}) but priority is not URGENT")
        
        # 4. Check for placeholder text
        placeholder_markers = ['[TODO]', '[PLACEHOLDER]', '[INSERT]', 'N/A', 'null', 'undefined']
        found_placeholders = [p for p in placeholder_markers if p in report]
        if found_placeholders:
            warnings.append(f"Potential placeholder text found: {found_placeholders}")
        
        # 5. Check format integrity
        format_issues = self._check_format(report)
        warnings.extend(format_issues)
        
        # 6. Check date/timestamp presence
        if '2024' not in report and '2025' not in report:
            warnings.append("Report may be missing timestamp")
        
        # 7. Check for balanced content
        sections_found = sum(1 for s in self.required_sections if s in report_upper)
        if sections_found < len(self.required_sections) * 0.75:
            warnings.append(f"Report may be unbalanced: only {sections_found}/{len(self.required_sections)} sections found")
        
        # Determine validation result
        is_valid = len(issues) == 0
        
        if is_valid:
            self.send_message(f"✅ Report validated successfully ({len(warnings)} warnings)", "SUCCESS")
        else:
            self.send_message(f"❌ Report validation failed: {issues}", "ERROR")
        
        self.set_state("validated")
        
        return {
            "valid": is_valid,
            "issues": issues,
            "warnings": warnings,
            "validation_score": self._calculate_validation_score(report, issues, warnings),
            "recommendations": self._generate_recommendations(issues, warnings)
        }
    
    def _check_format(self, report: str) -> List[str]:
        """Check report format integrity."""
        warnings = []
        
        # Check for broken formatting
        if report.count('╔') != report.count('╚'):
            warnings.append("Unbalanced box drawing characters")
        
        if report.count('┌') != report.count('└'):
            warnings.append("Unbalanced table characters")
        
        # Check for excessive whitespace
        if '\n\n\n\n' in report:
            warnings.append("Excessive blank lines in report")
        
        return warnings
    
    def _calculate_validation_score(self, report: str, issues: List, warnings: List) -> float:
        """Calculate overall validation score (0-100)."""
        score = 100.0
        
        # Deduct for issues
        score -= len(issues) * 25
        
        # Deduct for warnings
        score -= len(warnings) * 5
        
        # Bonus for length (up to +10)
        length_bonus = min(10, len(report) / 1000)
        score += length_bonus
        
        # Bonus for sections found
        report_upper = report.upper()
        sections_found = sum(1 for s in self.required_sections if s in report_upper)
        section_bonus = (sections_found / len(self.required_sections)) * 10
        score += section_bonus
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self, issues: List, warnings: List) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if any('section' in issue.lower() for issue in issues):
            recommendations.append("Add missing sections to ensure report completeness")
        
        if any('short' in issue.lower() for issue in issues):
            recommendations.append("Expand report content with more detailed analysis")
        
        if any('placeholder' in warning.lower() for warning in warnings):
            recommendations.append("Replace all placeholder text with actual content")
        
        if any('urgent' in warning.lower() for warning in warnings):
            recommendations.append("Review priority level given the number of critical issues")
        
        if not recommendations:
            recommendations.append("Report meets quality standards - ready for publication")
        
        return recommendations
    
    def quick_validate(self, report: str) -> bool:
        """Perform a quick validation check (returns True/False only)."""
        if len(report) < 500:
            return False
        
        report_upper = report.upper()
        essential_sections = ['KPI', 'DÉCISIONS']
        
        return all(section in report_upper for section in essential_sections)
