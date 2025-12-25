<<<<<<< HEAD
# 🏭 Architecture Multi-Agent avec Feedback Loops

## 📋 Vue d’ensemble
Cette architecture transforme un système séquentiel classique en un **système intelligent, résilient et auto-correctif**.  
Au lieu d’un pipeline linéaire, elle introduit des **boucles de feedback**, des **validations multi-niveaux** et une **traçabilité complète** afin de garantir la qualité du rapport final.

---

## 🎯 Principes Clés

### 1️⃣ Validation Multi-niveaux
- 3 points de validation critiques dans le pipeline  
- Chaque validation peut **rejeter** une étape et forcer une correction  
- Traçabilité complète de toutes les décisions

### 2️⃣ Boucles de Retry
- Maximum **3 tentatives** pour les opérations critiques  
- Évite la production de rapports de mauvaise qualité  
- Gestion intelligente des erreurs

### 3️⃣ Séparation des Responsabilités
- Chaque agent a **une seule mission**
- Communication via des structures de données standardisées
- Aucune dépendance circulaire

---

## 🔧 Les 12 Agents du Système

### 🟢 Groupe 1 : Collecte & Validation des Données

#### 1️⃣ DataCollectorAgent
- **Rôle** : Chargement des données CSV  
- **Input** : Chemin du fichier  
- **Output** :
```python


{
  "data": DataFrame,
  "status": str,
  "row_count": int,
  "columns": list
}
```python

2️⃣ ValidationAgent

Rôle : Validation qualité des données (2 étapes)

Validation 1 – Données brutes

Vérifie : nombre de lignes, colonnes requises, taux de valeurs nulles

Peut REJETER les données

Validation 2 – Post-preprocessing

Vérifie : perte de données, absence de NaN

Peut AVERTIR

Output


{
  "valid": bool,
  "issues": list,
  "data": DataFrame
}


3️⃣ PreprocessingAgent

Rôle : Nettoyage et préparation des données

Actions :

Conversion en types numériques

Suppression des lignes invalides (Operational_Hours <= 0)

Remplissage des NaN par la médiane

Output


{
  "data": DataFrame,
  "cleaning_report": dict
}


Groupe 2 : Calcul & Analyse
4️⃣ KPIAgent

Rôle : Calcul des indicateurs de performance

KPI calculés :

Machine_Age

Utilization_Rate

Energy_Efficiency

Stability_Index

AI_Override_Rate

➡️ Output : DataFrame enrichi

5️⃣ AnalysisAgent

Rôle : Analyse statistique globale

Calcule :

Moyennes globales

Machines sous-utilisées

Machines instables

Compteurs globaux

➡️ Output : dict

6️⃣ AnomalyDetectorAgent ⭐

Rôle : Détection d’anomalies statistiques

Détecte :

Températures > 95e percentile

Vibrations > 95e percentile

Pics énergétiques

Machines à l’arrêt


{
  "category": [Machine_IDs]
}


🟣 Groupe 3 : Intelligence & Décision
7️⃣ LLMInsightAgent

Rôle : Génération d’insights via Gemini 2.5 Flash

Produit :

3 problèmes

3 actions

Estimation d’impact

Fallback automatique si quota dépassé

8️⃣ QualityControlAgent ⭐

Rôle : Validation de la réponse LLM

Vérifie :

Longueur minimale

Mode fallback

Cohérence avec les KPI

➡️ Retry automatique (max 3)

9️⃣ DecisionAgent

Rôle : Décisions stratégiques finales

Basées sur :

KPI

Anomalies

Résultats LLM

Contrôle qualité


{
  "priority": "URGENT | NORMAL",
  "decisions": list,
  "action_needed": bool
}


Groupe 4 : Rapport & Validation Finale
🔟 ReportAgent

Rôle : Génération du rapport final

Contient :

KPI clés

Anomalies

Analyse LLM

Décisions

Traçabilité

Horodatage

➡️ Output : Texte structuré (ASCII)

1️⃣1️⃣ FinalValidationAgent ⭐

Rôle : Validation finale avant publication

Vérifie :

Sections obligatoires

Cohérence décisions / priorité

Format

➡️ Retry max 3

🔴 Groupe 5 : Orchestration
1️⃣2️⃣ SystemOrchestrator ⭐

Rôle : Chef d’orchestre du système

Gère :

Ordonnancement des agents

Boucles de retry

Historique des validations

Erreurs et timeouts

🔄 Boucles de Feedback

Validation post-preprocessing

Contrôle qualité LLM

Validation finale du rapport

➡️ Objectif : zéro rapport incohérent

📊 Traçabilité & Audit

Toutes les validations sont enregistrées :


validation_history = [
  {"agent": "Validator", "valid": True},
  {"agent": "QualityControl", "valid": False},
  {"agent": "QualityControl", "valid": True}
]

🚀 Installation

pip install streamlit pandas plotly google-generativeai


📁 Structure du Projet

project/
├── agents/
├── orchestrator.py
└── app.py

▶️ Lancer l’Application
streamlit run app.py

🎨 Interface Streamlit

📊 Dashboard KPI

🔍 Anomalies

🤖 Analyse LLM

⚡ Décisions

📄 Rapport final

💡 Améliorations Futures

Prédictions ML

Notifications automatiques

Export PDF

API REST

📚 Résumé

Cette architecture garantit :

✅ Qualité des données

✅ Décisions fiables

✅ Traçabilité complète

✅ Rapport final cohérent

Gain estimé :

📈 95 % de rapports valides dès la première génération

⏱️ Automatisation complète

🔒 Conformité et audit facilités
=======
# 🏭 Architecture Multi-Agent avec Feedback Loops

