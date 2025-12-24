from agents.base_agent import BaseAgent
import pandas as pd


class PreprocessingAgent(BaseAgent):
    def clean_data(self, df):
        self.send_message("Nettoyage et préparation des données")

        # Colonnes numériques
        numeric_cols = [
            'Operational_Hours',
            'Power_Consumption_kW',
            'Temperature_C',
            'Vibration_mms',
            'Sound_dB',
            'AI_Override_Events',
            'Installation_Year'
        ]

        # Conversion forcée en numérique
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Suppression lignes avec heures = 0 ou NaN
        df = df[df['Operational_Hours'] > 0]

        # Remplacer NaN restants par médiane
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

        return df
