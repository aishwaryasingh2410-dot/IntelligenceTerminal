import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from pathlib import Path

st.title("🧠 Market Activity Clustering")


# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

DATA_PATH = Path("frontend/data")


@st.cache_data
def load_data():

    files = list(DATA_PATH.glob("*.csv"))

    if not files:
        return pd.DataFrame()

    df = pd.concat([pd.read_csv(file) for file in files])

    df.columns = df.columns.str.strip().str.lower()

    return df


df = load_data()

if df.empty:
    st.warning("⚠ No CSV files found in backend/data folder")
    st.stop()


# --------------------------------------------------
# REQUIRED COLUMNS
# --------------------------------------------------

required_cols = ["volume_ce","volume_pe","oi_ce","oi_pe","strike"]

missing = [c for c in required_cols if c not in df.columns]

if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()


# --------------------------------------------------
# FEATURE ENGINEERING
# --------------------------------------------------

df["total_volume"] = pd.to_numeric(df["volume_ce"], errors="coerce") + \
                     pd.to_numeric(df["volume_pe"], errors="coerce")

df["total_oi"] = pd.to_numeric(df["oi_ce"], errors="coerce") + \
                 pd.to_numeric(df["oi_pe"], errors="coerce")

df = df.dropna(subset=["total_volume","total_oi","strike"])


# --------------------------------------------------
# SIDEBAR CONTROLS
# --------------------------------------------------

st.sidebar.header("⚙ Cluster Settings")

n_clusters = st.sidebar.slider(
    "Number of Clusters",
    2,
    6,
    3
)


# --------------------------------------------------
# DATA SUMMARY
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

col1.metric("Total Records", len(df))
col2.metric("Average Volume", int(df["total_volume"].mean()))
col3.metric("Average OI", int(df["total_oi"].mean()))


# --------------------------------------------------
# CLUSTERING
# --------------------------------------------------

features = df[["total_volume","total_oi"]]

if len(df) < n_clusters:
    st.error("Dataset too small for clustering")
    st.stop()

model = KMeans(
    n_clusters=n_clusters,
    random_state=42,
    n_init=10
)

df["cluster"] = model.fit_predict(features)


# label clusters
cluster_labels = {
    0:"Low Activity",
    1:"Medium Activity",
    2:"High Activity",
    3:"Institutional",
    4:"Extreme",
    5:"Outlier"
}

df["cluster_label"] = df["cluster"].map(cluster_labels)


# --------------------------------------------------
# VISUALIZATION
# --------------------------------------------------

st.subheader("📊 Market Activity Clusters")

fig = px.scatter(
    df,
    x="strike",
    y="total_volume",
    size="total_oi",
    color="cluster_label",
    title="Options Market Activity Clusters",
    hover_data=["total_oi"]
)

st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# CLUSTER SUMMARY
# --------------------------------------------------

st.subheader("📊 Cluster Summary")

summary = df.groupby("cluster_label")[["total_volume","total_oi"]].mean().round(0)

st.dataframe(summary, use_container_width=True)


# --------------------------------------------------
# INSIGHTS
# --------------------------------------------------

st.subheader("📈 AI Market Insight")

high_activity = df[df["cluster_label"]=="High Activity"]

if len(high_activity) > 10:
    st.warning("High trading activity detected in multiple strikes")

elif len(high_activity) > 0:
    st.info("Moderate smart-money participation detected")

else:
    st.success("Market activity appears normal")