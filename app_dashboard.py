import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Import de l'orchestrateur et agents
from agents.orchestrator import SystemOrchestrator

# ===== CONFIGURATION PAGE =====
st.set_page_config(
    page_title="Système Multi-Agent Industriel",
    page_icon="🏭",
    layout="wide"
)

# ===== TITRE =====
st.title("🏭 Système Multi-Agent de Pilotage Industriel")
st.markdown("Architecture avec validation et boucles de feedback")

# ===== SIDEBAR =====
st.sidebar.header("⚙️ Configuration")
file_uploaded = st.sidebar.file_uploader("Charger un fichier CSV", type=["csv"])

# Option pour afficher les logs détaillés
show_logs = st.sidebar.checkbox("Afficher logs détaillés", value=True)
max_retries = st.sidebar.slider("Nombre max de retries", 1, 5, 3)

# ===== INITIALISATION =====
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = SystemOrchestrator()
    st.session_state.orchestrator.max_retries = max_retries

# ===== TRAITEMENT =====
if file_uploaded is not None:
    
    # Sauvegarder temporairement le fichier
    temp_path = f"temp_{datetime.now().timestamp()}.csv"
    with open(temp_path, "wb") as f:
        f.write(file_uploaded.getbuffer())
    
    # Bouton pour lancer l'analyse
    if st.sidebar.button("🚀 Lancer l'analyse", type="primary"):
        with st.spinner("Analyse en cours..."):
            # Exécution du pipeline
            result = st.session_state.orchestrator.run_pipeline(temp_path)
            st.session_state.result = result
    
    # Affichage des résultats si disponibles
    if 'result' in st.session_state:
        result = st.session_state.result
        
        # Vérifier si erreur
        if "error" in result:
            st.error(f"❌ {result['error']}")
            st.write("Problèmes détectés:", result['issues'])
        else:
            # ===== TABS POUR ORGANISATION =====
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Dashboard", 
                "🔍 Anomalies", 
                "🤖 Analyse LLM",
                "⚡ Décisions",
                "📄 Rapport"
            ])
            
            # ===== TAB 1: DASHBOARD KPI =====
            with tab1:
                st.header("Tableau de bord KPI")
                
                # Métriques principales
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Utilisation Moyenne",
                        f"{result['summary']['avg_utilization']:.1%}",
                        delta=None
                    )
                
                with col2:
                    st.metric(
                        "Efficacité Énergétique",
                        f"{result['summary']['avg_energy_efficiency']:.2f} kW/h",
                        delta=None
                    )
                
                with col3:
                    st.metric(
                        "Stabilité Moyenne",
                        f"{result['summary']['avg_stability']:.2f}",
                        delta=None
                    )
                
                with col4:
                    critical_pct = (result['summary']['critical_machine_count'] / 
                                   result['summary']['total_machines']) * 100
                    st.metric(
                        "Machines Critiques",
                        f"{result['summary']['critical_machine_count']}",
                        delta=f"-{critical_pct:.1f}%",
                        delta_color="inverse"
                    )
                
                # Graphique de distribution
                st.subheader("Distribution des KPI")
                df = result['df']
                
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=df['Utilization_Rate'],
                    name='Taux utilisation',
                    nbinsx=30
                ))
                fig.update_layout(
                    title="Distribution du taux d'utilisation",
                    xaxis_title="Taux d'utilisation",
                    yaxis_title="Nombre de machines"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Top machines critiques
                st.subheader("Top 10 Machines Critiques")
                critical_df = df[df['Utilization_Rate'] < 0.4].sort_values('Utilization_Rate')
                st.dataframe(
                    critical_df[['Machine_ID', 'Machine_Type', 'Utilization_Rate', 
                                'Energy_Efficiency', 'Stability_Index']].head(10),
                    use_container_width=True
                )
            
            # ===== TAB 2: ANOMALIES =====
            with tab2:
                st.header("Détection des Anomalies")
                
                anomalies = result['anomalies']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🌡️ Températures Élevées")
                    if anomalies['high_temperature']:
                        st.warning(f"{len(anomalies['high_temperature'])} machines détectées")
                        st.write(anomalies['high_temperature'][:10])
                    else:
                        st.success("Aucune anomalie")
                    
                    st.subheader("📳 Vibrations Élevées")
                    if anomalies['high_vibration']:
                        st.warning(f"{len(anomalies['high_vibration'])} machines détectées")
                        st.write(anomalies['high_vibration'][:10])
                    else:
                        st.success("Aucune anomalie")
                
                with col2:
                    st.subheader("⚡ Pics Énergétiques")
                    if anomalies['energy_spikes']:
                        st.warning(f"{len(anomalies['energy_spikes'])} machines détectées")
                        st.write(anomalies['energy_spikes'][:10])
                    else:
                        st.success("Aucune anomalie")
                    
                    st.subheader("🔧 Machines à l'Arrêt")
                    if anomalies['zero_utilization']:
                        st.error(f"{len(anomalies['zero_utilization'])} machines à l'arrêt")
                        st.write(anomalies['zero_utilization'][:10])
                    else:
                        st.success("Toutes les machines opérationnelles")
                
                # Graphique scatter anomalies
                st.subheader("Visualisation des Anomalies")
                fig = go.Figure()
                
                # Points normaux
                normal_df = df[~df['Machine_ID'].isin(
                    anomalies['high_temperature'] + 
                    anomalies['high_vibration']
                )]
                fig.add_trace(go.Scatter(
                    x=normal_df['Temperature_C'],
                    y=normal_df['Vibration_mms'],
                    mode='markers',
                    name='Normal',
                    marker=dict(color='green', size=8)
                ))
                
                # Anomalies température
                temp_df = df[df['Machine_ID'].isin(anomalies['high_temperature'])]
                fig.add_trace(go.Scatter(
                    x=temp_df['Temperature_C'],
                    y=temp_df['Vibration_mms'],
                    mode='markers',
                    name='Température élevée',
                    marker=dict(color='red', size=12, symbol='x')
                ))
                
                # Anomalies vibration
                vib_df = df[df['Machine_ID'].isin(anomalies['high_vibration'])]
                fig.add_trace(go.Scatter(
                    x=vib_df['Temperature_C'],
                    y=vib_df['Vibration_mms'],
                    mode='markers',
                    name='Vibration élevée',
                    marker=dict(color='orange', size=12, symbol='diamond')
                ))
                
                fig.update_layout(
                    title="Cartographie Température vs Vibration",
                    xaxis_title="Température (°C)",
                    yaxis_title="Vibration (mm/s)"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # ===== TAB 3: ANALYSE LLM =====
            with tab3:
                st.header("🤖 Analyse par Intelligence Artificielle")
                
                llm_result = result['decisions']  # Correction: utiliser le bon champ
                
                # Status de l'analyse
                if 'llm_result' in result and result['llm_result']['status'] == 'success':
                    st.success("✅ Analyse LLM réussie")
                else:
                    st.warning("⚠️ Analyse en mode dégradé")
                
                # Afficher l'analyse
                st.markdown("### Insights Générés")
                if 'llm_result' in result:
                    st.write(result['llm_result']['text'])
                else:
                    st.info("Analyse LLM non disponible dans ce résultat")
                
                # Statistiques de validation
                st.markdown("### Statistiques de Validation")
                validation_history = result['validation_history']
                
                success_count = sum(1 for v in validation_history if v['valid'])
                total_count = len(validation_history)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Validations Totales", total_count)
                col2.metric("Validations Réussies", success_count)
                col3.metric("Taux de Succès", f"{(success_count/total_count)*100:.1f}%")
                
                # Timeline des validations
                st.markdown("### Timeline des Validations")
                for i, val in enumerate(validation_history, 1):
                    status_icon = "✅" if val['valid'] else "❌"
                    st.text(f"{i}. {status_icon} [{val['agent']}] {val['message']}")
            
            # ===== TAB 4: DÉCISIONS =====
            with tab4:
                st.header("⚡ Décisions et Actions Recommandées")
                
                decisions = result['decisions']
                
                # Priorité
                priority = decisions['priority']
                if priority == "URGENT":
                    st.error(f"🚨 PRIORITÉ: {priority}")
                else:
                    st.success(f"✅ PRIORITÉ: {priority}")
                
                # Actions recommandées
                st.subheader("Actions Recommandées")
                for i, decision in enumerate(decisions['decisions'], 1):
                    st.markdown(f"**{i}.** {decision}")
                
                # Graphique de priorités
                st.subheader("Répartition des Problèmes")
                
                problem_counts = {
                    "Machines critiques": result['summary']['critical_machine_count'],
                    "Températures élevées": len(result['anomalies']['high_temperature']),
                    "Vibrations élevées": len(result['anomalies']['high_vibration']),
                    "Pics énergétiques": len(result['anomalies']['energy_spikes']),
                    "Machines à l'arrêt": len(result['anomalies']['zero_utilization'])
                }
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=list(problem_counts.keys()),
                        y=list(problem_counts.values()),
                        marker_color=['red', 'orange', 'orange', 'yellow', 'red']
                    )
                ])
                fig.update_layout(
                    title="Nombre de Problèmes par Catégorie",
                    xaxis_title="Catégorie",
                    yaxis_title="Nombre"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # ===== TAB 5: RAPPORT =====
            with tab5:
                st.header("📄 Rapport Complet")
                
                # Afficher le rapport
                st.text_area(
                    "Rapport généré",
                    result['report'],
                    height=600
                )
                
                # Bouton de téléchargement
                st.download_button(
                    label="📥 Télécharger le Rapport",
                    data=result['report'],
                    file_name=f"rapport_kpi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
                
                # Export CSV des données enrichies
                csv = result['df'].to_csv(index=False)
                st.download_button(
                    label="📥 Télécharger les Données (CSV)",
                    data=csv,
                    file_name=f"donnees_kpi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            # ===== LOGS DÉTAILLÉS (SIDEBAR) =====
            if show_logs:
                with st.sidebar.expander("📋 Logs Détaillés", expanded=False):
                    for val in result['validation_history']:
                        status = "✅" if val['valid'] else "❌"
                        st.text(f"{status} {val['agent']}")
                        st.caption(val['message'])

else:
    # ===== PAGE D'ACCUEIL =====
    st.info("👈 Chargez un fichier CSV pour commencer l'analyse")
    
    st.markdown("""
    ## Architecture du Système Multi-Agent
    
    Ce système utilise une architecture avec **validations multiples** et **boucles de feedback**:
    
    ### 🔄 Flux de Traitement
    
    1. **DataCollectorAgent** → Charge les données
    2. **ValidationAgent** → Valide les données brutes ✓
    3. **PreprocessingAgent** → Nettoie les données
    4. **ValidationAgent** → Revalide après nettoyage ✓
    5. **KPIAgent** → Calcule les indicateurs
    6. **AnalysisAgent** → Analyse les KPI
    7. **AnomalyDetectorAgent** → Détecte les anomalies
    8. **LLMInsightAgent** → Génère des insights
    9. **QualityControlAgent** → Contrôle qualité LLM ✓ (avec retry si échec)
    10. **DecisionAgent** → Prend les décisions
    11. **ReportAgent** → Génère le rapport
    12. **FinalValidationAgent** → Validation finale ✓ (avec retry si échec)
    
    ### ✨ Nouveautés
    
    - ✅ **3 points de validation** avec possibilité de rejet
    - 🔄 **Boucles de retry** pour LLM et rapport final
    - 📊 **Détection d'anomalies** statistiques
    - 🎯 **Système de décisions** multi-critères
    - 📝 **Traçabilité complète** de toutes les validations
    
    ### 📋 Format CSV Attendu
    
    Le fichier doit contenir les colonnes suivantes:
    - `Machine_ID`
    - `Machine_Type`
    - `Operational_Hours`
    - `Power_Consumption_kW`
    - `Temperature_C`
    - `Vibration_mms`
    - `Sound_dB`
    - `AI_Override_Events`
    - `Installation_Year`
    """)
    
    # Exemple de données
    with st.expander("📊 Voir un exemple de données"):
        example_data = {
            'Machine_ID': ['M001', 'M002', 'M003'],
            'Machine_Type': ['CNC', 'Laser', 'Robot'],
            'Operational_Hours': [8000, 3000, 12000],
            'Power_Consumption_kW': [150, 80, 200],
            'Temperature_C': [45, 38, 52],
            'Vibration_mms': [2.5, 1.8, 3.2],
            'Sound_dB': [75, 68, 82],
            'AI_Override_Events': [5, 2, 8],
            'Installation_Year': [2020, 2022, 2019]
        }
        st.dataframe(pd.DataFrame(example_data))