## 📋 Vue d’ensemble
Cette architecture transforme un système séquentiel classique en un **système intelligent, résilient et auto-correctif**.  
Au lieu d’un pipeline linéaire, elle introduit des **boucles de feedback**, des **validations multi-niveaux** et une **traçabilité complète** afin de garantir la qualité du rapport final.

---

## 🎯 Principes Clés

### 1️⃣ Validation Multi-niveaux
- 3 points de validation critiques dans le pipeline  
- Chaque validation peut **rejeter** une étape et forcer une correction  
- Traçabilité complète de toutes les décisions

### 2️⃣ Boucles de Retry
- Maximum **3 tentatives** pour les opérations critiques  
- Évite la production de rapports de mauvaise qualité  
- Gestion intelligente des erreurs

### 3️⃣ Séparation des Responsabilités
- Chaque agent a **une seule mission**
- Communication via des structures de données standardisées
- Aucune dépendance circulaire

---

## 🔧 Les 12 Agents du Système

### 🟢 Groupe 1 : Collecte & Validation des Données

#### 1️⃣ DataCollectorAgent
- **Rôle** : Chargement des données CSV  
- **Input** : Chemin du fichier  
- **Output** :
```python
{
  "data": DataFrame,
  "status": str,
  "row_count": int,
  "columns": list
}


2️⃣ ValidationAgent

Rôle : Validation qualité des données (2 étapes)

Validation 1 – Données brutes

Vérifie : nombre de lignes, colonnes requises, taux de valeurs nulles

Peut REJETER les données

Validation 2 – Post-preprocessing

Vérifie : perte de données, absence de NaN

Peut AVERTIR

Output


{
  "valid": bool,
  "issues": list,
  "data": DataFrame
}


3️⃣ PreprocessingAgent

Rôle : Nettoyage et préparation des données

Actions :

Conversion en types numériques

Suppression des lignes invalides (Operational_Hours <= 0)

Remplissage des NaN par la médiane

Output


{
  "data": DataFrame,
  "cleaning_report": dict
}


Groupe 2 : Calcul & Analyse
4️⃣ KPIAgent

Rôle : Calcul des indicateurs de performance

KPI calculés :

Machine_Age

Utilization_Rate

Energy_Efficiency

Stability_Index

AI_Override_Rate

➡️ Output : DataFrame enrichi

5️⃣ AnalysisAgent

Rôle : Analyse statistique globale

Calcule :

Moyennes globales

Machines sous-utilisées

Machines instables

Compteurs globaux

➡️ Output : dict

6️⃣ AnomalyDetectorAgent ⭐

Rôle : Détection d’anomalies statistiques

Détecte :

Températures > 95e percentile

Vibrations > 95e percentile

Pics énergétiques

Machines à l’arrêt


{
  "category": [Machine_IDs]
}


🟣 Groupe 3 : Intelligence & Décision
7️⃣ LLMInsightAgent

Rôle : Génération d’insights via Gemini 2.5 Flash

Produit :

3 problèmes

3 actions

Estimation d’impact

Fallback automatique si quota dépassé

8️⃣ QualityControlAgent ⭐

Rôle : Validation de la réponse LLM

Vérifie :

Longueur minimale

Mode fallback

Cohérence avec les KPI

➡️ Retry automatique (max 3)

9️⃣ DecisionAgent

Rôle : Décisions stratégiques finales

Basées sur :

KPI

Anomalies

Résultats LLM

Contrôle qualité


{
  "priority": "URGENT | NORMAL",
  "decisions": list,
  "action_needed": bool
}


Groupe 4 : Rapport & Validation Finale
🔟 ReportAgent

Rôle : Génération du rapport final

Contient :

KPI clés

Anomalies

Analyse LLM

Décisions

Traçabilité

Horodatage

➡️ Output : Texte structuré (ASCII)

1️⃣1️⃣ FinalValidationAgent ⭐

Rôle : Validation finale avant publication

Vérifie :

Sections obligatoires

Cohérence décisions / priorité

Format

➡️ Retry max 3

🔴 Groupe 5 : Orchestration
1️⃣2️⃣ SystemOrchestrator ⭐

Rôle : Chef d’orchestre du système

Gère :

Ordonnancement des agents

Boucles de retry

Historique des validations

Erreurs et timeouts

🔄 Boucles de Feedback

Validation post-preprocessing

Contrôle qualité LLM

Validation finale du rapport

➡️ Objectif : zéro rapport incohérent

📊 Traçabilité & Audit

Toutes les validations sont enregistrées :


validation_history = [
  {"agent": "Validator", "valid": True},
  {"agent": "QualityControl", "valid": False},
  {"agent": "QualityControl", "valid": True}
]

🚀 Installation

pip install streamlit pandas plotly google-generativeai


📁 Structure du Projet

project/
├── agents/
├── orchestrator.py
└── app.py

▶️ Lancer l’Application
streamlit run app.py

🎨 Interface Streamlit

📊 Dashboard KPI

🔍 Anomalies

🤖 Analyse LLM

⚡ Décisions

📄 Rapport final

💡 Améliorations Futures

Prédictions ML

Notifications automatiques

Export PDF

API REST

📚 Résumé

Cette architecture garantit :

✅ Qualité des données

✅ Décisions fiables

✅ Traçabilité complète

✅ Rapport final cohérent

Gain estimé :

📈 95 % de rapports valides dès la première génération

⏱️ Automatisation complète

🔒 Conformité et audit facilités
>>>>>>> d52d4eb (Mise à jour du projet : Ajouter la partie orchestration des entre aganets)
