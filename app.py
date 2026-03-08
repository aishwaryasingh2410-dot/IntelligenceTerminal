import streamlit as st
import pandas as pd
import glob
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import time

px.defaults.template = "plotly_dark" 
from sklearn.ensemble import IsolationForest
from backend.data_loader import get_available_expiries, load_expiry_data
# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------

st.set_page_config(
    page_title="Options Intelligence Terminal",
    layout="wide",
    page_icon="📊"
)

# ----------------------------------------------------
# STYLING
# ----------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #0E1117;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#111827,#1f2937);
}

h1,h2,h3,h4 {
    color: white;
}

.block-container {
    padding-top: 2rem;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# HEADER
# ----------------------------------------------------

st.title("📊 NIFTY Options Intelligence Terminal")
st.caption("AI-powered options analytics with database performance monitoring")

# ----------------------------------------------------
# LOAD DATA
# ----------------------------------------------------

@st.cache_data
def load_data():

    files = glob.glob("backend/data/*.csv")

    if len(files) == 0:
        return pd.DataFrame()

    df = pd.concat([pd.read_csv(file) for file in files], ignore_index=True)

    df.columns = df.columns.str.strip().str.lower()

    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")

    # Feature engineering
    if {"volume_ce","volume_pe"}.issubset(df.columns):
        df["total_volume"] = df["volume_ce"] + df["volume_pe"]

    if {"oi_ce","oi_pe"}.issubset(df.columns):
        df["total_oi"] = df["oi_ce"] + df["oi_pe"]

    if {"volume_ce","volume_pe"}.issubset(df.columns):
        df["pcr"] = df["volume_pe"] / (df["volume_ce"] + 1)

    return df


df = load_data()

if df.empty:
    st.error("❌ No CSV files found in backend/data")
    st.stop()

# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------

with st.sidebar:

    st.title("📊 Options Terminal")

    st.markdown("### 🔎 Market Filters")

    expiries = get_available_expiries()

    if not expiries:
        st.error("❌ No expiry datasets found in backend/data")
        st.stop()

    expiry = st.selectbox(
        "Select Expiry",
        expiries
    )

# ----------------------------------------------------
# LOAD DATA FOR SELECTED EXPIRY
# ----------------------------------------------------

df = load_expiry_data(expiry)

if df.empty:
    st.warning("No data found for selected expiry")
    st.stop()

# ----------------------------------------------------
# STRIKE FILTER
# ----------------------------------------------------

min_strike = int(df["strike"].min())
max_strike = int(df["strike"].max())

strike_range = st.slider(
    "Strike Range",
    min_strike,
    max_strike,
    (min_strike, max_strike)
)

df_filtered = df[
    (df["strike"] >= strike_range[0]) &
    (df["strike"] <= strike_range[1])
].copy()

with st.sidebar:

    st.divider()

    page = st.radio(
        "📊 Dashboard",
        [
            "Market Overview",
            "Open Interest",
            "Volume Heatmap",
            "PCR Sentiment",
            "AI Anomaly",
            "Volatility Smile",
            "Volatility Surface",
            "Database Performance"
        ]
    )

# ----------------------------------------------------
# MARKET OVERVIEW
# ----------------------------------------------------

if page == "Market Overview":

    st.subheader("📈 Market Overview")

    spot = round(df_filtered["spot_close"].iloc[-1],2) if "spot_close" in df_filtered.columns else "N/A"
    total_volume = int(df_filtered["total_volume"].sum()) if "total_volume" in df_filtered.columns else 0
    total_oi = int(df_filtered["total_oi"].sum()) if "total_oi" in df_filtered.columns else 0
    avg_pcr = round(df_filtered["pcr"].mean(),2) if "pcr" in df_filtered.columns else 0

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("NIFTY Spot",spot)
    col2.metric("Total Volume",f"{total_volume:,}")
    col3.metric("Total OI",f"{total_oi:,}")
    col4.metric("Average PCR",avg_pcr)

    st.divider()

    st.subheader("📊 PCR Sentiment")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_pcr,
        title={'text':"Put Call Ratio"},
        gauge={
            'axis':{'range':[0,2]},
            'steps':[
                {'range':[0,0.8],'color':"#ff4b4b"},
                {'range':[0.8,1.2],'color':"#888"},
                {'range':[1.2,2],'color':"#2ecc71"}
            ]
        }
    ))

    st.plotly_chart(fig,use_container_width=True)

