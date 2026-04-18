from typing import Dict, List

import pandas as pd

from backend.analysis.pcr import calculate_pcr


def calculate_pcr_timeseries(df: pd.DataFrame, limit: int = 50) -> List[Dict]:
    if df.empty or "datetime" not in df.columns:
        return []

    normalized = df.rename(columns={"oi_ce": "oi_CE", "oi_pe": "oi_PE"}).copy()
    normalized["datetime"] = pd.to_datetime(normalized["datetime"], errors="coerce")
    normalized = normalized.dropna(subset=["datetime"])

    if normalized.empty:
        return []

    rows: List[Dict] = []
    for timestamp, group in normalized.groupby("datetime", sort=True):
        metrics = calculate_pcr(group)
        rows.append(
            {
                "datetime": timestamp.isoformat(),
                "pcr": round(metrics["pcr"], 6),
                "call_oi": metrics["call_oi"],
                "put_oi": metrics["put_oi"],
            }
        )

    return rows[-limit:]


def calculate_rolling_pcr_summary(df: pd.DataFrame, window: int = 5) -> Dict:
    timeseries = calculate_pcr_timeseries(df, limit=200)
    if not timeseries:
        return {"latest_pcr": 0.0, "rolling_pcr": 0.0, "samples": 0}

    frame = pd.DataFrame(timeseries)
    frame["rolling_pcr"] = frame["pcr"].rolling(window=window, min_periods=1).mean()
    latest = frame.iloc[-1]
    return {
        "latest_pcr": float(latest["pcr"]),
        "rolling_pcr": float(latest["rolling_pcr"]),
        "samples": int(len(frame)),
    }
