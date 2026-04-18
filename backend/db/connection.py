import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "cursor_database")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

RAW_OPTIONS_COLLECTION = "raw_options_chain"
LEGACY_OPTIONS_COLLECTION = "options_chain"
NIFTY_TICKS_COLLECTION = "nifty_ticks"
ANALYTICS_SNAPSHOTS_COLLECTION = "analytics_snapshots"
ANOMALY_SIGNALS_COLLECTION = "anomaly_signals"
PROCESSING_CHECKPOINTS_COLLECTION = "processing_checkpoints"
LATEST_MARKET_SUMMARY_COLLECTION = "latest_market_summary"

raw_options_collection = db[RAW_OPTIONS_COLLECTION]
options_collection = db[LEGACY_OPTIONS_COLLECTION]
nifty_ticks_collection = db[NIFTY_TICKS_COLLECTION]
analytics_snapshots_collection = db[ANALYTICS_SNAPSHOTS_COLLECTION]
anomaly_signals_collection = db[ANOMALY_SIGNALS_COLLECTION]
processing_checkpoints_collection = db[PROCESSING_CHECKPOINTS_COLLECTION]
latest_market_summary_collection = db[LATEST_MARKET_SUMMARY_COLLECTION]


def get_database():
    return db


def get_collection(name):
    return db[name]
