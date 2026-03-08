import streamlit as st
import pandas as pd
import glob
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.title("📊 Open Interest Analysis")

# ----------------------------------------------------
# DATA LOADING
# ----------------------------------------------------

@st.cache_data
def load_data():
    files = glob.glob("data/*.csv")

    if len(files) == 0:
        return pd.DataFrame()

    df = pd.concat([pd.read_csv(file) for file in files])
    df["datetime"] = pd.to_datetime(df["datetime"])

    return df


df = load_data()

if df.empty:
    st.warning("No CSV files found in data folder")
    st.stop()

# ----------------------------------------------------
# SIDEBAR FILTERS
# ----------------------------------------------------

st.sidebar.header("🔎 Filters")

expiry = st.sidebar.selectbox(
    "Select Expiry",
    sorted(df["expiry"].unique())
)

df = df[df["expiry"] == expiry]

# Strike range
min_strike = int(df["strike"].min())
max_strike = int(df["strike"].max())

strike_range = st.sidebar.slider(
    "Select Strike Range",
    min_strike,
    max_strike,
    (min_strike, max_strike)
)

df = df[
    (df["strike"] >= strike_range[0]) &
    (df["strike"] <= strike_range[1])
]

# ----------------------------------------------------
# GROUP OI
# ----------------------------------------------------

oi_group = df.groupby("strike")[["oi_CE", "oi_PE"]].sum().reset_index()

# ----------------------------------------------------
# OI DISTRIBUTION CHART
# ----------------------------------------------------

st.subheader("📊 Call vs Put Open Interest")

fig = px.bar(
    oi_group,
    x="strike",
    y=["oi_CE", "oi_PE"],
    barmode="group",
    title="Call vs Put Open Interest by Strike"
)

fig.update_layout(
    template="plotly_dark",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# OI DIFFERENCE (MARKET BIAS)
# ----------------------------------------------------

st.subheader("📈 Market Bias (OI Difference)")

oi_group["oi_diff"] = oi_group["oi_PE"] - oi_group["oi_CE"]

fig2 = px.bar(
    oi_group,
    x="strike",
    y="oi_diff",
    title="Put - Call Open Interest"
)

fig2.update_layout(template="plotly_dark")

st.plotly_chart(fig2, use_container_width=True)

# ----------------------------------------------------
# SUPPORT / RESISTANCE LEVELS
# ----------------------------------------------------

st.subheader("📍 Key OI Levels")

max_call = oi_group.loc[oi_group["oi_CE"].idxmax(), "strike"]
max_put = oi_group.loc[oi_group["oi_PE"].idxmax(), "strike"]

col1, col2 = st.columns(2)

col1.metric("Strong Call OI (Resistance)", max_call)
col2.metric("Strong Put OI (Support)", max_put)

# ----------------------------------------------------
# OI HEATMAP
# ----------------------------------------------------

st.subheader("🔥 Open Interest Heatmap")

heatmap_df = df.pivot_table(
    values="oi_CE",
    index="strike",
    columns="datetime",
    aggfunc="sum"
)

fig3 = px.imshow(
    heatmap_df,
    aspect="auto",
    title="Call Open Interest Heatmap"
)

fig3.update_layout(template="plotly_dark")

st.plotly_chart(fig3, use_container_width=True)

# ----------------------------------------------------
# DATA PREVIEW
# ----------------------------------------------------

st.subheader("📋 Data Preview")

st.dataframe(df.head(50), use_container_width=True)