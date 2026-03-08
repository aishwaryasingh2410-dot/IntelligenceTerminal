import streamlit as st
from pathlib import Path

# -------------------------------------------------------
# PAGE CONFIG (MUST BE FIRST STREAMLIT COMMAND)
# -------------------------------------------------------

st.set_page_config(
    page_title="NIFTY Options Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------
# LOAD CSS
# -------------------------------------------------------

def load_css():
    css_path = Path("styles/style.css")

    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# -------------------------------------------------------
# HEADER CARD
# -------------------------------------------------------

st.markdown(
"""
<div class="header-card">
<h3>📊 Market Intelligence Platform</h3>
<p>
Analyze liquidity, volatility, sentiment and AI-driven anomalies
in the <b>NIFTY Options Market</b>.
</p>
</div>
""",
unsafe_allow_html=True
)

# -------------------------------------------------------
# DATA LOADER
# -------------------------------------------------------

DATA_PATH = Path("data")

@st.cache_data
def get_available_expiries():

    if not DATA_PATH.exists():
        return []

    files = list(DATA_PATH.glob("*.csv"))
    expiries = [f.stem for f in files]
    expiries.sort()

    return expiries


expiries = get_available_expiries()

# -------------------------------------------------------
# SIDEBAR CONTROLS
# -------------------------------------------------------

st.sidebar.title("⚙ Dashboard Controls")

if expiries:

    selected_expiry = st.sidebar.selectbox(
        "📅 Select Expiry Dataset",
        expiries
    )

    st.session_state["selected_expiry"] = selected_expiry

else:

    st.sidebar.warning("No datasets found in /data folder")
    selected_expiry = None

st.sidebar.markdown("---")

st.sidebar.markdown("### 📊 Dashboard Modules")

st.sidebar.markdown("""
• Market Overview  
• Price Analysis  
• Open Interest Analysis  
• Volume Heatmap  
• PCR Sentiment  
• AI Anomaly Detection  
• Volatility Smile  
• Volatility Surface  
• Market Activity Clusters
""")

st.sidebar.markdown("---")

st.sidebar.markdown("### 🧰 Built With")

st.sidebar.markdown("""
Streamlit  
Pandas  
Plotly  
Scikit-learn  
NumPy
""")

# -------------------------------------------------------
# MAIN TITLE
# -------------------------------------------------------

st.title("📊 NIFTY Options Market Intelligence Dashboard")

# -------------------------------------------------------
# METRICS ROW
# -------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📂 Datasets Loaded", len(expiries))

with col2:
    st.metric("📅 Selected Dataset", selected_expiry if selected_expiry else "None")

with col3:
    st.metric("🟢 Dashboard Status", "Online")

# -------------------------------------------------------
# DESCRIPTION
# -------------------------------------------------------

st.markdown(
"""
<div class="section">
<h4>📌 Platform Overview</h4>

A <b>data-driven analytics platform</b> for exploring the
<b>NIFTY Options Market Structure</b>.

The dashboard helps analyze:

• Market sentiment  
• Liquidity clusters  
• Volatility patterns  
• AI-detected anomalies  

</div>
""",
unsafe_allow_html=True
)

# -------------------------------------------------------
# FEATURE OVERVIEW
# -------------------------------------------------------

st.markdown("## 🚀 Dashboard Capabilities")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
    """
    <div class="section">
    <h4>📈 Market Analytics</h4>

    • Price analysis  
    • Open interest tracking  
    • Volume heatmaps  

    </div>
    """,
    unsafe_allow_html=True
    )

with col2:
    st.markdown(
    """
    <div class="section">
    <h4>🧠 AI Insights</h4>

    • Market anomaly detection  
    • Activity clustering  
    • Smart signals  

    </div>
    """,
    unsafe_allow_html=True
    )

with col3:
    st.markdown(
    """
    <div class="section">
    <h4>📉 Volatility Intelligence</h4>

    • Volatility smile  
    • Volatility surface  
    • Sentiment indicators  

    </div>
    """,
    unsafe_allow_html=True
    )

st.divider()

# -------------------------------------------------------
# DATASET STATUS
# -------------------------------------------------------

st.subheader("📂 Dataset Status")

if expiries:

    st.success(f"✅ {len(expiries)} dataset files detected")

    st.dataframe(
        {"Dataset": expiries},
        use_container_width=True
    )

    if selected_expiry:
        st.info(f"Current Dataset: **{selected_expiry}.csv**")

else:

    st.error("❌ No datasets detected in the data folder.")

# -------------------------------------------------------
# FOOTER
# -------------------------------------------------------

st.divider()

st.caption(
    "Built with open-source tools for scalable financial analytics."
)