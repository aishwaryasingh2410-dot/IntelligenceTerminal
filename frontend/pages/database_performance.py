import streamlit as st
import pandas as pd
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


st.title("⚡ Database Performance Benchmark")
st.caption("Comparing normal vs cursor-optimized MongoDB queries")

# Use the cached collection from app.py if available
collection = None
try:
    from pymongo import MongoClient
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://aishwaryasingh2410_db_user:rZPAw8NKMJcW838v@cluster0.sdicuyj.mongodb.net/cursor_database")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    collection = client["cursor_database"]["options_chain"]
    st.success("✅ MongoDB Connected")
except Exception as e:
    st.error(f"MongoDB connection failed: {e}")
    st.stop()

# -----------------------------
# BENCHMARK FUNCTIONS
# -----------------------------
def normal_query(n=500):
    start = time.time()
    list(collection.find().limit(n))
    return round((time.time() - start) * 1000, 2)

def optimized_query(n=500, batch=100):
    start = time.time()
    cursor = collection.find().batch_size(batch)
    data = []
    for doc in cursor:
        data.append(doc)
        if len(data) >= n:
            break
    return round((time.time() - start) * 1000, 2)

# -----------------------------
# RUN BENCHMARK UI
# -----------------------------
st.subheader("🔧 Benchmark Settings")
col1, col2 = st.columns(2)
limit = col1.slider("Documents to fetch", 100, 2000, 500, step=100)
batch = col2.slider("Cursor batch size", 10, 500, 100, step=10)

if st.button("▶ Run Benchmark", use_container_width=True):
    with st.spinner("Running benchmark..."):
        normal_time = normal_query(limit)
        optimized_time = optimized_query(limit, batch)

    improvement = round(((normal_time - optimized_time) / normal_time) * 100, 1)

    col1, col2, col3 = st.columns(3)
    col1.metric("Normal Query", f"{normal_time} ms")
    col2.metric("Cursor Optimized", f"{optimized_time} ms",
                delta=f"{improvement}% faster" if optimized_time < normal_time else f"{abs(improvement)}% slower",
                delta_color="inverse")
    col3.metric("Documents Fetched", limit)

    st.divider()
    st.subheader("📊 Query Time Comparison")
    df = pd.DataFrame({
        "Method": ["Normal Query", "Cursor Optimized"],
        "Time (ms)": [normal_time, optimized_time]
    })
    st.bar_chart(df.set_index("Method"))

    st.subheader("📋 Results")
    if optimized_time < normal_time:
        st.success(f"✅ Cursor optimization saved {round(normal_time - optimized_time, 2)} ms ({improvement}% faster)")
    else:
        st.info("ℹ️ Normal query was faster this run — results vary with network latency")

else:
    st.info("👆 Click 'Run Benchmark' to start the performance test")

# -----------------------------
# MULTI-BATCH BENCHMARK
# -----------------------------
st.divider()
st.subheader("📈 Batch Size Performance Analysis")

if st.button("▶ Run Multi-Batch Analysis", use_container_width=True):
    results = []
    batch_sizes = [10, 50, 100, 250, 500]
    with st.spinner("Testing different batch sizes..."):
        for b in batch_sizes:
            t = optimized_query(500, b)
            results.append({"Batch Size": b, "Query Time (ms)": t})
    df2 = pd.DataFrame(results)
    st.bar_chart(df2.set_index("Batch Size"))
    st.dataframe(df2, use_container_width=True)