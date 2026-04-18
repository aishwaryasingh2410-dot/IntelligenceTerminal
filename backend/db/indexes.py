from backend.db.connection import (
    analytics_snapshots_collection,
    anomaly_signals_collection,
    latest_market_summary_collection,
    processing_checkpoints_collection,
    raw_options_collection,
)


def ensure_indexes() -> None:
    raw_options_collection.create_index("datetime")
    raw_options_collection.create_index("strike")
    raw_options_collection.create_index("expiry")
    raw_options_collection.create_index([("expiry", 1), ("strike", 1)])
    raw_options_collection.create_index([("datetime", 1), ("strike", 1)])
    raw_options_collection.create_index([("symbol", 1), ("expiry", 1), ("datetime", 1)])

    analytics_snapshots_collection.create_index("snapshot_time")
    analytics_snapshots_collection.create_index([("source", 1), ("snapshot_time", -1)])

    anomaly_signals_collection.create_index("snapshot_time")
    anomaly_signals_collection.create_index([("strike", 1), ("snapshot_time", -1)])

    latest_market_summary_collection.create_index("summary_key", unique=True)
    latest_market_summary_collection.create_index("updated_at")

    processing_checkpoints_collection.create_index("pipeline", unique=True)


if __name__ == "__main__":
    ensure_indexes()
    print("Indexes created successfully")
