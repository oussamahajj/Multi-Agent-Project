import numpy as np
import pandas as pd
from agents.base_agent import BaseAgent

class PreprocessingAgent(BaseAgent):
    def __init__(self, name="Prétraitement"):
        super().__init__(name)
        self.cleaning_report = {}
    
    def clean_data(self, validation_result):
        """Nettoyage avec rapport détaillé"""
        self.send_message("Nettoyage et préparation des données")
        df = validation_result["data"].copy()
        
        initial_rows = len(df)
        
        # Colonnes numériques
        numeric_cols = [
            'Operational_Hours', 'Power_Consumption_kW',
            'Temperature_C', 'Vibration_mms', 'Sound_dB',
            'AI_Override_Events', 'Installation_Year'
        ]
        
        # Conversion forcée
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Suppression lignes invalides
        df = df[df['Operational_Hours'] > 0]
        
        # Remplissage NaN
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        
        # Rapport de nettoyage
        self.cleaning_report = {
            "rows_removed": initial_rows - len(df),
            "rows_remaining": len(df),
            "removal_rate": (initial_rows - len(df)) / initial_rows
        }
        
        self.send_message(f"Nettoyage terminé: {self.cleaning_report['rows_removed']} lignes supprimées")
        
        return {
            "data": df,
            "cleaning_report": self.cleaning_report
        }