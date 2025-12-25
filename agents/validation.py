from agents.base_agent import BaseAgent
class ValidationAgent(BaseAgent):
    def __init__(self, name="Validateur"):
        super().__init__(name)
        self.validation_threshold = {
            "min_rows": 10,
            "required_columns": [
                'Machine_ID', 'Operational_Hours', 
                'Power_Consumption_kW', 'Temperature_C'
            ],
            "max_null_percentage": 0.3
        }
    
    def validate_raw_data(self, data_package):
        """Validation des données brutes"""
        self.send_message("Validation des données brutes")
        df = data_package["data"]
        issues = []
        
        # Vérifier nombre de lignes
        if len(df) < self.validation_threshold["min_rows"]:
            issues.append(f"Données insuffisantes: {len(df)} lignes")
        
        # Vérifier colonnes requises
        missing_cols = set(self.validation_threshold["required_columns"]) - set(df.columns)
        if missing_cols:
            issues.append(f"Colonnes manquantes: {missing_cols}")
        
        # Vérifier taux de nulls
        null_percentage = df.isnull().sum().sum() / (len(df) * len(df.columns))
        if null_percentage > self.validation_threshold["max_null_percentage"]:
            issues.append(f"Trop de valeurs manquantes: {null_percentage:.2%}")
        
        if issues:
            self.send_message(f"❌ Validation échouée: {issues}", "ERROR")
            return {"valid": False, "issues": issues, "data": df}
        
        self.send_message("✅ Données brutes valides")
        return {"valid": True, "issues": [], "data": df}
    
    def validate_processed_data(self, df):
        """Validation après preprocessing"""
        self.send_message("Validation post-traitement")
        issues = []
        
        # Vérifier perte de données
        if len(df) < 5:
            issues.append("Trop de données supprimées")
        
        # Vérifier présence de NaN
        if df.isnull().any().any():
            issues.append("Des NaN persistent après nettoyage")
        
        if issues:
            self.send_message(f"⚠️ Validation partielle: {issues}", "WARNING")
            return {"valid": False, "issues": issues, "data": df}
        
        self.send_message("✅ Données traitées valides")
        return {"valid": True, "issues": [], "data": df}