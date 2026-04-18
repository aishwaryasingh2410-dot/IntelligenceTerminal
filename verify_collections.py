from pprint import pprint

from backend.db.connection import db

COLLECTIONS = [
    "raw_options_chain",
    "analytics_snapshots",
    "anomaly_signals",
    "latest_market_summary",
    "processing_checkpoints",
]


def project_sample(name, sample):
    if not sample:
        return "No documents found"

    if name == "raw_options_chain":
        keys = ["symbol", "datetime", "expiry", "strike", "oi_CE", "oi_PE"]
    elif name == "analytics_snapshots":
        keys = ["source", "snapshot_time", "record_count", "pcr", "sentiment", "max_pain_strike"]
    elif name == "anomaly_signals":
        keys = ["snapshot_time", "strike", "total_oi", "anomaly_score"]
    elif name == "latest_market_summary":
        keys = ["summary_key", "source", "updated_at", "pcr", "sentiment", "max_pain_strike"]
    else:
        keys = ["pipeline", "last_seen", "updated_at", "metadata"]

    return {key: sample.get(key) for key in keys if key in sample}


def main():
    print("Collection Verification")
    print("=" * 60)

    for name in COLLECTIONS:
        collection = db[name]
        count = collection.count_documents({})
        sample = collection.find_one(sort=[("_id", -1)])

        print(f"\n{name}")
        print("-" * 60)
        print(f"Count: {count}")
        print("Latest sample:")
        pprint(project_sample(name, sample), sort_dicts=False)


if __name__ == "__main__":
    main()
