import streamlit as st
import pandas as pd
import glob
import plotly.express as px
from sklearn.cluster import KMeans
st.set_page_config(
    page_title="Options Intelligence Terminal",
    layout="wide",
    page_icon="📊"
)

st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
}

[data-testid="stSidebar"] {
    background-color: #161B22;
}

h1,h2,h3,h4 {
    color: white;
}

.block-container {
    padding-top: 2rem;
}

.metric-container {
    background-color: #161B22;
    border-radius: 10px;
    padding: 15px;
}
</style>
""", unsafe_allow_html=True)
st.set_page_config(layout="wide")

st.title("🧠 Market Activity Clustering")

# -------------------------
# Load Data
# -------------------------

files = glob.glob("data/*.csv")

if not files:
    st.warning("No CSV files found in data folder")
    st.stop()

df = pd.concat([pd.read_csv(file) for file in files])

# Clean column names
df.columns = df.columns.str.strip()
df.columns = df.columns.str.lower()

# -------------------------
# Feature Engineering
# -------------------------

required_cols = ["volume_ce","volume_pe","oi_ce","oi_pe","strike"]

for col in required_cols:
    if col not in df.columns:
        st.error(f"Missing column: {col}")
        st.stop()

df["total_volume"] = df["volume_ce"] + df["volume_pe"]
df["total_oi"] = df["oi_ce"] + df["oi_pe"]

# -------------------------
# Clustering
# -------------------------

features = df[["total_volume","total_oi"]]

kmeans = KMeans(n_clusters=3, random_state=42)

df["cluster"] = kmeans.fit_predict(features)

# -------------------------
# Visualization
# -------------------------

fig = px.scatter(
    df,
    x="strike",
    y="total_volume",
    color="cluster",
    size="total_oi",
    template="plotly_dark",
    title="Market Activity Clusters",
    color_continuous_scale="Turbo"
)

fig.update_layout(
    plot_bgcolor="#0E1117",
    paper_bgcolor="#0E1117",
    font=dict(color="white")
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Explanation
# -------------------------

st.info("""
Clusters represent different types of market activity:

Cluster 0 → Low activity  
Cluster 1 → Medium activity  
Cluster 2 → High activity / Institutional activity
""")