"""
Analysis Agent - Responsible for statistical analysis and insights generation
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from agents.base_agent import BaseAgent


class AnalysisAgent(BaseAgent):
    """
    Agent responsible for statistical analysis of KPI data.
    Generates insights, identifies patterns, and produces summary statistics.
    """
    
    def __init__(self, name: str = "Analyzer"):
        super().__init__(name, role="Data Analysis Specialist")
    
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on the enriched DataFrame.
        
        Args:
            df: DataFrame with computed KPIs
            
        Returns:
            Dictionary containing analysis results and insights
        """
        self.set_state("analyzing")
        self.send_message("📈 Performing comprehensive data analysis...")
        
        summary = {}
        
        # Core KPI Statistics
        if 'Utilization_Rate' in df.columns:
            summary['avg_utilization'] = round(df['Utilization_Rate'].mean(), 4)
            summary['median_utilization'] = round(df['Utilization_Rate'].median(), 4)
            summary['utilization_std'] = round(df['Utilization_Rate'].std(), 4)
        
        if 'Energy_Efficiency' in df.columns:
            summary['avg_energy_efficiency'] = round(df['Energy_Efficiency'].mean(), 4)
            summary['energy_efficiency_std'] = round(df['Energy_Efficiency'].std(), 4)
        
        if 'Stability_Index' in df.columns:
            summary['avg_stability'] = round(df['Stability_Index'].mean(), 2)
            summary['stability_std'] = round(df['Stability_Index'].std(), 2)
        
        if 'Health_Score' in df.columns:
            summary['avg_health_score'] = round(df['Health_Score'].mean(), 2)
            summary['min_health_score'] = round(df['Health_Score'].min(), 2)
        
        # Machine Classifications
        summary['total_machines'] = len(df)
        
        if 'Utilization_Rate' in df.columns:
            summary['machines_sous_utilisees'] = df[df['Utilization_Rate'] < 0.4]['Machine_ID'].tolist()
            summary['machines_well_utilized'] = df[df['Utilization_Rate'] >= 0.7]['Machine_ID'].tolist()
            summary['critical_machine_count'] = len(summary['machines_sous_utilisees'])
        
        if 'Stability_Index' in df.columns:
            stability_threshold = df['Stability_Index'].mean() + df['Stability_Index'].std()
            summary['machines_instables'] = df[df['Stability_Index'] > stability_threshold]['Machine_ID'].tolist()
        
        if 'Health_Score' in df.columns:
            summary['machines_critical_health'] = df[df['Health_Score'] < 50]['Machine_ID'].tolist()
            summary['machines_good_health'] = df[df['Health_Score'] >= 80]['Machine_ID'].tolist()
        
        # Risk Distribution
        if 'Risk_Category' in df.columns:
            summary['risk_distribution'] = df['Risk_Category'].value_counts().to_dict()
        
        # Machine Type Analysis
        if 'Machine_Type' in df.columns:
            summary['machine_type_counts'] = df['Machine_Type'].value_counts().to_dict()
            summary['machine_types'] = df['Machine_Type'].nunique()
            
            # Performance by machine type
            if 'Utilization_Rate' in df.columns:
                summary['utilization_by_type'] = df.groupby('Machine_Type')['Utilization_Rate'].mean().round(4).to_dict()
            
            if 'Health_Score' in df.columns:
                summary['health_by_type'] = df.groupby('Machine_Type')['Health_Score'].mean().round(2).to_dict()
        
        # Age Analysis
        if 'Machine_Age' in df.columns:
            summary['avg_machine_age'] = round(df['Machine_Age'].mean(), 1)
            summary['oldest_machines'] = df.nlargest(5, 'Machine_Age')[['Machine_ID', 'Machine_Age']].to_dict('records')
            summary['newest_machines'] = df.nsmallest(5, 'Machine_Age')[['Machine_ID', 'Machine_Age']].to_dict('records')
        
        # Maintenance Analysis
        if 'Last_Maintenance_Days_Ago' in df.columns:
            summary['avg_days_since_maintenance'] = round(df['Last_Maintenance_Days_Ago'].mean(), 1)
            summary['machines_overdue_maintenance'] = df[df['Last_Maintenance_Days_Ago'] > 180]['Machine_ID'].tolist()
        
        # Correlation Analysis
        correlations = self._compute_correlations(df)
        if correlations:
            summary['key_correlations'] = correlations
        
        # Trend Indicators
        summary['trend_indicators'] = self._compute_trend_indicators(df)
        
        self.set_state("analyzed")
        self.send_message(f"✅ Analysis complete: {len(summary)} metrics computed", "SUCCESS")
        
        self.update_shared_context("analysis_summary", summary)
        
        return summary
    
    def _compute_correlations(self, df: pd.DataFrame) -> Dict[str, float]:
        """Compute key correlations between metrics."""
        correlations = {}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Key correlation pairs
        correlation_pairs = [
            ('Utilization_Rate', 'Energy_Efficiency'),
            ('Machine_Age', 'Health_Score'),
            ('Temperature_C', 'Vibration_mms'),
            ('Operational_Hours', 'Failure_History_Count'),
            ('Last_Maintenance_Days_Ago', 'Health_Score')
        ]
        
        for col1, col2 in correlation_pairs:
            if col1 in numeric_cols and col2 in numeric_cols:
                corr = df[col1].corr(df[col2])
                if not np.isnan(corr):
                    correlations[f'{col1}_vs_{col2}'] = round(corr, 3)
        
        return correlations
    
    def _compute_trend_indicators(self, df: pd.DataFrame) -> Dict[str, str]:
        """Compute trend indicators for key metrics."""
        trends = {}
        
        if 'Utilization_Rate' in df.columns:
            if df['Utilization_Rate'].mean() < 0.5:
                trends['utilization'] = 'LOW - Action Required'
            elif df['Utilization_Rate'].mean() < 0.7:
                trends['utilization'] = 'MODERATE - Monitor'
            else:
                trends['utilization'] = 'GOOD - Maintain'
        
        if 'Health_Score' in df.columns:
            critical_pct = (df['Health_Score'] < 50).mean() * 100
            if critical_pct > 20:
                trends['health'] = f'CRITICAL - {critical_pct:.1f}% machines need attention'
            elif critical_pct > 10:
                trends['health'] = f'CONCERNING - {critical_pct:.1f}% machines at risk'
            else:
                trends['health'] = f'STABLE - {critical_pct:.1f}% machines critical'
        
        return trends
    
    def get_executive_summary(self, summary: Dict[str, Any]) -> str:
        """Generate a human-readable executive summary."""
        lines = [
            "═" * 50,
            "       EXECUTIVE SUMMARY",
            "═" * 50,
            "",
            f"📊 Total Machines Analyzed: {summary.get('total_machines', 'N/A')}",
            f"📈 Average Utilization: {summary.get('avg_utilization', 0):.1%}",
            f"⚡ Average Energy Efficiency: {summary.get('avg_energy_efficiency', 0):.2f} kW/h",
            f"💚 Average Health Score: {summary.get('avg_health_score', 0):.1f}/100",
            "",
            f"🚨 Critical Machines (Low Utilization): {summary.get('critical_machine_count', 0)}",
            f"⚠️ Machines Overdue Maintenance: {len(summary.get('machines_overdue_maintenance', []))}",
            f"❤️ Machines with Good Health: {len(summary.get('machines_good_health', []))}",
            "",
            "═" * 50
        ]
        
        return "\n".join(lines)
