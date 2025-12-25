# 🏭 Multi-Agent Industrial Monitoring System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.29+-red.svg)](https://streamlit.io/)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-green.svg)](https://deepmind.google/technologies/gemini/)

> An intelligent multi-agent system for industrial machine monitoring and predictive maintenance, powered by collaborative AI agents and Google Gemini LLM.

![System Architecture](https://via.placeholder.com/800x400/0a0e14/00d9ff?text=Multi-Agent+Industrial+Monitoring+System)

## 🌟 Features

### 🤖 15 Specialized AI Agents
- **Data Collector**: Loads and profiles industrial machine data
- **Validator**: Ensures data quality with configurable thresholds
- **Preprocessor**: Cleans and transforms data using IQR outlier detection
- **KPI Agent**: Computes 8 key performance indicators
- **Analysis Agent**: Performs statistical analysis and correlations
- **Anomaly Detector**: Detects 11 types of anomalies
- **Reasoning Agent**: Chain-of-Thought analysis with Gemini LLM
- **Debate Agent**: Multi-perspective debates between expert personas
- **Planning Agent**: Strategic action planning with phases
- **LLM Insight Agent**: Expert interpretations in French
- **Quality Control**: Validates AI outputs for consistency
- **Decision Agent**: Strategic decision making with priorities
- **Report Agent**: Comprehensive French-language reports
- **Final Validator**: Quality assurance before publication

### 🧠 Advanced AI Capabilities
- **Chain-of-Thought Reasoning**: 8-step reasoning process for root cause analysis
- **Multi-Expert Debate**: Simulated debates between Operations, Maintenance, Finance, and Safety perspectives
- **Strategic Planning**: 3-phase action plans (Immediate, Short-term, Medium-term)
- **Fallback Mode**: Fully functional without API key

### 📊 Rich Visualizations
- Interactive Plotly dashboards
- Gauge charts for KPIs
- Radar charts for anomalies
- Scatter plots for machine distribution
- Industrial-themed dark UI

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/multi-agent-industrial.git
cd multi-agent-industrial

# Install dependencies
pip install -r requirements.txt

# Optional: Set Gemini API key
export GEMINI_API_KEY="your-api-key-here"
```

### Generate Sample Data

```bash
python main.py sample
```

### Run Analysis (CLI)

```bash
# With API key (full features)
python main.py analyze --data sample_industrial_data.csv --api-key YOUR_KEY

# Without API key (fallback mode)
python main.py analyze --data sample_industrial_data.csv

# Fast mode (disable reasoning features)
python main.py analyze --data data.csv --no-reasoning --no-debate --no-planning
```

### Launch Web Interface

```bash
python main.py web
# Or directly:
streamlit run app.py
```

## 📁 Project Structure

```
multi_agent_system/
├── agents/
│   ├── __init__.py           # Package exports
│   ├── base_agent.py         # Base agent class
│   ├── data_collector.py     # Data loading agent
│   ├── validation.py         # Validation agent
│   ├── preprocessing.py      # Data cleaning agent
│   ├── kpi_agent.py          # KPI calculation agent
│   ├── analysis.py           # Statistical analysis agent
│   ├── anomaly_detector.py   # Anomaly detection agent
│   ├── reasoning_agent.py    # Chain-of-Thought reasoning
│   ├── debate_agent.py       # Multi-perspective debate
│   ├── planning_agent.py     # Strategic planning
│   ├── llm_agent.py          # LLM insights agent
│   ├── quality_control.py    # Quality validation agent
│   ├── decision.py           # Decision making agent
│   ├── report.py             # Report generation agent
│   └── final_validation.py   # Final quality check
├── orchestrator.py           # Pipeline coordinator
├── app.py                    # Streamlit web interface
├── main.py                   # CLI entry point
├── config.py                 # Configuration management
├── sample_data.py            # Sample data generator
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 📊 Expected Data Format

Your CSV should include these columns:

| Column | Type | Description |
|--------|------|-------------|
| `Machine_ID` | string | Unique machine identifier |
| `Machine_Type` | string | CNC, Lathe, Robot, etc. |
| `Installation_Year` | int | Year of installation |
| `Operational_Hours` | float | Total operating hours |
| `Temperature_C` | float | Current temperature (°C) |
| `Vibration_mms` | float | Vibration level (mm/s) |
| `Sound_dB` | float | Sound level (dB) |
| `Oil_Level_pct` | float | Oil level (%) |
| `Coolant_Level_pct` | float | Coolant level (%) |
| `Power_Consumption_kW` | float | Power usage (kW) |
| `Last_Maintenance_Days_Ago` | int | Days since maintenance |
| `Maintenance_History_Count` | int | Total maintenances |
| `Failure_History_Count` | int | Total failures |
| `AI_Supervision` | int | 0 or 1 |
| `Error_Codes_Last_30_Days` | int | Recent error count |
| `Remaining_Useful_Life_days` | int | Predicted RUL |
| `Failure_Within_7_Days` | int | 0 or 1 |

## 🔧 Configuration

Edit `config.py` to customize:

```python
# LLM Settings
llm_config = {
    "model_name": "gemini-2.5-flash",
    "max_tokens": 2048,
    "temperature": 0.7
}

# Anomaly Thresholds
anomaly_config = {
    "percentile_high": 0.95,
    "z_score_threshold": 3.0,
    "maintenance_overdue_days": 90
}

# Decision Thresholds
decision_config = {
    "critical_machine_ratio": 0.30,
    "high_temp_count": 5,
    "low_health_threshold": 50.0
}
```

## 📈 KPIs Computed

1. **Machine_Age**: Years since installation
2. **Utilization_Rate**: Operating efficiency (0-1)
3. **Energy_Efficiency**: Power per operational hour
4. **Stability_Index**: Operational consistency (0-100)
5. **AI_Override_Rate**: Human intervention frequency
6. **Maintenance_Urgency**: Maintenance priority score
7. **Health_Score**: Overall machine health (0-100)
8. **Risk_Category**: LOW / MEDIUM / HIGH / CRITICAL

## 🔍 Anomaly Types Detected

- 🌡️ High Temperature
- 📳 High Vibration
- ⚡ Energy Spikes
- ⏸️ Zero Utilization
- 📉 Very Low Utilization
- 🔊 High Sound Level
- 🔧 Maintenance Overdue
- 🚨 Maintenance Critical
- ❌ High Error Rate
- 🤖 High AI Override
- ⚠️ Multi-Factor Critical

## 🎭 Expert Personas (Debate Agent)

| Expert | Focus | Perspective |
|--------|-------|-------------|
| Operations Manager | Production | Efficiency & output |
| Maintenance Engineer | Equipment | Health & longevity |
| Financial Analyst | Cost | Budget & ROI |
| Safety Officer | Safety | Worker protection |

## 📝 Report Sections

1. **Header**: Priority, timestamp, system info
2. **Executive Summary**: Global status, key metrics
3. **KPIs**: Performance indicators with analysis
4. **Anomalies**: Detected issues by category
5. **AI Analysis**: LLM insights and reasoning
6. **Debate**: Multi-perspective conclusions
7. **Decisions**: Strategic actions with priorities
8. **Action Plan**: Phased implementation plan
9. **Traceability**: Validation history

## 🌐 API Reference

### SystemOrchestrator

```python
from orchestrator import SystemOrchestrator

# Initialize
orchestrator = SystemOrchestrator(api_key="YOUR_API_KEY")

# Run pipeline
result = orchestrator.run_pipeline(
    data_source="data.csv",
    enable_reasoning=True,
    enable_debate=True,
    enable_planning=True
)

# Check status
print(result['status'])  # 'success' or 'error'
print(result['anomaly_count'])
print(result['report'])
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Google Gemini AI](https://deepmind.google/technologies/gemini/) for LLM capabilities
- [Streamlit](https://streamlit.io/) for the web framework
- [Plotly](https://plotly.com/) for visualizations

---

<div align="center">
  <strong>Built with ❤️ for Industrial Excellence</strong>
  <br>
  <sub>Multi-Agent System v2.0</sub>
</div>
