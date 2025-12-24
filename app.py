# ===== IMPORTS DES AGENTS =====
from agents.data_collector import DataCollectorAgent
from agents.preprocessing import PreprocessingAgent
from agents.kpi_agent import KPIAgent
from agents.analysis import AnalysisAgent
from agents.llm_agent import LLMInsightAgent
from agents.report import ReportAgent


def main():
    # ===== INITIALISATION DES AGENTS =====
    collector = DataCollectorAgent("Collecteur")
    preprocessor = PreprocessingAgent("Prétraitement")
    kpi_agent = KPIAgent("Agent KPI")
    analyzer = AnalysisAgent("Analyseur")
    llm_agent = LLMInsightAgent()
    reporter = ReportAgent("Rapporteur")

    # ===== PIPELINE MULTI-AGENTS =====
    df = collector.load_data("data.csv")
    df = preprocessor.clean_data(df)

    df = kpi_agent.compute_kpis(df)
    print(kpi_agent.compute_kpis(df))

    kpi_summary = analyzer.analyze(df)

    # Passer df pour inclure machines critiques (top 10) dans le prompt
    llm_insight = llm_agent.interpret(kpi_summary, df=df, top_n=10)

    final_report = reporter.generate_report(kpi_summary, llm_insight)

    print(final_report)


if __name__ == "__main__":
    main()
