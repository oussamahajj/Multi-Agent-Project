# 🏭 Architecture Multi-Agent avec Feedback Loops

## 📋 Vue d’ensemble
Cette architecture transforme un système séquentiel classique en un **système intelligent, résilient et auto-correctif**.  
Au lieu d’un pipeline linéaire, elle introduit des **boucles de feedback**, des **validations multi-niveaux** et une **traçabilité complète** afin de garantir la qualité du rapport final.

---

## 🎯 Principes Clés

1. **Validation Multi-niveaux** : 3 points de validation critiques, chaque validation peut rejeter ou corriger, avec traçabilité complète.  
2. **Boucles de Retry** : maximum 3 tentatives pour les opérations critiques.  
3. **Séparation des Responsabilités** : chaque agent a une seule mission, communication via structures standardisées, pas de dépendances circulaires.

---

## 🔧 Les 12 Agents du Système

### 🟢 Groupe 1 : Collecte & Validation des Données

**1️⃣ DataCollectorAgent**  
- Rôle : Chargement des données CSV  
- Input : chemin du fichier  
- Output : dictionnaire Python  
{
"data": DataFrame,
"status": str,
"row_count": int,
"columns": list
}

**2️⃣ ValidationAgent**  
- Rôle : Validation qualité des données (2 étapes)  
  - Validation 1 : Données brutes (nombre de lignes, colonnes requises, taux de valeurs nulles) → peut REJETER  
  - Validation 2 : Post-preprocessing (perte de données, absence de NaN) → peut AVERTIR  
- Output : dictionnaire Python  
{
"valid": bool,
"issues": list,
"data": DataFrame
}

**3️⃣ PreprocessingAgent**  
- Rôle : Nettoyage et préparation des données  
- Actions : conversion en types numériques, suppression des lignes invalides (Operational_Hours <= 0), remplissage des NaN par la médiane  
- Output : dictionnaire Python  
{
"data": DataFrame,
"cleaning_report": dict
}

---

### 🟢 Groupe 2 : Calcul & Analyse

**4️⃣ KPIAgent**  
- Rôle : Calcul des indicateurs de performance (`Machine_Age`, `Utilization_Rate`, `Energy_Efficiency`, `Stability_Index`, `AI_Override_Rate`)  
- Output : DataFrame enrichi

**5️⃣ AnalysisAgent**  
- Rôle : Analyse statistique globale (moyennes globales, machines sous-utilisées, machines instables, compteurs globaux)  
- Output : dictionnaire Python

**6️⃣ AnomalyDetectorAgent**  
- Rôle : Détection d’anomalies statistiques (températures > 95e percentile, vibrations > 95e percentile, pics énergétiques, machines à l’arrêt)  
- Output : dictionnaire Python  
{
"category": [Machine_IDs]
}

---

### 🟣 Groupe 3 : Intelligence & Décision

**7️⃣ LLMInsightAgent**  
- Rôle : Génération d’insights via Gemini 2.5 Flash  
- Produit : 3 problèmes, 3 actions, estimation d’impact, fallback automatique si quota dépassé

**8️⃣ QualityControlAgent**  
- Rôle : Validation de la réponse LLM (longueur minimale, mode fallback, cohérence avec KPI)  
- Retry automatique (max 3)

**9️⃣ DecisionAgent**  
- Rôle : Décisions stratégiques finales (basées sur KPI, anomalies, résultats LLM, contrôle qualité)  
- Output : dictionnaire Python  
{
"priority": "URGENT | NORMAL",
"decisions": list,
"action_needed": bool
}

---

### 🔵 Groupe 4 : Rapport & Validation Finale

**🔟 ReportAgent**  
- Rôle : Génération du rapport final (KPI, anomalies, analyse LLM, décisions, traçabilité, horodatage)  
- Output : texte structuré (ASCII)

**1️⃣1️⃣ FinalValidationAgent**  
- Rôle : Validation finale avant publication (sections obligatoires, cohérence décisions/priorité, format)  
- Retry max 3

---

### 🔴 Groupe 5 : Orchestration

**1️⃣2️⃣ SystemOrchestrator**  
- Rôle : Chef d’orchestre du système  
- Gère ordonnancement des agents, boucles de retry, historique des validations, erreurs et timeouts  
- Implémente les boucles de feedback : validation post-preprocessing, contrôle qualité LLM, validation finale du rapport  
- Objectif : zéro rapport incohérent

---

## 📊 Traçabilité & Audit
Toutes les validations sont enregistrées :  
validation_history = [  
  {"agent": "Validator", "valid": True},  
  {"agent": "QualityControl", "valid": False},  
  {"agent": "QualityControl", "valid": True}  
]

---

## 🚀 Installation
pip install streamlit pandas plotly google-generativeai

---

## 📁 Structure du Projet
project/  
├── agents/  
├── orchestrator.py  
└── app.py  

---

## ▶️ Lancer l’Application
streamlit run app.py

---

## 🎨 Interface Streamlit
- Dashboard KPI  
- Anomalies  
- Analyse LLM  
- Décisions  
- Rapport final

---

## 💡 Améliorations Futures
- Prédictions ML  
- Notifications automatiques  
- Export PDF  
- API REST

---

## 📚 Résumé
✅ Qualité des données  
✅ Décisions fiables  
✅ Traçabilité complète  
✅ Rapport final cohérent  

Gain estimé :  
📈 95 % de rapports valides dès la première génération  
⏱️ Automatisation complète  
🔒 Conformité et audit facilités
