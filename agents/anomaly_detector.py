"""
Anomaly Detector Agent - Responsible for identifying statistical anomalies and outliers
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from agents.base_agent import BaseAgent


class AnomalyDetectorAgent(BaseAgent):
    """
    Agent responsible for detecting anomalies in industrial data.
    Uses statistical methods to identify outliers and unusual patterns.
    """
    
    def __init__(self, name: str = "AnomalyDetector"):
        super().__init__(name, role="Anomaly Detection Specialist")
        
        # Configurable thresholds
        self.thresholds = {
            'percentile_high': 0.95,
            'percentile_low': 0.05,
            'z_score_threshold': 3.0,
            'iqr_multiplier': 1.5
        }
    
    def detect_anomalies(self, df: pd.DataFrame, summary: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Detect anomalies across multiple dimensions.
        
        Args:
            df: DataFrame with computed KPIs
            summary: Optional analysis summary from AnalysisAgent
            
        Returns:
            Dictionary containing detected anomalies by category
        """
        self.set_state("detecting")
        self.send_message("🔍 Scanning for anomalies...")
        
        if summary is None:
            summary = {}
        
        anomalies = {}
        anomaly_details = {}
        
        # 1. Temperature Anomalies
        if 'Temperature_C' in df.columns:
            high_temp_threshold = df['Temperature_C'].quantile(self.thresholds['percentile_high'])
            anomalies['high_temperature'] = df[df['Temperature_C'] > high_temp_threshold]['Machine_ID'].tolist()
            anomaly_details['high_temperature'] = {
                'threshold': round(high_temp_threshold, 2),
                'count': len(anomalies['high_temperature']),
                'severity': 'HIGH' if len(anomalies['high_temperature']) > 5 else 'MEDIUM'
            }
        
        # 2. Vibration Anomalies
        if 'Vibration_mms' in df.columns:
            high_vib_threshold = df['Vibration_mms'].quantile(self.thresholds['percentile_high'])
            anomalies['high_vibration'] = df[df['Vibration_mms'] > high_vib_threshold]['Machine_ID'].tolist()
            anomaly_details['high_vibration'] = {
                'threshold': round(high_vib_threshold, 2),
                'count': len(anomalies['high_vibration']),
                'severity': 'HIGH' if len(anomalies['high_vibration']) > 5 else 'MEDIUM'
            }
        
        # 3. Energy Spikes
        if 'Energy_Efficiency' in df.columns:
            energy_threshold = df['Energy_Efficiency'].quantile(self.thresholds['percentile_high'])
            anomalies['energy_spikes'] = df[df['Energy_Efficiency'] > energy_threshold]['Machine_ID'].tolist()
            anomaly_details['energy_spikes'] = {
                'threshold': round(energy_threshold, 4),
                'count': len(anomalies['energy_spikes']),
                'severity': 'MEDIUM'
            }
        
        # 4. Zero/Low Utilization (Idle Machines)
        if 'Utilization_Rate' in df.columns:
            anomalies['zero_utilization'] = df[df['Utilization_Rate'] == 0]['Machine_ID'].tolist()
            anomalies['very_low_utilization'] = df[
                (df['Utilization_Rate'] > 0) & (df['Utilization_Rate'] < 0.1)
            ]['Machine_ID'].tolist()
            anomaly_details['zero_utilization'] = {
                'count': len(anomalies['zero_utilization']),
                'severity': 'CRITICAL' if anomalies['zero_utilization'] else 'OK'
            }
        
        # 5. Sound Level Anomalies
        if 'Sound_dB' in df.columns:
            high_sound_threshold = df['Sound_dB'].quantile(self.thresholds['percentile_high'])
            anomalies['high_sound'] = df[df['Sound_dB'] > high_sound_threshold]['Machine_ID'].tolist()
            anomaly_details['high_sound'] = {
                'threshold': round(high_sound_threshold, 2),
                'count': len(anomalies['high_sound']),
                'severity': 'MEDIUM'
            }
        
        # 6. Maintenance Overdue
        if 'Last_Maintenance_Days_Ago' in df.columns:
            anomalies['maintenance_overdue'] = df[df['Last_Maintenance_Days_Ago'] > 180]['Machine_ID'].tolist()
            anomalies['maintenance_critical'] = df[df['Last_Maintenance_Days_Ago'] > 365]['Machine_ID'].tolist()
            anomaly_details['maintenance_overdue'] = {
                'threshold_days': 180,
                'count': len(anomalies['maintenance_overdue']),
                'critical_count': len(anomalies['maintenance_critical']),
                'severity': 'HIGH' if len(anomalies['maintenance_critical']) > 0 else 'MEDIUM'
            }
        
        # 7. High Error Rate
        if 'Error_Codes_Last_30_Days' in df.columns:
            error_threshold = df['Error_Codes_Last_30_Days'].quantile(0.9)
            anomalies['high_error_rate'] = df[df['Error_Codes_Last_30_Days'] > error_threshold]['Machine_ID'].tolist()
            anomaly_details['high_error_rate'] = {
                'threshold': int(error_threshold),
                'count': len(anomalies['high_error_rate']),
                'severity': 'HIGH' if len(anomalies['high_error_rate']) > 3 else 'MEDIUM'
            }
        
        # 8. AI Override Anomalies
        if 'AI_Override_Rate' in df.columns:
            override_threshold = df['AI_Override_Rate'].quantile(0.95)
            anomalies['high_ai_override'] = df[df['AI_Override_Rate'] > override_threshold]['Machine_ID'].tolist()
            anomaly_details['high_ai_override'] = {
                'threshold': round(override_threshold, 4),
                'count': len(anomalies['high_ai_override']),
                'severity': 'MEDIUM'
            }
        
        # 9. Multi-factor Anomalies (machines with multiple issues)
        anomalies['multi_factor_critical'] = self._find_multi_factor_anomalies(df, anomalies)
        
        # Calculate totals
        total_anomalies = sum(len(v) for k, v in anomalies.items() if isinstance(v, list))
        
        self.set_state("detected")
        self.send_message(f"🔍 Detected {total_anomalies} total anomalies across {len(anomalies)} categories", "SUCCESS")
        
        # Log critical findings
        for category, details in anomaly_details.items():
            if details.get('severity') in ['HIGH', 'CRITICAL']:
                self.send_message(f"  ⚠️ {category}: {details['count']} machines - {details['severity']}", "WARNING")
        
        result = {
            'anomalies': anomalies,
            'details': anomaly_details,
            'total_count': total_anomalies,
            'summary': self._generate_anomaly_summary(anomalies, anomaly_details)
        }
        
        self.update_shared_context("anomaly_detection", result)
        
        return anomalies
    
    def _find_multi_factor_anomalies(self, df: pd.DataFrame, anomalies: Dict) -> List[str]:
        """Find machines that appear in multiple anomaly categories."""
        all_anomaly_machines = []
        
        for category, machines in anomalies.items():
            if isinstance(machines, list):
                all_anomaly_machines.extend(machines)
        
        # Count occurrences
        from collections import Counter
        machine_counts = Counter(all_anomaly_machines)
        
        # Return machines with 3+ anomaly types
        return [machine for machine, count in machine_counts.items() if count >= 3]
    
    def _generate_anomaly_summary(self, anomalies: Dict, details: Dict) -> str:
        """Generate a text summary of anomalies."""
        lines = ["📊 ANOMALY DETECTION SUMMARY", "=" * 40]
        
        for category, machines in anomalies.items():
            if isinstance(machines, list) and len(machines) > 0:
                severity = details.get(category, {}).get('severity', 'INFO')
                severity_icon = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'OK': '🟢'}.get(severity, '⚪')
                lines.append(f"{severity_icon} {category}: {len(machines)} machines")
        
        return "\n".join(lines)
    
    def get_priority_list(self, anomalies: Dict) -> List[Tuple[str, str, str]]:
        """
        Generate a prioritized list of anomalies for action.
        
        Returns:
            List of tuples (machine_id, anomaly_type, priority)
        """
        priority_list = []
        
        # Critical priorities
        for machine in anomalies.get('multi_factor_critical', []):
            priority_list.append((machine, 'Multi-factor Critical', 'P1'))
        
        for machine in anomalies.get('maintenance_critical', []):
            if machine not in [p[0] for p in priority_list]:
                priority_list.append((machine, 'Maintenance Critical', 'P1'))
        
        # High priorities
        for machine in anomalies.get('high_temperature', []):
            if machine not in [p[0] for p in priority_list]:
                priority_list.append((machine, 'High Temperature', 'P2'))
        
        for machine in anomalies.get('high_vibration', []):
            if machine not in [p[0] for p in priority_list]:
                priority_list.append((machine, 'High Vibration', 'P2'))
        
        return sorted(priority_list, key=lambda x: x[2])
