import pandas as pd

from backend.db.connection import (
    analytics_snapshots_collection,
    anomaly_signals_collection,
    latest_market_summary_collection,
    options_collection,
    raw_options_collection,
)


# ---------------------------------------------------
# CURSOR QUERY
# Used for incremental streaming of options data
# ---------------------------------------------------

def get_options_cursor(last_seen=None, limit=100):

    query = {}

    if last_seen:
        query["datetime"] = {"$gt": last_seen}

    collection = raw_options_collection if raw_options_collection.estimated_document_count() > 0 else options_collection

    cursor = (
        collection
        .find(query)
        .sort("datetime", 1)
        .limit(limit)
    )

    data = list(cursor)

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    if "_id" in df.columns:
        df.drop(columns=["_id"], inplace=True)

    return df


# ---------------------------------------------------
# AGGREGATION QUERY
# MongoDB Pipeline for Top Open Interest Strikes
# ---------------------------------------------------

def get_top_oi_strikes(expiry, limit=10):

    pipeline = [

        {
            "$match": {
                "expiry": expiry
            }
        },

        {
            "$group": {
                "_id": "$strike",

                "total_oi": {
                    "$sum": {
                        "$add": ["$oi_ce", "$oi_pe"]
                    }
                }
            }
        },

        {
            "$sort": {
                "total_oi": -1
            }
        },

        {
            "$limit": limit
        }

    ]

    collection = raw_options_collection if raw_options_collection.estimated_document_count() > 0 else options_collection
    result = list(collection.aggregate(pipeline))

    if not result:
        return pd.DataFrame()

    df = pd.DataFrame(result)

    df.rename(columns={"_id": "strike"}, inplace=True)

    return df


def get_latest_snapshot():
    return analytics_snapshots_collection.find_one(sort=[("snapshot_time", -1)])


def get_latest_anomaly_signals(limit=5):
    cursor = (
        anomaly_signals_collection
        .find({}, {"_id": 0})
        .sort("snapshot_time", -1)
        .limit(limit)
    )
    return list(cursor)


def get_latest_market_summary():
    return latest_market_summary_collection.find_one({"summary_key": "global"})
