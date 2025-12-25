"""
Validation Agent - Responsible for data quality validation at multiple stages
"""

import pandas as pd
from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class ValidationAgent(BaseAgent):
    """
    Agent responsible for validating data quality at multiple stages of the pipeline.
    Implements validation rules for raw data, processed data, and outputs.
    """
    
    def __init__(self, name: str = "Validator"):
        super().__init__(name, role="Quality Assurance Specialist")
        
        # Configurable validation thresholds
        self.validation_config = {
            "min_rows": 10,
            "max_null_percentage": 0.3,
            "required_columns": [
                'Machine_ID', 'Machine_Type', 'Operational_Hours',
                'Power_Consumption_kW', 'Temperature_C', 'Vibration_mms',
                'Sound_dB', 'Installation_Year'
            ],
            "numeric_columns": [
                'Operational_Hours', 'Power_Consumption_kW',
                'Temperature_C', 'Vibration_mms', 'Sound_dB',
                'Installation_Year', 'AI_Override_Events'
            ],
            "value_ranges": {
                'Temperature_C': (0, 200),
                'Vibration_mms': (0, 100),
                'Sound_dB': (0, 150),
                'Operational_Hours': (0, 200000),
                'Power_Consumption_kW': (-50, 1000)
            }
        }
    
    def validate_raw_data(self, data_package: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate raw data before preprocessing.
        
        Args:
            data_package: Package from DataCollectorAgent containing data and metadata
            
        Returns:
            Validation result with status, issues, and cleaned data
        """
        self.set_state("validating_raw")
        self.send_message("🔍 Validating raw data quality...")
        
        df = data_package["data"]
        issues = []
        warnings = []
        
        # 1. Check minimum rows
        if len(df) < self.validation_config["min_rows"]:
            issues.append(f"Insufficient data: {len(df)} rows (minimum: {self.validation_config['min_rows']})")
        
        # 2. Check required columns
        missing_cols = set(self.validation_config["required_columns"]) - set(df.columns)
        if missing_cols:
            issues.append(f"Missing required columns: {missing_cols}")
        
        # 3. Check null percentage
        total_cells = len(df) * len(df.columns)
        null_cells = df.isnull().sum().sum()
        null_percentage = null_cells / total_cells if total_cells > 0 else 0
        
        if null_percentage > self.validation_config["max_null_percentage"]:
            issues.append(f"High null percentage: {null_percentage:.2%} (max: {self.validation_config['max_null_percentage']:.0%})")
        elif null_percentage > 0.1:
            warnings.append(f"Moderate null percentage: {null_percentage:.2%}")
        
        # 4. Check data types for numeric columns
        type_issues = []
        for col in self.validation_config["numeric_columns"]:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    # Try to convert
                    try:
                        pd.to_numeric(df[col], errors='raise')
                    except:
                        type_issues.append(col)
        
        if type_issues:
            warnings.append(f"Non-numeric data in expected numeric columns: {type_issues}")
        
        # 5. Check for duplicate Machine_IDs
        if 'Machine_ID' in df.columns:
            duplicates = df['Machine_ID'].duplicated().sum()
            if duplicates > 0:
                warnings.append(f"Found {duplicates} duplicate Machine_IDs")
        
        # 6. Check value ranges
        range_issues = self._check_value_ranges(df)
        if range_issues:
            warnings.extend(range_issues)
        
        # Determine validation result
        is_valid = len(issues) == 0
        
        if is_valid:
            self.send_message(f"✅ Raw data validation passed with {len(warnings)} warnings", "SUCCESS")
        else:
            self.send_message(f"❌ Raw data validation failed: {len(issues)} issues found", "ERROR")
        
        self.set_state("validated")
        
        return {
            "valid": is_valid,
            "issues": issues,
            "warnings": warnings,
            "data": df,
            "validation_stats": {
                "row_count": len(df),
                "column_count": len(df.columns),
                "null_percentage": null_percentage,
                "issues_count": len(issues),
                "warnings_count": len(warnings)
            }
        }
    
    def validate_processed_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate data after preprocessing.
        
        Args:
            df: Preprocessed DataFrame
            
        Returns:
            Validation result
        """
        self.set_state("validating_processed")
        self.send_message("🔍 Validating processed data...")
        
        issues = []
        warnings = []
        
        # 1. Check if too much data was lost
        if len(df) < 5:
            issues.append(f"Too much data lost during preprocessing: only {len(df)} rows remaining")
        
        # 2. Check for remaining NaN values
        nan_columns = df.columns[df.isnull().any()].tolist()
        if nan_columns:
            issues.append(f"NaN values persist after cleaning in columns: {nan_columns}")
        
        # 3. Check for infinite values
        numeric_df = df.select_dtypes(include=['number'])
        inf_columns = numeric_df.columns[(numeric_df == float('inf')).any() | (numeric_df == float('-inf')).any()].tolist()
        if inf_columns:
            issues.append(f"Infinite values found in columns: {inf_columns}")
        
        # 4. Check value ranges again after processing
        range_issues = self._check_value_ranges(df)
        if range_issues:
            warnings.extend(range_issues)
        
        # 5. Check for negative values where they shouldn't be
        negative_check_cols = ['Operational_Hours', 'Power_Consumption_kW']
        for col in negative_check_cols:
            if col in df.columns:
                negative_count = (df[col] < 0).sum()
                if negative_count > 0:
                    warnings.append(f"Found {negative_count} negative values in {col}")
        
        is_valid = len(issues) == 0
        
        if is_valid:
            self.send_message(f"✅ Processed data validation passed with {len(warnings)} warnings", "SUCCESS")
        else:
            self.send_message(f"❌ Processed data validation failed: {issues}", "ERROR")
        
        self.set_state("validated")
        
        return {
            "valid": is_valid,
            "issues": issues,
            "warnings": warnings,
            "data": df,
            "validation_stats": {
                "row_count": len(df),
                "nan_columns": nan_columns,
                "issues_count": len(issues)
            }
        }
    
    def _check_value_ranges(self, df: pd.DataFrame) -> List[str]:
        """Check if values fall within expected ranges."""
        issues = []
        
        for col, (min_val, max_val) in self.validation_config["value_ranges"].items():
            if col in df.columns:
                out_of_range = df[(df[col] < min_val) | (df[col] > max_val)]
                if len(out_of_range) > 0:
                    issues.append(f"{col}: {len(out_of_range)} values outside range [{min_val}, {max_val}]")
        
        return issues
    
    def set_validation_threshold(self, key: str, value: Any) -> None:
        """Update a validation threshold."""
        if key in self.validation_config:
            self.validation_config[key] = value
            self.send_message(f"Updated validation threshold: {key} = {value}", "DEBUG")
        else:
            self.send_message(f"Unknown validation key: {key}", "WARNING")
