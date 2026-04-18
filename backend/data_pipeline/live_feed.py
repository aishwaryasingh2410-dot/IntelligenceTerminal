import yfinance as yf
import time
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("Missing MONGO_URI environment variable. Set it in .env or the environment.")
client = MongoClient(MONGO_URI)
collection = client["cursor_database"]["nifty_ticks"]
POLL_SECONDS = int(os.getenv("NIFTY_POLL_SECONDS", "15"))

def fetch_and_store():
    nifty = yf.Ticker("^NSEI")
    hist = nifty.history(period="1d", interval="1m")
    if hist.empty:
        print("No NIFTY ticks returned")
        return

    hist.reset_index(inplace=True)
    row = hist.iloc[-1]
    doc = {
        "datetime": row["Datetime"].isoformat(),
        "open": float(row["Open"]),
        "high": float(row["High"]),
        "low": float(row["Low"]),
        "close": float(row["Close"]),
        "volume": float(row["Volume"]),
    }

    # Upsert only the latest one-minute candle to keep writes light.
    result = collection.update_one(
        {"datetime": doc["datetime"]},
        {"$set": doc},
        upsert=True
    )

    action = "Inserted" if result.upserted_id is not None else "Updated"
    print(f"{action} NIFTY tick {doc['datetime']} close={doc['close']}")

if __name__ == "__main__":
    while True:
        try:
            fetch_and_store()
        except Exception as exc:
            print(f"live_feed error: {exc}")
        time.sleep(POLL_SECONDS)