# ----------------------------------------------------
# OPEN INTEREST
# ----------------------------------------------------

elif page == "Open Interest":

    st.subheader("📌 Open Interest Distribution")

    oi_df = df_filtered.groupby("strike")[["oi_ce","oi_pe"]].sum().reset_index()

    fig = px.bar(
        oi_df,
        x="strike",
        y=["oi_ce","oi_pe"],
        barmode="group",
        template="plotly_dark"
    )

    st.plotly_chart(fig,use_container_width=True)

# ----------------------------------------------------
# VOLUME HEATMAP
# ----------------------------------------------------

elif page == "Volume Heatmap":

    st.subheader("📊 Volume Distribution")

    vol_df = df_filtered.groupby("strike")[["volume_ce","volume_pe"]].sum().reset_index()

    fig = px.bar(
        vol_df,
        x="strike",
        y=["volume_ce","volume_pe"],
        barmode="group",
        template="plotly_dark"
    )

    st.plotly_chart(fig,use_container_width=True)

# ----------------------------------------------------
# PCR TREND
# ----------------------------------------------------

elif page == "PCR Sentiment":

    st.subheader("📊 PCR Trend")

    if "datetime" not in df_filtered.columns:
        st.warning("Datetime column missing")
    else:
        pcr = df_filtered.groupby("datetime")["pcr"].mean().reset_index()

        fig = px.line(
            pcr,
            x="datetime",
            y="pcr",
            template="plotly_dark"
        )

        st.plotly_chart(fig,use_container_width=True)

# ----------------------------------------------------
# AI ANOMALY
# ----------------------------------------------------

elif page == "AI Anomaly":

    st.subheader("🤖 AI Unusual Options Activity")

    features = df_filtered[["oi_ce","oi_pe","volume_ce","volume_pe"]].fillna(0)

    model = IsolationForest(contamination=0.02,random_state=42)

    df_filtered = df_filtered.copy()
    df_filtered["anomaly"] = model.fit_predict(features)

    anomalies = df_filtered[df_filtered["anomaly"]==-1]

    fig = px.scatter(
        df_filtered,
        x="strike",
        y="total_volume",
        color="anomaly",
        size="total_oi",
        template="plotly_dark"
    )

    st.plotly_chart(fig,use_container_width=True)

    st.subheader("Detected Anomalies")
    st.dataframe(anomalies.head(10),use_container_width=True)

# ----------------------------------------------------
# VOLATILITY SMILE
# ----------------------------------------------------

elif page == "Volatility Smile":

    st.subheader("📊 Volatility Smile")

    if "ce" not in df_filtered.columns:
        st.warning("IV column 'ce' not found")
    else:
        iv = df_filtered.groupby("strike")["ce"].mean().reset_index()

        fig = px.line(
            iv,
            x="strike",
            y="ce",
            markers=True,
            template="plotly_dark"
        )

        st.plotly_chart(fig,use_container_width=True)

# ----------------------------------------------------
# VOLATILITY SURFACE
# ----------------------------------------------------

elif page == "Volatility Surface":

    st.subheader("🌐 Volatility Surface")

    if "ce" not in df_filtered.columns:
        st.warning("IV column 'ce' not found")
    else:
        pivot = df_filtered.pivot_table(
            values="ce",
            index="strike",
            columns="expiry",
            aggfunc="mean"
        )

        fig = px.imshow(
            pivot,
            aspect="auto",
            color_continuous_scale="Turbo",
            template="plotly_dark"
        )

        st.plotly_chart(fig,use_container_width=True)

# ----------------------------------------------------
# DATA PREVIEW
# ----------------------------------------------------

st.divider()

st.subheader("📋 Dataset Preview")

st.dataframe(df_filtered.head(50),use_container_width=True)