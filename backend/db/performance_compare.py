from time import perf_counter

from backend.db.connection import options_collection, raw_options_collection
from backend.db.cursor_reader import fetch_in_batches


def get_source_collection():
    if raw_options_collection.estimated_document_count() > 0:
        return raw_options_collection, "raw_options_chain"
    return options_collection, "options_chain"


def benchmark_full_scan(collection):
    start = perf_counter()
    rows = list(collection.find({}))
    elapsed = perf_counter() - start
    return {"mode": "full_scan", "rows": len(rows), "seconds": elapsed}


def benchmark_cursor_batches(collection, batch_size=500):
    start = perf_counter()
    total_rows = 0
    batches = 0

    for batch in fetch_in_batches(collection=collection, batch_size=batch_size):
        total_rows += len(batch)
        batches += 1

    elapsed = perf_counter() - start
    return {
        "mode": "cursor_batches",
        "rows": total_rows,
        "batches": batches,
        "batch_size": batch_size,
        "seconds": elapsed,
    }


def main():
    collection, source_name = get_source_collection()
    full_scan = benchmark_full_scan(collection)
    cursor_batches = benchmark_cursor_batches(collection)

    print("Cursor Optimization Benchmark")
    print("=" * 60)
    print(f"Collection: {source_name}")
    print()
    print("Full scan")
    print(f"Rows: {full_scan['rows']}")
    print(f"Seconds: {full_scan['seconds']:.4f}")
    print()
    print("Cursor batches")
    print(f"Rows: {cursor_batches['rows']}")
    print(f"Batches: {cursor_batches['batches']}")
    print(f"Batch size: {cursor_batches['batch_size']}")
    print(f"Seconds: {cursor_batches['seconds']:.4f}")
    print()

    if full_scan["seconds"] > 0:
        speed_ratio = cursor_batches["seconds"] / full_scan["seconds"]
        print(f"Cursor/Full time ratio: {speed_ratio:.4f}")


if __name__ == "__main__":
    main()
