# -----------------------------
# IMPORTS
# -----------------------------
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import glob
import time
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import IsolationForest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from backend.queries.options_queries import (
    get_options_cursor,
    get_top_oi_strikes
)

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

from dotenv import load_dotenv, find_dotenv

# -----------------------------
# MONGODB CONNECTION — cached so it only runs ONCE per session
# -----------------------------
load_dotenv(find_dotenv())

@st.cache_resource
def get_mongo_collection():
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        raise RuntimeError("Missing MONGO_URI environment variable. Set it in .env or the environment.")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client["cursor_database"]
        collection = db["options_chain"]
        # warm-up ping
        start = time.time()
        list(collection.find().limit(10))
        query_time = round((time.time() - start) * 1000, 2)
        return collection, query_time, None
    except PyMongoError as e:
        return None, None, str(e)

collection, query_time, mongo_error = get_mongo_collection()

if mongo_error:
    st.warning(f"MongoDB connection failed: {mongo_error}")
else:
    st.success("✅ MongoDB Connected")

# -----------------------------
# LOAD CSV DATA — cached so it only runs ONCE
# -----------------------------
@st.cache_data
def load_data():
    DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    if not files:
        return pd.DataFrame(), []
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df.columns = df.columns.str.strip().str.lower()
    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    expiries = sorted(df["expiry"].dropna().unique())
    return df, expiries

df_raw, expiries = load_data()

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
    expiry = st.selectbox("Select Expiry", expiries)
    min_strike = int(df_raw["strike"].min())
    max_strike = int(df_raw["strike"].max())
    strike_range = st.slider("Strike Range", min_strike, max_strike, (min_strike, max_strike))

# Save to session_state so all pages can access filters
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
# AI ANOMALY DETECTION — cached per expiry+strike selection
# -----------------------------
@st.cache_data
def run_anomaly_detection(df_json):
    df = pd.read_json(df_json)
    features = df[["oi_ce", "oi_pe", "volume_ce", "volume_pe"]].fillna(0)
    model = IsolationForest(contamination=0.02, random_state=42)
    df["anomaly"] = model.fit_predict(features)
    return df

df = run_anomaly_detection(df.to_json())

# -----------------------------
# HEADER
# -----------------------------
st.title("📊 Intelligence Terminal")
st.caption("AI-powered options analytics with database performance monitoring")

# -----------------------------
# TOP METRICS
# -----------------------------
spot = round(df["spot_close"].iloc[-1], 2)
total_volume = int(df["volume_ce"].sum() + df["volume_pe"].sum())
total_oi = int(df["oi_ce"].sum() + df["oi_pe"].sum())
pcr = round(df["volume_pe"].sum() / (df["volume_ce"].sum() + 1), 2)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Spot Price", spot)
col2.metric("Total Volume", f"{total_volume:,}")
col3.metric("Total OI", f"{total_oi:,}")
col4.metric("PCR", pcr)
col5.metric("DB Query Time", query_time if query_time else "N/A")

st.divider()

# -----------------------------
# ROW 1 : PRICE + ANOMALY
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Price Analysis")
    fig = px.line(df, x="datetime", y="spot_close")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("AI Anomaly Detection")
    fig = px.scatter(df, x="strike", y="volume_ce", color="anomaly")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# ROW 2 : OI + VOLUME
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Open Interest Distribution")
    oi = df.groupby("strike")[["oi_ce", "oi_pe"]].sum().reset_index()
    fig = px.bar(oi, x="strike", y=["oi_ce", "oi_pe"], barmode="group")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Volume Heatmap")
    vol = df.groupby("strike")[["volume_ce", "volume_pe"]].sum()
    fig = px.imshow(vol)
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# VOLATILITY ANALYSIS
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Volatility Smile")
    iv = df.groupby("strike")["ce"].mean().reset_index()
    fig = px.line(iv, x="strike", y="ce", markers=True)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Volatility Surface")
    pivot = df.pivot_table(values="ce", index="strike", columns="expiry", aggfunc="mean")
    fig = px.imshow(pivot, aspect="auto", color_continuous_scale="Turbo")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# MONGODB AGGREGATION — cached per expiry
# -----------------------------
st.divider()
st.subheader("Top Open Interest Strikes (MongoDB Aggregation)")

@st.cache_data(ttl=60)  # re-fetches every 60 seconds
def fetch_top_oi(expiry):
    return get_top_oi_strikes(expiry)

try:
    df_oi = fetch_top_oi(expiry)
    if not df_oi.empty:
        fig = px.bar(df_oi, x="strike", y="total_oi")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No MongoDB aggregation data found")
except Exception as e:
    st.error(f"Aggregation failed: {e}")

# -----------------------------
# CURSOR PERFORMANCE BENCHMARK — cached so it doesn't re-run on every click
# -----------------------------
if collection is not None:
    st.subheader("⚡ Cursor Performance Benchmark")

    @st.cache_data(ttl=120)
    def run_benchmark():
        results = []
        for batch in [10, 100, 1000]:
            start = time.time()
            list(collection.find().limit(batch))
            results.append((batch, round((time.time() - start) * 1000, 2)))
        return pd.DataFrame(results, columns=["Batch Size", "Query Time (ms)"])

    bench = run_benchmark()
    st.bar_chart(bench.set_index("Batch Size"))

# -----------------------------
# CURSOR QUERY DEMO
# -----------------------------
st.subheader("⚡ MongoDB Cursor Query (Sample)")

try:
    data = get_options_cursor(limit=20)
    st.dataframe(data)
except PyMongoError as e:
    st.warning(f"MongoDB query failed: {e}")

# -----------------------------
# DATA PREVIEW
# -----------------------------
st.divider()
st.subheader("Dataset Preview")
st.dataframe(df.head(50), use_container_width=True)
