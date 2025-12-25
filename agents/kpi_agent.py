"""
KPI Agent - Responsible for calculating key performance indicators
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class KPIAgent(BaseAgent):
    """
    Agent responsible for calculating and monitoring Key Performance Indicators.
    Computes operational efficiency, energy metrics, stability indices, and risk scores.
    """
    
    def __init__(self, name: str = "KPI Calculator"):
        super().__init__(name, role="Performance Analytics Specialist")
        self.kpi_definitions = {}
        self.computed_kpis = []
    
    def compute_kpis(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute all KPIs and add them as new columns.
        
        Args:
            df: Preprocessed DataFrame
            
        Returns:
            DataFrame enriched with KPI columns
        """
        self.set_state("computing")
        self.send_message("📊 Computing Key Performance Indicators...")
        
        df = df.copy()
        current_year = datetime.now().year
        
        # 1. Machine Age
        if 'Installation_Year' in df.columns:
            df['Machine_Age'] = current_year - df['Installation_Year']
            self.computed_kpis.append('Machine_Age')
            self.send_message("  ✓ Machine_Age calculated", "DEBUG")
        
        # 2. Utilization Rate (assuming 24/7 operation capacity)
        if 'Operational_Hours' in df.columns:
            df['Utilization_Rate'] = np.clip(df['Operational_Hours'] / (24 * 365), 0, 1)
            self.computed_kpis.append('Utilization_Rate')
            self.send_message("  ✓ Utilization_Rate calculated", "DEBUG")
        
        # 3. Energy Efficiency
        if 'Power_Consumption_kW' in df.columns and 'Operational_Hours' in df.columns:
            df['Energy_Efficiency'] = np.where(
                df['Operational_Hours'] > 0,
                df['Power_Consumption_kW'] / df['Operational_Hours'],
                np.nan
            )
            self.computed_kpis.append('Energy_Efficiency')
            self.send_message("  ✓ Energy_Efficiency calculated", "DEBUG")
        
        # 4. Stability Index (composite metric from sensors)
        stability_cols = ['Temperature_C', 'Vibration_mms', 'Sound_dB']
        available_stability_cols = [col for col in stability_cols if col in df.columns]
        
        if available_stability_cols:
            # Normalize each metric to 0-100 scale before averaging
            for col in available_stability_cols:
                col_min = df[col].min()
                col_max = df[col].max()
                if col_max > col_min:
                    df[f'{col}_normalized'] = (df[col] - col_min) / (col_max - col_min) * 100
                else:
                    df[f'{col}_normalized'] = 50
            
            normalized_cols = [f'{col}_normalized' for col in available_stability_cols]
            df['Stability_Index'] = df[normalized_cols].mean(axis=1)
            
            # Clean up temporary columns
            df.drop(columns=normalized_cols, inplace=True)
            self.computed_kpis.append('Stability_Index')
            self.send_message("  ✓ Stability_Index calculated", "DEBUG")
        
        # 5. AI Override Rate
        if 'AI_Override_Events' in df.columns and 'Operational_Hours' in df.columns:
            df['AI_Override_Rate'] = np.where(
                df['Operational_Hours'] > 0,
                df['AI_Override_Events'] / df['Operational_Hours'] * 1000,  # Per 1000 hours
                0
            )
            self.computed_kpis.append('AI_Override_Rate')
            self.send_message("  ✓ AI_Override_Rate calculated", "DEBUG")
        
        # 6. Maintenance Urgency Score
        if 'Last_Maintenance_Days_Ago' in df.columns and 'Failure_History_Count' in df.columns:
            df['Maintenance_Urgency'] = (
                df['Last_Maintenance_Days_Ago'] / 365 * 0.4 +  # Days since maintenance
                df['Failure_History_Count'] / df['Failure_History_Count'].max() * 0.3 +  # Failure history
                (1 - df['Utilization_Rate']) * 0.3 if 'Utilization_Rate' in df.columns else 0  # Low utilization
            )
            df['Maintenance_Urgency'] = np.clip(df['Maintenance_Urgency'], 0, 1)
            self.computed_kpis.append('Maintenance_Urgency')
            self.send_message("  ✓ Maintenance_Urgency calculated", "DEBUG")
        
        # 7. Health Score (inverse of risk factors)
        risk_factors = []
        if 'Temperature_C' in df.columns:
            temp_risk = (df['Temperature_C'] - df['Temperature_C'].min()) / (df['Temperature_C'].max() - df['Temperature_C'].min())
            risk_factors.append(temp_risk)
        if 'Vibration_mms' in df.columns:
            vib_risk = (df['Vibration_mms'] - df['Vibration_mms'].min()) / (df['Vibration_mms'].max() - df['Vibration_mms'].min())
            risk_factors.append(vib_risk)
        if 'Error_Codes_Last_30_Days' in df.columns:
            error_risk = df['Error_Codes_Last_30_Days'] / df['Error_Codes_Last_30_Days'].max()
            risk_factors.append(error_risk)
        
        if risk_factors:
            df['Health_Score'] = 100 * (1 - pd.concat(risk_factors, axis=1).mean(axis=1))
            df['Health_Score'] = np.clip(df['Health_Score'], 0, 100)
            self.computed_kpis.append('Health_Score')
            self.send_message("  ✓ Health_Score calculated", "DEBUG")
        
        # 8. Risk Category
        if 'Health_Score' in df.columns:
            df['Risk_Category'] = pd.cut(
                df['Health_Score'],
                bins=[0, 30, 60, 80, 100],
                labels=['Critical', 'High', 'Medium', 'Low']
            )
            self.computed_kpis.append('Risk_Category')
        
        self.set_state("computed")
        self.send_message(f"✅ Computed {len(self.computed_kpis)} KPIs successfully", "SUCCESS")
        
        # Store KPI summary in shared context
        self.update_shared_context("computed_kpis", self.computed_kpis)
        
        return df
    
    def get_kpi_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate a summary of all computed KPIs."""
        summary = {}
        
        for kpi in self.computed_kpis:
            if kpi in df.columns:
                if df[kpi].dtype in ['float64', 'float32', 'int64', 'int32']:
                    summary[kpi] = {
                        'mean': round(df[kpi].mean(), 4),
                        'median': round(df[kpi].median(), 4),
                        'std': round(df[kpi].std(), 4),
                        'min': round(df[kpi].min(), 4),
                        'max': round(df[kpi].max(), 4)
                    }
                else:
                    summary[kpi] = df[kpi].value_counts().to_dict()
        
        return summary
    
    def identify_critical_machines(self, df: pd.DataFrame, threshold: float = 0.4) -> List[str]:
        """Identify machines with utilization rate below threshold."""
        if 'Utilization_Rate' not in df.columns:
            return []
        
        critical = df[df['Utilization_Rate'] < threshold]['Machine_ID'].tolist()
        self.send_message(f"🚨 Identified {len(critical)} critical machines (utilization < {threshold:.0%})")
        return critical
