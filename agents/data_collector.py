"""
Data Collector Agent - Responsible for loading and initial data inspection
"""

import pandas as pd
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent


class DataCollectorAgent(BaseAgent):
    """
    Agent responsible for data collection and initial inspection.
    Handles CSV loading, schema detection, and basic data profiling.
    """
    
    def __init__(self, name: str = "DataCollector"):
        super().__init__(name, role="Data Collection Specialist")
        self.supported_formats = ['.csv', '.xlsx', '.json']
        
    def load_data(self, path: str) -> Dict[str, Any]:
        """
        Load data from a CSV file and perform initial inspection.
        
        Args:
            path: Path to the data file
            
        Returns:
            Dictionary containing data and metadata
        """
        self.set_state("loading")
        self.send_message(f"📂 Loading industrial data from: {path}")
        
        try:
            df = pd.read_csv(path)
            
            # Basic profiling
            profile = self._profile_data(df)
            
            self.set_state("loaded")
            self.send_message(f"✅ Successfully loaded {len(df)} rows × {len(df.columns)} columns", "SUCCESS")
            
            # Update shared context
            self.update_shared_context("raw_data_profile", profile)
            
            return {
                "data": df,
                "status": "loaded",
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": list(df.columns),
                "profile": profile,
                "file_path": path
            }
            
        except FileNotFoundError:
            self.send_message(f"❌ File not found: {path}", "ERROR")
            self.set_state("error")
            return {"data": None, "status": "error", "error": "File not found"}
            
        except Exception as e:
            self.send_message(f"❌ Error loading data: {str(e)}", "ERROR")
            self.set_state("error")
            return {"data": None, "status": "error", "error": str(e)}
    
    def _profile_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate a basic data profile."""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        profile = {
            "shape": df.shape,
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "missing_values": df.isnull().sum().to_dict(),
            "total_missing": int(df.isnull().sum().sum()),
            "missing_percentage": round(df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100, 2),
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            "duplicates": int(df.duplicated().sum()),
            "dtypes": df.dtypes.astype(str).to_dict()
        }
        
        # Sample statistics for numeric columns
        if numeric_cols:
            profile["numeric_stats"] = df[numeric_cols].describe().to_dict()
        
        # Unique counts for categorical columns
        if categorical_cols:
            profile["categorical_unique"] = {col: df[col].nunique() for col in categorical_cols}
        
        return profile
    
    def load_from_dataframe(self, df: pd.DataFrame, name: str = "uploaded_data") -> Dict[str, Any]:
        """
        Load data from an existing DataFrame.
        
        Args:
            df: Pandas DataFrame
            name: Name for the dataset
        """
        self.set_state("loading")
        self.send_message(f"📂 Loading data from DataFrame: {name}")
        
        profile = self._profile_data(df)
        
        self.set_state("loaded")
        self.send_message(f"✅ Successfully loaded {len(df)} rows × {len(df.columns)} columns", "SUCCESS")
        
        self.update_shared_context("raw_data_profile", profile)
        
        return {
            "data": df,
            "status": "loaded",
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "profile": profile,
            "source": name
        }
    
    def get_column_info(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """Get detailed information about a specific column."""
        if column not in df.columns:
            return {"error": f"Column '{column}' not found"}
        
        col_data = df[column]
        info = {
            "name": column,
            "dtype": str(col_data.dtype),
            "non_null_count": int(col_data.notna().sum()),
            "null_count": int(col_data.isna().sum()),
            "unique_count": int(col_data.nunique())
        }
        
        if pd.api.types.is_numeric_dtype(col_data):
            info.update({
                "min": float(col_data.min()) if not col_data.isna().all() else None,
                "max": float(col_data.max()) if not col_data.isna().all() else None,
                "mean": float(col_data.mean()) if not col_data.isna().all() else None,
                "std": float(col_data.std()) if not col_data.isna().all() else None,
                "median": float(col_data.median()) if not col_data.isna().all() else None
            })
        else:
            info["top_values"] = col_data.value_counts().head(5).to_dict()
        
        return info
