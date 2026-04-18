from datetime import datetime, timezone
from typing import Dict, Iterable, List

import pandas as pd

from backend.analysis import (
    calculate_max_pain,
    calculate_pcr,
    calculate_pcr_timeseries,
    calculate_rolling_pcr_summary,
    calculate_top_oi_strikes,
    classify_sentiment,
    detect_unusual_oi,
    calculate_oi_change_by_strike,
    summarize_call_put_oi,
)
from backend.db.checkpoints import get_last_seen, save_checkpoint
from backend.db.connection import (
    analytics_snapshots_collection,
    anomaly_signals_collection,
    latest_market_summary_collection,
    options_collection,
    raw_options_collection,
)
from backend.db.cursor_reader import fetch_in_batches

PIPELINE_NAME = "incremental_options_analytics"


def _source_collection():
    if raw_options_collection.estimated_document_count() > 0:
        return raw_options_collection, "raw_options_chain"
    return options_collection, "options_chain"


def _to_dataframe(batch: Iterable[Dict]) -> pd.DataFrame:
    df = pd.DataFrame(list(batch))
    if df.empty:
        return df
    if "_id" in df.columns:
        df = df.copy()
    return df


def compute_snapshot(df: pd.DataFrame, source: str) -> Dict:
    pcr_metrics = calculate_pcr(df)
    max_pain = calculate_max_pain(df)
    top_oi = calculate_top_oi_strikes(df)
    call_put = summarize_call_put_oi(df)
    unusual_oi = detect_unusual_oi(df)
    rolling_pcr = calculate_rolling_pcr_summary(df)
    pcr_timeseries = calculate_pcr_timeseries(df, limit=50)
    oi_change = calculate_oi_change_by_strike(df, limit=10)

    snapshot_time = datetime.now(timezone.utc)
    return {
        "source": source,
        "snapshot_time": snapshot_time,
        "record_count": int(len(df)),
        "pcr": pcr_metrics["pcr"],
        "call_oi": call_put["call_oi"],
        "put_oi": call_put["put_oi"],
        "sentiment": classify_sentiment(pcr_metrics["pcr"]),
        "max_pain_strike": max_pain["max_pain_strike"],
        "pain_value": max_pain["pain_value"],
        "top_oi_strikes": top_oi,
        "unusual_oi": unusual_oi,
        "rolling_pcr": rolling_pcr,
        "pcr_timeseries": pcr_timeseries,
        "oi_change_by_strike": oi_change,
    }


def persist_snapshot(snapshot: Dict) -> None:
    analytics_snapshots_collection.insert_one(snapshot)

    anomaly_docs: List[Dict] = []
    for signal in snapshot["unusual_oi"]:
        anomaly_docs.append(
            {
                **signal,
                "snapshot_time": snapshot["snapshot_time"],
                "source": snapshot["source"],
            }
        )
    if anomaly_docs:
        anomaly_signals_collection.insert_many(anomaly_docs)


def persist_market_summary(summary: Dict) -> None:
    latest_market_summary_collection.update_one(
        {"summary_key": "global"},
        {
            "$set": {
                **summary,
                "summary_key": "global",
                "updated_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )


def run_incremental(batch_size: int = 500) -> Dict:
    collection, source_name = _source_collection()
    last_seen = get_last_seen(PIPELINE_NAME)
    batches_processed = 0
    records_processed = 0
    latest_cursor = last_seen

    for batch in fetch_in_batches(
        collection=collection,
        batch_size=batch_size,
        cursor_field="_id",
        last_seen=last_seen,
    ):
        df = _to_dataframe(batch)
        if df.empty:
            continue

        snapshot = compute_snapshot(df, source=source_name)
        persist_snapshot(snapshot)

        latest_cursor = batch[-1]["_id"]
        batches_processed += 1
        records_processed += len(batch)

    full_df = pd.DataFrame(list(collection.find({})))
    if not full_df.empty:
        full_summary = compute_snapshot(full_df, source=source_name)
        persist_market_summary(full_summary)

    if latest_cursor is not None:
        save_checkpoint(
            PIPELINE_NAME,
            latest_cursor,
            metadata={
                "batches_processed": batches_processed,
                "records_processed": records_processed,
                "source": source_name,
            },
        )

    return {
        "pipeline": PIPELINE_NAME,
        "source": source_name,
        "batches_processed": batches_processed,
        "records_processed": records_processed,
        "last_seen": latest_cursor,
    }


if __name__ == "__main__":
    result = run_incremental()
    print(result)
