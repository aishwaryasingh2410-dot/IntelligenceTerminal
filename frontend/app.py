
# -----------------------------
# IMPORTS
# -----------------------------
import sys
import os
import glob

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from sklearn.ensemble import IsolationForest


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Options Intelligence Terminal",
    layout="wide",
    page_icon="📊"
)

px.defaults.template = "plotly_dark"


# -----------------------------
# STYLING
# -----------------------------
st.markdown("""
<style>
.stApp { background-color: #0E1117; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#111827,#1f2937); }
h1,h2,h3,h4 { color: white; }
.block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)


# -----------------------------
# LOAD CSV DATA — cached so it only runs ONCE
# -----------------------------
@st.cache_data
def load_data():
    DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))

    if not files:
        return pd.DataFrame(), []

    df = pd.concat(
        [pd.read_csv(f) for f in files],
        ignore_index=True
    )

    df.columns = df.columns.str.strip().str.lower()

    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(
            df["datetime"],
            errors="coerce"
        )

    expiries = sorted(
        df["expiry"].dropna().unique()
    )

    return df, expiries


df_raw, expiries = load_data()


@st.cache_data(ttl=30)
def get_live_market_snapshot():
    try:
        response = requests.get(
            "http://localhost:5000/api/options/live-market",
            timeout=5,
        )
        if response.status_code == 200:
            data = response.json()
            return data
    except Exception:
        return None
    return None


# -----------------------------
# DATA VALIDATION
# -----------------------------
if df_raw.empty:
    st.error("❌ No CSV files found in data folder")
    st.stop()


# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.title("📊 Options Terminal")

    st.write("CSV files loaded:", len(expiries))
    st.write("Total rows:", len(df_raw))

    st.divider()

    expiry = st.selectbox(
        "Select Expiry",
        expiries
    )

    min_strike = int(df_raw["strike"].min())
    max_strike = int(df_raw["strike"].max())

    strike_range = st.slider(
        "Strike Range",
        min_strike,
        max_strike,
        (min_strike, max_strike)
    )


# Save filters to session state
st.session_state["expiry"] = expiry
st.session_state["strike_range"] = strike_range


# -----------------------------
# FILTER DATA
# -----------------------------
df = df_raw[
    (df_raw["expiry"] == expiry) &
    (df_raw["strike"] >= strike_range[0]) &
    (df_raw["strike"] <= strike_range[1])
].copy()


if df.empty:
    st.warning("No data available for selected filters")
    st.stop()


# -----------------------------
# AI ANOMALY DETECTION
# -----------------------------
@st.cache_data
def run_anomaly_detection(df):

    df = df.copy()

    features = df[
        [
            "oi_ce",
            "oi_pe",
            "volume_ce",
            "volume_pe"
        ]
    ].fillna(0)

    model = IsolationForest(
        contamination=0.02,
        random_state=42
    )

    df["anomaly"] = model.fit_predict(features)

    return df


df = run_anomaly_detection(df)


# -----------------------------
# HEADER
# -----------------------------
st.title("📊 Intelligence Terminal")

st.caption(
    "AI-powered options market analytics"
)


# -----------------------------
# TOP METRICS
# -----------------------------
market_snapshot = get_live_market_snapshot()
spot_value = None
source_label = "CSV data"

if market_snapshot:
    spot_value = market_snapshot.get("spot") or market_snapshot.get("price")
    source_label = market_snapshot.get("source", "Live market")

if spot_value is None:
    spot = round(df["spot_close"].iloc[-1], 2)
else:
    spot = round(float(spot_value), 2)

if market_snapshot:
    st.caption(f"Live market feed: {source_label} • {market_snapshot.get('symbol', 'N/A')} • {spot}")

total_volume = int(
    df["volume_ce"].sum()
    +
    df["volume_pe"].sum()
)

total_oi = int(
    df["oi_ce"].sum()
    +
    df["oi_pe"].sum()
)

pcr = round(
    df["volume_pe"].sum()
    /
    (df["volume_ce"].sum() + 1),
    2
)


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Spot Price",
    spot
)

col2.metric(
    "Total Volume",
    f"{total_volume:,}"
)

col3.metric(
    "Total OI",
    f"{total_oi:,}"
)

col4.metric(
    "PCR",
    pcr
)


st.divider()


# -----------------------------
# ROW 1 : PRICE + ANOMALY
# -----------------------------
col1, col2 = st.columns(2)


with col1:

    st.subheader("Price Analysis")

    fig = px.line(
        df,
        x="datetime",
        y="spot_close"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with col2:

    st.subheader("AI Anomaly Detection")

    fig = px.scatter(
        df,
        x="strike",
        y="volume_ce",
        color="anomaly"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# -----------------------------
# ROW 2 : OI + VOLUME
# -----------------------------
col1, col2 = st.columns(2)


with col1:

    st.subheader(
        "Open Interest Distribution"
    )

    oi = (
        df.groupby("strike")[
            ["oi_ce", "oi_pe"]
        ]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        oi,
        x="strike",
        y=["oi_ce", "oi_pe"],
        barmode="group"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with col2:

    st.subheader(
        "Volume Heatmap"
    )

    vol = (
        df.groupby("strike")[
            ["volume_ce", "volume_pe"]
        ]
        .sum()
    )

    fig = px.imshow(vol)

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# -----------------------------
# VOLATILITY ANALYSIS
# -----------------------------
col1, col2 = st.columns(2)


with col1:

    st.subheader(
        "Volatility Smile"
    )

    iv = (
        df.groupby("strike")["ce"]
        .mean()
        .reset_index()
    )

    fig = px.line(
        iv,
        x="strike",
        y="ce",
        markers=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with col2:

    st.subheader(
        "Volatility Surface"
    )

    pivot = df.pivot_table(
        values="ce",
        index="strike",
        columns="expiry",
        aggfunc="mean"
    )

    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="Turbo"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# -----------------------------
# LOCAL OI ANALYSIS
# -----------------------------
st.divider()

st.subheader(
    "Top Open Interest Strikes"
)

top_oi = (
    df.groupby("strike")[
        ["oi_ce", "oi_pe"]
    ]
    .sum()
    .reset_index()
)

top_oi["total_oi"] = (
    top_oi["oi_ce"]
    +
    top_oi["oi_pe"]
)

top_oi = (
    top_oi
    .sort_values(
        "total_oi",
        ascending=False
    )
    .head(10)
)

fig = px.bar(
    top_oi,
    x="strike",
    y="total_oi",
    title="Top 10 Strikes by Open Interest"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -----------------------------
# DATA PREVIEW
# -----------------------------
st.divider()

st.subheader(
    "Dataset Preview"
)

st.dataframe(
    df.head(50),
    use_container_width=True
)

