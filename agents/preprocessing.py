"""
Preprocessing Agent - Responsible for data cleaning and transformation
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent


class PreprocessingAgent(BaseAgent):
    """
    Agent responsible for cleaning and preparing data for analysis.
    Handles missing values, type conversions, and feature engineering.
    """
    
    def __init__(self, name: str = "Preprocessor"):
        super().__init__(name, role="Data Engineering Specialist")
        self.cleaning_report = {}
        
        # Columns that should be numeric
        self.numeric_columns = [
            'Operational_Hours', 'Power_Consumption_kW', 'Temperature_C',
            'Vibration_mms', 'Sound_dB', 'AI_Override_Events',
            'Installation_Year', 'Oil_Level_pct', 'Coolant_Level_pct',
            'Last_Maintenance_Days_Ago', 'Maintenance_History_Count',
            'Failure_History_Count', 'Error_Codes_Last_30_Days',
            'Remaining_Useful_Life_days', 'Laser_Intensity',
            'Hydraulic_Pressure_bar', 'Coolant_Flow_L_min', 'Heat_Index'
        ]
    
    def clean_data(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and prepare data for analysis.
        
        Args:
            validation_result: Result from ValidationAgent containing validated data
            
        Returns:
            Dictionary with cleaned data and cleaning report
        """
        self.set_state("cleaning")
        self.send_message("🧹 Starting data cleaning and preparation...")
        
        df = validation_result["data"].copy()
        initial_rows = len(df)
        initial_nulls = df.isnull().sum().sum()
        
        cleaning_steps = []
        
        # Step 1: Convert to numeric types
        converted_cols = self._convert_numeric_columns(df)
        if converted_cols:
            cleaning_steps.append(f"Converted {len(converted_cols)} columns to numeric")
        
        # Step 2: Handle invalid Operational_Hours
        if 'Operational_Hours' in df.columns:
            invalid_hours = (df['Operational_Hours'] <= 0).sum()
            df = df[df['Operational_Hours'] > 0]
            if invalid_hours > 0:
                cleaning_steps.append(f"Removed {invalid_hours} rows with invalid Operational_Hours")
        
        # Step 3: Handle extreme outliers in critical columns
        outlier_info = self._handle_outliers(df)
        if outlier_info:
            cleaning_steps.append(outlier_info)
        
        # Step 4: Fill missing values
        fill_info = self._fill_missing_values(df)
        if fill_info:
            cleaning_steps.append(fill_info)
        
        # Step 5: Remove remaining rows with critical NaN
        critical_cols = ['Machine_ID', 'Machine_Type', 'Operational_Hours']
        for col in critical_cols:
            if col in df.columns:
                before = len(df)
                df = df.dropna(subset=[col])
                dropped = before - len(df)
                if dropped > 0:
                    cleaning_steps.append(f"Dropped {dropped} rows with NaN in {col}")
        
        # Step 6: Ensure Installation_Year is valid
        if 'Installation_Year' in df.columns:
            current_year = pd.Timestamp.now().year
            invalid_years = ((df['Installation_Year'] < 1990) | (df['Installation_Year'] > current_year + 5)).sum()
            df.loc[(df['Installation_Year'] < 1990) | (df['Installation_Year'] > current_year + 5), 'Installation_Year'] = np.nan
            df['Installation_Year'] = df['Installation_Year'].fillna(df['Installation_Year'].median())
            if invalid_years > 0:
                cleaning_steps.append(f"Corrected {invalid_years} invalid Installation_Year values")
        
        # Generate cleaning report
        final_rows = len(df)
        final_nulls = df.isnull().sum().sum()
        
        self.cleaning_report = {
            "initial_rows": initial_rows,
            "final_rows": final_rows,
            "rows_removed": initial_rows - final_rows,
            "removal_rate": round((initial_rows - final_rows) / initial_rows * 100, 2) if initial_rows > 0 else 0,
            "initial_nulls": initial_nulls,
            "final_nulls": final_nulls,
            "nulls_handled": initial_nulls - final_nulls,
            "cleaning_steps": cleaning_steps
        }
        
        self.set_state("cleaned")
        self.send_message(
            f"✅ Cleaning complete: {final_rows}/{initial_rows} rows retained "
            f"({self.cleaning_report['removal_rate']:.1f}% removed)",
            "SUCCESS"
        )
        
        self.update_shared_context("cleaning_report", self.cleaning_report)
        
        return {
            "data": df,
            "cleaning_report": self.cleaning_report
        }
    
    def _convert_numeric_columns(self, df: pd.DataFrame) -> List[str]:
        """Convert columns to numeric types."""
        converted = []
        
        for col in self.numeric_columns:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    converted.append(col)
        
        return converted
    
    def _handle_outliers(self, df: pd.DataFrame, method: str = 'cap') -> Optional[str]:
        """
        Handle outliers using IQR method.
        
        Args:
            df: DataFrame to process (modified in place)
            method: 'cap' to cap values, 'remove' to remove rows
        """
        outlier_cols = ['Temperature_C', 'Vibration_mms', 'Sound_dB', 'Power_Consumption_kW']
        total_capped = 0
        
        for col in outlier_cols:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                Q1 = df[col].quantile(0.01)
                Q3 = df[col].quantile(0.99)
                
                if method == 'cap':
                    lower_outliers = (df[col] < Q1).sum()
                    upper_outliers = (df[col] > Q3).sum()
                    df[col] = df[col].clip(lower=Q1, upper=Q3)
                    total_capped += lower_outliers + upper_outliers
        
        if total_capped > 0:
            return f"Capped {total_capped} outlier values (1st-99th percentile)"
        return None
    
    def _fill_missing_values(self, df: pd.DataFrame) -> Optional[str]:
        """Fill missing values with appropriate strategies."""
        fill_count = 0
        
        # Numeric columns: fill with median
        for col in self.numeric_columns:
            if col in df.columns:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    df[col] = df[col].fillna(df[col].median())
                    fill_count += null_count
        
        # Boolean columns: fill with mode
        bool_cols = ['AI_Supervision', 'Failure_Within_7_Days']
        for col in bool_cols:
            if col in df.columns:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    mode_val = df[col].mode()[0] if len(df[col].mode()) > 0 else False
                    df[col] = df[col].fillna(mode_val)
                    fill_count += null_count
        
        if fill_count > 0:
            return f"Filled {fill_count} missing values (median for numeric, mode for boolean)"
        return None
    
    def get_cleaning_summary(self) -> str:
        """Generate a human-readable cleaning summary."""
        if not self.cleaning_report:
            return "No cleaning has been performed yet."
        
        summary = [
            "📊 Data Cleaning Summary:",
            f"  • Initial rows: {self.cleaning_report['initial_rows']}",
            f"  • Final rows: {self.cleaning_report['final_rows']}",
            f"  • Rows removed: {self.cleaning_report['rows_removed']} ({self.cleaning_report['removal_rate']:.1f}%)",
            f"  • Null values handled: {self.cleaning_report['nulls_handled']}",
            "",
            "📝 Cleaning Steps:"
        ]
        
        for step in self.cleaning_report.get('cleaning_steps', []):
            summary.append(f"  • {step}")
        
        return "\n".join(summary)
