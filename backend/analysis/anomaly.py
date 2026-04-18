from typing import Dict, List

import pandas as pd


def detect_unusual_oi(df: pd.DataFrame, limit: int = 5) -> List[Dict]:
    if df.empty or "strike" not in df.columns:
        return []

    normalized = df.rename(columns={"oi_ce": "oi_CE", "oi_pe": "oi_PE"}).copy()
    normalized["strike"] = pd.to_numeric(normalized.get("strike"), errors="coerce")
    normalized["oi_CE"] = pd.to_numeric(normalized.get("oi_CE"), errors="coerce").fillna(0)
    normalized["oi_PE"] = pd.to_numeric(normalized.get("oi_PE"), errors="coerce").fillna(0)
    normalized = normalized.dropna(subset=["strike"])
    normalized["total_oi"] = normalized["oi_CE"] + normalized["oi_PE"]

    grouped = (
        normalized.groupby("strike", as_index=False)["total_oi"]
        .sum()
        .sort_values("total_oi", ascending=False)
        .head(limit)
    )

    if grouped.empty:
        return []

    baseline = float(grouped["total_oi"].mean()) or 1.0
    return [
        {
            "strike": float(row["strike"]),
            "total_oi": float(row["total_oi"]),
            "anomaly_score": float(row["total_oi"]) / baseline,
        }
        for _, row in grouped.iterrows()
    ]
