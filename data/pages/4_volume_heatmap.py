import streamlit as st
import pandas as pd
import glob
import plotly.express as px

st.set_page_config(layout="wide")

st.title("🔥 Options Volume Heatmap")

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

    df["total_volume"] = df["volume_CE"] + df["volume_PE"]

    return df


df = load_data()

if df.empty:
    st.warning("No CSV files found in data folder")
    st.stop()

# ----------------------------------------------------
# SIDEBAR FILTERS
# ----------------------------------------------------

st.sidebar.header("🔎 Filters")

expiries = sorted(df["expiry"].unique())

selected_expiry = st.sidebar.multiselect(
    "Select Expiry",
    expiries,
    default=expiries
)

df = df[df["expiry"].isin(selected_expiry)]

# Strike filter
min_strike = int(df["strike"].min())
max_strike = int(df["strike"].max())

strike_range = st.sidebar.slider(
    "Strike Range",
    min_strike,
    max_strike,
    (min_strike, max_strike)
)

df = df[
    (df["strike"] >= strike_range[0]) &
    (df["strike"] <= strike_range[1])
]

# ----------------------------------------------------
# STRIKE vs EXPIRY HEATMAP
# ----------------------------------------------------

st.subheader("📊 Volume Heatmap (Strike vs Expiry)")

pivot = df.pivot_table(
    values="total_volume",
    index="strike",
    columns="expiry",
    aggfunc="sum"
)

fig = px.imshow(
    pivot,
    color_continuous_scale="Turbo",
    aspect="auto"
)

fig.update_layout(
    template="plotly_dark",
    xaxis_title="Expiry",
    yaxis_title="Strike Price",
    coloraxis_colorbar=dict(title="Volume")
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# TIME vs STRIKE HEATMAP
# ----------------------------------------------------

st.subheader("⏱ Volume Heatmap (Strike vs Time)")

time_pivot = df.pivot_table(
    values="total_volume",
    index="strike",
    columns="datetime",
    aggfunc="sum"
)

fig2 = px.imshow(
    time_pivot,
    color_continuous_scale="Turbo",
    aspect="auto"
)

fig2.update_layout(
    template="plotly_dark",
    xaxis_title="Time",
    yaxis_title="Strike"
)

st.plotly_chart(fig2, use_container_width=True)

# ----------------------------------------------------
# CE vs PE VOLUME COMPARISON
# ----------------------------------------------------

st.subheader("📊 Call vs Put Volume")

volume_group = df.groupby("strike")[["volume_CE", "volume_PE"]].sum().reset_index()

fig3 = px.bar(
    volume_group,
    x="strike",
    y=["volume_CE", "volume_PE"],
    barmode="group",
    title="Call vs Put Volume by Strike"
)

fig3.update_layout(template="plotly_dark")

st.plotly_chart(fig3, use_container_width=True)

# ----------------------------------------------------
# VOLUME SPIKE DETECTION
# ----------------------------------------------------

st.subheader("🚨 Volume Spike Detection")

threshold = df["total_volume"].quantile(0.98)

spikes = df[df["total_volume"] > threshold]

if len(spikes) > 0:
    st.dataframe(spikes.head(20), use_container_width=True)
else:
    st.success("No significant volume spikes detected")

# ----------------------------------------------------
# DATA PREVIEW
# ----------------------------------------------------

st.subheader("📋 Data Preview")

st.dataframe(df.head(50), use_container_width=True)