"""
🏭 Multi-Agent Industrial Monitoring System
Streamlit Application with Bold Industrial Design
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import json
import os
import sys
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="INDUS-AI | Multi-Agent System",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════
# CUSTOM CSS - BOLD INDUSTRIAL AESTHETIC
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* Import Google Fonts - Industrial/Technical Feel */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Outfit:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Root Variables - Industrial Color Palette */
    :root {
        --bg-primary: #0a0e14;
        --bg-secondary: #12171f;
        --bg-tertiary: #1a2130;
        --accent-orange: #ff6b35;
        --accent-cyan: #00d9ff;
        --accent-green: #00ff88;
        --accent-red: #ff3366;
        --accent-yellow: #ffcc00;
        --text-primary: #e8eaed;
        --text-secondary: #9aa0a6;
        --border-color: #2a3442;
        --glow-orange: 0 0 30px rgba(255, 107, 53, 0.3);
        --glow-cyan: 0 0 30px rgba(0, 217, 255, 0.3);
    }
    
    /* Main App Styling */
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 50%, var(--bg-tertiary) 100%);
    }
    
    /* Hide Streamlit branding - but keep sidebar toggle visible */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* header {visibility: hidden;} */ /* Commented out - can hide sidebar toggle */
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
    }
    
    h1 {
        font-size: 3.5rem !important;
        background: linear-gradient(135deg, var(--accent-orange) 0%, var(--accent-cyan) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-transform: uppercase;
        margin-bottom: 0.5rem !important;
    }
    
    /* Body text */
    p, span, div, label {
        font-family: 'JetBrains Mono', monospace !important;
        color: var(--text-primary);
    }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, var(--bg-secondary), var(--bg-tertiary));
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem !important;
        box-shadow: var(--glow-cyan);
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: var(--glow-orange);
        border-color: var(--accent-orange);
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-secondary) !important;
    }
    
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        color: var(--accent-cyan) !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%) !important;
        border-right: 2px solid var(--accent-orange) !important;
        min-width: 300px !important;
        width: 300px !important;
    }

    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem;
    }

    section[data-testid="stSidebar"] .stTextInput,
    section[data-testid="stSidebar"] .stFileUploader,
    section[data-testid="stSidebar"] .stCheckbox,
    section[data-testid="stSidebar"] .stSlider {
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    /* Buttons */
    .stButton > button {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        background: linear-gradient(135deg, var(--accent-orange) 0%, #ff8c5a 100%);
        color: var(--bg-primary) !important;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(255, 107, 53, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 30px rgba(255, 107, 53, 0.6);
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: var(--bg-tertiary);
        border: 2px dashed var(--accent-cyan);
        border-radius: 16px;
        padding: 1.5rem;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--accent-orange);
        box-shadow: var(--glow-orange);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--bg-secondary);
        padding: 0.5rem;
        border-radius: 16px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        background: transparent;
        border-radius: 12px;
        color: var(--text-secondary) !important;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--accent-orange), var(--accent-cyan)) !important;
        color: var(--bg-primary) !important;
    }
    
    /* Dataframes */
    [data-testid="stDataFrame"] {
        background: var(--bg-secondary);
        border-radius: 12px;
        border: 1px solid var(--border-color);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        background: var(--bg-tertiary);
        border-radius: 12px;
        border: 1px solid var(--border-color);
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--accent-orange), var(--accent-cyan));
        border-radius: 10px;
    }
    
    /* Text Area */
    .stTextArea > div > div > textarea {
        font-family: 'JetBrains Mono', monospace !important;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        color: var(--text-primary);
    }
    
    /* Select box */
    .stSelectbox > div > div {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
    }
    
    /* Checkbox */
    .stCheckbox label {
        font-family: 'JetBrains Mono', monospace !important;
        color: var(--text-secondary) !important;
    }
    
    /* Custom Classes */
    .hero-title {
        font-size: 4rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #ff6b35 0%, #00d9ff 50%, #00ff88 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        animation: glow 3s ease-in-out infinite;
    }
    
    @keyframes glow {
        0%, 100% { filter: drop-shadow(0 0 20px rgba(255, 107, 53, 0.5)); }
        50% { filter: drop-shadow(0 0 30px rgba(0, 217, 255, 0.5)); }
    }
    
    .subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.1rem;
        color: var(--text-secondary);
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 0.3em;
        margin-top: 0.5rem;
    }
    
    .status-card {
        background: linear-gradient(145deg, var(--bg-secondary), var(--bg-tertiary));
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
    }
    
    .agent-chip {
        display: inline-block;
        background: var(--bg-tertiary);
        border: 1px solid var(--accent-cyan);
        border-radius: 20px;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        font-size: 0.75rem;
        color: var(--accent-cyan);
    }
    
    .priority-urgent {
        background: linear-gradient(135deg, var(--accent-red), #ff1a1a);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 700;
    }
    
    .priority-normal {
        background: linear-gradient(135deg, var(--accent-green), #00cc6a);
        color: var(--bg-primary);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 700;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-primary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--accent-orange);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-cyan);
    }
    
    /* Animation for loading */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading-pulse {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* Glass effect panels */
    .glass-panel {
        background: rgba(26, 33, 48, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def create_gauge_chart(value, title, max_val=100, color_scheme="cyan"):
    """Create a stylized gauge chart."""
    colors = {
        "cyan": ["#0a1628", "#00d9ff"],
        "orange": ["#1a0f0a", "#ff6b35"],
        "green": ["#0a1a12", "#00ff88"],
        "red": ["#1a0a0a", "#ff3366"]
    }
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'color': '#e8eaed', 'family': 'Outfit'}},
        number={'font': {'size': 40, 'color': colors[color_scheme][1], 'family': 'JetBrains Mono'}},
        gauge={
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "#2a3442"},
            'bar': {'color': colors[color_scheme][1]},
            'bgcolor': colors[color_scheme][0],
            'borderwidth': 2,
            'bordercolor': "#2a3442",
            'steps': [
                {'range': [0, max_val * 0.3], 'color': '#1a0a0a'},
                {'range': [max_val * 0.3, max_val * 0.7], 'color': '#1a1a0a'},
                {'range': [max_val * 0.7, max_val], 'color': '#0a1a12'}
            ],
            'threshold': {
                'line': {'color': "#ff6b35", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#e8eaed', 'family': 'JetBrains Mono'},
        height=250,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def create_anomaly_radar(anomalies):
    """Create a radar chart for anomalies."""
    categories = ['Température', 'Vibration', 'Énergie', 'Arrêt', 'Maintenance', 'Erreurs']
    values = [
        len(anomalies.get('high_temperature', [])),
        len(anomalies.get('high_vibration', [])),
        len(anomalies.get('energy_spikes', [])),
        len(anomalies.get('zero_utilization', [])),
        len(anomalies.get('maintenance_overdue', [])),
        len(anomalies.get('high_error_rate', []))
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(255, 107, 53, 0.3)',
        line=dict(color='#ff6b35', width=3),
        marker=dict(size=10, color='#ff6b35')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                gridcolor='#2a3442',
                linecolor='#2a3442',
                tickfont=dict(color='#9aa0a6', family='JetBrains Mono')
            ),
            angularaxis=dict(
                gridcolor='#2a3442',
                linecolor='#2a3442',
                tickfont=dict(color='#e8eaed', family='Outfit', size=12)
            ),
            bgcolor='rgba(10, 14, 20, 0.8)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e8eaed'),
        showlegend=False,
        height=400,
        margin=dict(l=80, r=80, t=40, b=40)
    )
    
    return fig


def create_machine_scatter(df):
    """Create scatter plot of machines."""
    # Prepare size column - ensure non-negative values for marker sizes
    size_col = None
    if 'Power_Consumption_kW' in df.columns:
        # Create a copy to avoid modifying original data
        df = df.copy()
        # Ensure all size values are positive (use absolute value and add minimum size)
        df['_marker_size'] = df['Power_Consumption_kW'].abs().clip(lower=1)
        size_col = '_marker_size'

    fig = px.scatter(
        df,
        x='Utilization_Rate' if 'Utilization_Rate' in df.columns else 'Operational_Hours',
        y='Health_Score' if 'Health_Score' in df.columns else 'Temperature_C',
        color='Risk_Category' if 'Risk_Category' in df.columns else None,
        size=size_col,
        hover_data=['Machine_ID', 'Machine_Type'],
        color_discrete_map={
            'LOW': '#00ff88',
            'MEDIUM': '#ffcc00',
            'HIGH': '#ff6b35',
            'CRITICAL': '#ff3366'
        }
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(10, 14, 20, 0.8)',
        font=dict(color='#e8eaed', family='JetBrains Mono'),
        xaxis=dict(gridcolor='#2a3442', zerolinecolor='#2a3442'),
        yaxis=dict(gridcolor='#2a3442', zerolinecolor='#2a3442'),
        legend=dict(bgcolor='rgba(26, 33, 48, 0.8)'),
        height=500,
        margin=dict(l=60, r=40, t=40, b=60)
    )
    
    return fig


def create_agent_flow():
    """Create agent pipeline visualization."""
    agents = [
        ("📥", "Data Collector", "#00d9ff"),
        ("✓", "Validator", "#00ff88"),
        ("🔧", "Preprocessor", "#ffcc00"),
        ("📊", "KPI Agent", "#00d9ff"),
        ("📈", "Analyzer", "#ff6b35"),
        ("🔍", "Anomaly Detector", "#ff3366"),
        ("🧠", "Reasoning", "#9b59b6"),
        ("🎭", "Debate", "#e74c3c"),
        ("📋", "Planning", "#3498db"),
        ("🤖", "LLM Insight", "#00ff88"),
        ("⚖️", "Quality Control", "#ffcc00"),
        ("⚡", "Decision", "#ff6b35"),
        ("📄", "Reporter", "#00d9ff"),
        ("✅", "Final Validator", "#00ff88")
    ]
    
    html = '<div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; padding: 20px;">'
    for icon, name, color in agents:
        html += f'''
        <div style="
            background: linear-gradient(145deg, rgba(26, 33, 48, 0.9), rgba(18, 23, 31, 0.9));
            border: 2px solid {color};
            border-radius: 12px;
            padding: 12px 16px;
            text-align: center;
            min-width: 120px;
            box-shadow: 0 4px 15px {color}40;
            transition: all 0.3s ease;
        ">
            <div style="font-size: 1.5rem; margin-bottom: 4px;">{icon}</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: {color};">{name}</div>
        </div>
        '''
    html += '</div>'
    return html


# ═══════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

def main():
    # Header
    st.markdown('<h1 class="hero-title">🏭 INDUS-AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Multi-Agent Industrial Monitoring System</p>', unsafe_allow_html=True)
    st.markdown('---')
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        st.markdown("---")
        
        # API Key input
        api_key = st.text_input(
            "🔑 Gemini API Key",
            type="password",
            help="Enter your Google Gemini API key"
        )
        
        st.markdown("---")
        st.markdown("### 📁 Data Source")
        
        uploaded_file = st.file_uploader(
            "Upload CSV",
            type=['csv'],
            help="Upload your industrial machine data"
        )
        
        st.markdown("---")
        st.markdown("### 🧠 Agent Configuration")
        
        enable_reasoning = st.checkbox("Chain-of-Thought Reasoning", value=True, 
                                       help="Enable deep reasoning analysis")
        enable_debate = st.checkbox("Multi-Perspective Debate", value=True,
                                    help="Enable expert debate simulation")
        enable_planning = st.checkbox("Strategic Planning", value=True,
                                      help="Enable action plan generation")
        
        st.markdown("---")
        st.markdown("### 📊 Advanced Options")
        
        max_retries = st.slider("Max Retries", 1, 5, 3)
        show_debug = st.checkbox("Show Debug Logs", value=False)
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 20px; opacity: 0.7;">
            <small>
                Built with ❤️ using<br/>
                <strong>Gemini AI</strong> + <strong>Streamlit</strong>
            </small>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    if uploaded_file is None:
        # Welcome screen
        st.markdown("""
        <div class="glass-panel" style="text-align: center; padding: 3rem;">
            <h2 style="margin-bottom: 1rem;">👋 Welcome to INDUS-AI</h2>
            <p style="font-size: 1.1rem; color: #9aa0a6; max-width: 600px; margin: 0 auto;">
                Upload your industrial machine data to begin intelligent analysis 
                powered by a collaborative multi-agent system.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Agent Pipeline Visualization
        st.markdown("### 🔄 Agent Pipeline Architecture")
        st.markdown(create_agent_flow(), unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Features Grid
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="status-card">
                <h3 style="color: #00d9ff;">🧠 Reasoning</h3>
                <p style="color: #9aa0a6;">Chain-of-Thought analysis for deep understanding of industrial patterns</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="status-card">
                <h3 style="color: #ff6b35;">🎭 Multi-Expert Debate</h3>
                <p style="color: #9aa0a6;">Simulated debates between Operations, Maintenance, Finance, and Safety perspectives</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="status-card">
                <h3 style="color: #00ff88;">📋 Strategic Planning</h3>
                <p style="color: #9aa0a6;">Automated action plans with phases, metrics, and risk mitigation</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Sample data format
        with st.expander("📋 Expected Data Format"):
            st.markdown("""
            Your CSV should contain these columns:
            - `Machine_ID` - Unique identifier
            - `Machine_Type` - Type of machine
            - `Installation_Year` - Year installed
            - `Operational_Hours` - Total operating hours
            - `Temperature_C` - Current temperature
            - `Vibration_mms` - Vibration level
            - `Sound_dB` - Sound level
            - `Power_Consumption_kW` - Power usage
            - `Last_Maintenance_Days_Ago` - Days since maintenance
            - And more...
            """)
            
            sample_data = {
                'Machine_ID': ['MC_000001', 'MC_000002', 'MC_000003'],
                'Machine_Type': ['CNC', 'Laser_Cutter', 'Robot'],
                'Operational_Hours': [8000, 3000, 12000],
                'Temperature_C': [45, 38, 52],
                'Vibration_mms': [2.5, 1.8, 3.2]
            }
            st.dataframe(pd.DataFrame(sample_data), use_container_width=True)
    
    else:
        # Process uploaded file
        try:
            df_raw = pd.read_csv(uploaded_file)
            st.session_state['df_raw'] = df_raw
            
            # Data preview
            st.markdown("### 📊 Data Preview")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Rows", f"{len(df_raw):,}")
            col2.metric("Columns", len(df_raw.columns))
            col3.metric("Machine Types", df_raw['Machine_Type'].nunique() if 'Machine_Type' in df_raw.columns else "N/A")
            col4.metric("Missing Values", f"{df_raw.isnull().sum().sum():,}")
            
            with st.expander("🔍 View Raw Data", expanded=False):
                st.dataframe(df_raw.head(100), use_container_width=True)
            
            st.markdown("---")
            
            # Run Analysis Button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                run_analysis = st.button(
                    "🚀 LAUNCH MULTI-AGENT ANALYSIS",
                    use_container_width=True
                )
            
            if run_analysis:
                # Check API key
                if not api_key:
                    st.warning("⚠️ No API key provided. Running in fallback mode...")
                
                # Save file temporarily
                temp_path = os.path.join(tempfile.gettempdir(), f"data_{datetime.now().timestamp()}.csv")
                df_raw.to_csv(temp_path, index=False)
                
                # Progress tracking
                progress_container = st.container()
                with progress_container:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    def progress_callback(stage, progress, message):
                        progress_bar.progress(progress / 100)
                        status_text.markdown(f"**{stage}**: {message}")
                    
                    # Initialize and run orchestrator
                    try:
                        from orchestrator import SystemOrchestrator
                        
                        status_text.markdown("**Initializing**: Loading agents...")
                        orchestrator = SystemOrchestrator(api_key=api_key)
                        orchestrator.max_retries = max_retries
                        
                        # Run pipeline
                        result = orchestrator.run_pipeline(
                            temp_path,
                            enable_reasoning=enable_reasoning,
                            enable_debate=enable_debate,
                            enable_planning=enable_planning,
                            progress_callback=progress_callback
                        )
                        
                        st.session_state['result'] = result
                        
                        if result['status'] == 'success':
                            st.success("✅ Analysis completed successfully!")
                        else:
                            st.error(f"❌ Analysis failed: {result.get('errors', [])}")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        if show_debug:
                            st.exception(e)
            
            # Display results if available
            if 'result' in st.session_state:
                result = st.session_state['result']
                
                if result['status'] == 'success':
                    st.markdown("---")
                    
                    # Results Tabs
                    tabs = st.tabs([
                        "📊 Dashboard",
                        "🔍 Anomalies",
                        "🧠 AI Analysis",
                        "🎭 Debate",
                        "📋 Action Plan",
                        "⚡ Decisions",
                        "📄 Report"
                    ])
                    
                    # Tab 1: Dashboard
                    with tabs[0]:
                        st.markdown("## 📊 Key Performance Indicators")
                        
                        summary = result.get('summary', {})
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.plotly_chart(
                                create_gauge_chart(
                                    summary.get('avg_utilization', 0) * 100,
                                    "Utilization %",
                                    100, "cyan"
                                ),
                                use_container_width=True
                            )
                        
                        with col2:
                            st.plotly_chart(
                                create_gauge_chart(
                                    summary.get('avg_health_score', 0),
                                    "Health Score",
                                    100, "green"
                                ),
                                use_container_width=True
                            )
                        
                        with col3:
                            st.plotly_chart(
                                create_gauge_chart(
                                    summary.get('avg_stability', 0),
                                    "Stability Index",
                                    100, "orange"
                                ),
                                use_container_width=True
                            )
                        
                        with col4:
                            critical = summary.get('critical_machine_count', 0)
                            total = summary.get('total_machines', 1)
                            st.plotly_chart(
                                create_gauge_chart(
                                    (critical / total) * 100,
                                    "Critical %",
                                    100, "red"
                                ),
                                use_container_width=True
                            )
                        
                        # Machine scatter plot
                        if 'df' in result:
                            st.markdown("### 🎯 Machine Distribution")
                            st.plotly_chart(
                                create_machine_scatter(result['df']),
                                use_container_width=True
                            )
                    
                    # Tab 2: Anomalies
                    with tabs[1]:
                        st.markdown("## 🔍 Anomaly Detection")
                        
                        anomalies = result.get('anomalies', {})
                        
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.plotly_chart(
                                create_anomaly_radar(anomalies),
                                use_container_width=True
                            )
                        
                        with col2:
                            st.markdown("### Anomaly Summary")
                            for key, machines in anomalies.items():
                                if isinstance(machines, list) and machines:
                                    icon = {
                                        'high_temperature': '🌡️',
                                        'high_vibration': '📳',
                                        'energy_spikes': '⚡',
                                        'zero_utilization': '⏸️',
                                        'maintenance_overdue': '🔧',
                                        'high_error_rate': '❌'
                                    }.get(key, '⚠️')
                                    
                                    with st.expander(f"{icon} {key.replace('_', ' ').title()} ({len(machines)})"):
                                        st.write(machines[:20])
                    
                    # Tab 3: AI Analysis
                    with tabs[2]:
                        st.markdown("## 🧠 AI-Powered Analysis")
                        
                        # LLM Insight
                        if 'llm_insight' in result:
                            llm = result['llm_insight']
                            status = "✅ Success" if llm.get('status') == 'success' else "⚠️ Fallback"
                            st.markdown(f"**Status**: {status}")
                            st.markdown("---")
                            st.markdown(llm.get('text', 'No analysis available'))
                        
                        # Reasoning
                        if 'reasoning' in result:
                            st.markdown("---")
                            st.markdown("### 🔗 Chain-of-Thought Reasoning")
                            reasoning = result['reasoning']
                            st.markdown(f"**Confidence**: {reasoning.get('confidence', 'N/A')}")
                            
                            with st.expander("View Reasoning Steps"):
                                st.markdown(reasoning.get('reasoning_text', 'No reasoning available'))
                    
                    # Tab 4: Debate
                    with tabs[3]:
                        st.markdown("## 🎭 Multi-Expert Debate")
                        
                        if 'debate' in result:
                            debate = result['debate']
                            st.markdown(f"**Topic**: {debate.get('topic', 'N/A')}")
                            st.markdown(f"**Rounds**: {debate.get('rounds', 0)}")
                            
                            # Show debate log
                            st.markdown("### Debate Transcript")
                            for entry in debate.get('debate_log', []):
                                with st.expander(f"Round {entry['round']} - {entry['expert']}"):
                                    st.markdown(entry['argument'])
                            
                            # Show consensus
                            st.markdown("### 🤝 Consensus")
                            consensus = debate.get('consensus', {}).get('text', 'No consensus reached')
                            st.markdown(consensus)
                        else:
                            st.info("Debate was not enabled for this analysis")
                    
                    # Tab 5: Action Plan
                    with tabs[4]:
                        st.markdown("## 📋 Strategic Action Plan")
                        
                        if 'action_plan' in result:
                            plan = result['action_plan']
                            st.markdown(f"**Goal**: {plan.get('goal', 'N/A')}")
                            st.markdown(f"**Status**: {plan.get('status', 'N/A')}")
                            
                            for phase in plan.get('phases', []):
                                with st.expander(f"📌 {phase.get('name', 'Phase')}", expanded=True):
                                    st.markdown(phase.get('content', 'No content'))
                            
                            if plan.get('metrics'):
                                st.markdown("### 📊 Success Metrics")
                                for metric in plan['metrics']:
                                    st.markdown(f"- {metric}")
                            
                            if plan.get('risks'):
                                st.markdown("### ⚠️ Risks")
                                for risk in plan['risks']:
                                    st.markdown(f"- {risk}")
                        else:
                            st.info("Planning was not enabled for this analysis")
                    
                    # Tab 6: Decisions
                    with tabs[5]:
                        st.markdown("## ⚡ Strategic Decisions")
                        
                        decisions = result.get('decisions', {})
                        priority = decisions.get('priority', 'NORMAL')
                        
                        if priority == 'URGENT':
                            st.markdown('<div class="priority-urgent">🚨 PRIORITY: URGENT</div>', 
                                      unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="priority-normal">✅ PRIORITY: NORMAL</div>', 
                                      unsafe_allow_html=True)
                        
                        st.markdown("### Recommended Actions")
                        for i, decision in enumerate(decisions.get('decisions', []), 1):
                            priority_badge = {'P1': '🔴', 'P2': '🟠', 'P3': '🟢'}.get(
                                decision.get('priority', ''), '⚪'
                            )
                            st.markdown(f"""
                            **{i}. {priority_badge} {decision.get('action', 'N/A')}**
                            - Category: {decision.get('category', 'N/A')}
                            - Impact: {decision.get('impact', 'N/A')}
                            """)
                    
                    # Tab 7: Report
                    with tabs[6]:
                        st.markdown("## 📄 Complete Report")
                        
                        report = result.get('report', 'No report generated')
                        
                        st.text_area(
                            "Generated Report",
                            report,
                            height=600
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                "📥 Download Report (TXT)",
                                report,
                                f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                "text/plain"
                            )
                        
                        with col2:
                            if 'df' in result:
                                csv = result['df'].to_csv(index=False)
                                st.download_button(
                                    "📥 Download Data (CSV)",
                                    csv,
                                    f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    "text/csv"
                                )
                    
                    # Validation History
                    st.markdown("---")
                    with st.expander("🔄 Validation History & Traceability"):
                        validation_summary = orchestrator.get_validation_summary() if 'orchestrator' in dir() else {}
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Total Validations", validation_summary.get('total', 0))
                        col2.metric("Passed", validation_summary.get('passed', 0))
                        col3.metric("Success Rate", f"{validation_summary.get('rate', 0):.1f}%")
                        
                        for val in result.get('validation_history', []):
                            status = "✅" if val.get('valid') else "❌"
                            st.text(f"{status} [{val.get('agent', 'Unknown')}] {val.get('message', '')}")
                    
                    # Debug logs
                    if show_debug:
                        with st.expander("🐛 Debug Logs"):
                            for msg in result.get('agent_messages', []):
                                st.text(f"[{msg.get('level')}][{msg.get('agent')}] {msg.get('message')}")
        
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            if show_debug:
                st.exception(e)


if __name__ == "__main__":
    main()
