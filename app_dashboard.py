import streamlit as st
import pandas as pd

# ===== Import des agents =====
from agents.data_collector import DataCollectorAgent
from agents.preprocessing import PreprocessingAgent
from agents.kpi_agent import KPIAgent
from agents.analysis import AnalysisAgent
from agents.llm_agent import LLMInsightAgent
from agents.report import ReportAgent

# ===== Titre de l'app =====
st.set_page_config(page_title="Rapport KPI Industriel", layout="wide")
st.title("📄 Rapport KPI Production Industrielle")
st.markdown("Suivi des performances et machines critiques")

# ===== INITIALISATION DES AGENTS =====
collector = DataCollectorAgent("Collecteur")
preprocessor = PreprocessingAgent("Prétraitement")
kpi_agent = KPIAgent("Agent KPI")
analyzer = AnalysisAgent("Analyseur")
llm_agent = LLMInsightAgent()
reporter = ReportAgent("Rapporteur")

# ===== CHARGEMENT DES DONNÉES =====
st.sidebar.header("Paramètres")
file_uploaded = st.sidebar.file_uploader("Charger un fichier CSV", type=["csv"])

if file_uploaded is not None:
    df = pd.read_csv(file_uploaded)

    # ===== PREPROCESSING =====
    df = preprocessor.clean_data(df)

    # ===== CALCUL KPI =====
    df = kpi_agent.compute_kpis(df)
    kpi_summary = analyzer.analyze(df)

    # ===== INTERPRÉTATION LLM =====
    llm_text = llm_agent.interpret(kpi_summary, df=df, top_n=10)

    # ===== AFFICHAGE DES KPI =====
    st.subheader("KPI Clés")
   

    # ===== MACHINES CRITIQUES =====
    st.subheader("Machines critiques (top 10)")
    st.write(df[df['Utilization_Rate'] < 0.4][['Machine_ID','Machine_Type','Utilization_Rate']].head(10))

    # ===== ANALYSE LLM =====
    st.subheader("Analyse LLM")
    st.write(llm_text)

    # ===== EXPORT DU RAPPORT =====
    report_text = reporter.generate_report(kpi_summary, llm_text)
    st.download_button("Télécharger le rapport", report_text, file_name="rapport_kpi.txt")
