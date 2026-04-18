from backend.db.performance_compare import benchmark_cursor_batches, benchmark_full_scan, get_source_collection


def main():
    collection, source_name = get_source_collection()
    full_scan = benchmark_full_scan(collection)
    cursor_batches = benchmark_cursor_batches(collection, batch_size=500)

    print("Cursor Benchmark Walkthrough")
    print("=" * 60)
    print(f"Source collection: {source_name}")
    print()
    print("Full scan result")
    print(full_scan)
    print()
    print("Cursor batch result")
    print(cursor_batches)
    print()

    if full_scan["seconds"] > 0:
        print(f"Cursor/full ratio: {cursor_batches['seconds'] / full_scan['seconds']:.4f}")


if __name__ == "__main__":
    main()
