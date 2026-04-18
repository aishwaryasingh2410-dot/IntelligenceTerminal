from typing import Dict, Iterator, List, Optional

from pymongo.collection import Collection


def build_incremental_query(
    cursor_field: str = "_id",
    last_seen=None,
    extra_filters: Optional[Dict] = None,
) -> Dict:
    query = dict(extra_filters or {})
    if last_seen is not None:
        query[cursor_field] = {"$gt": last_seen}
    return query


def fetch_in_batches(
    collection: Collection,
    batch_size: int = 500,
    cursor_field: str = "_id",
    last_seen=None,
    extra_filters: Optional[Dict] = None,
    projection: Optional[Dict] = None,
) -> Iterator[List[Dict]]:
    query = build_incremental_query(
        cursor_field=cursor_field,
        last_seen=last_seen,
        extra_filters=extra_filters,
    )

    cursor = (
        collection.find(query, projection)
        .sort(cursor_field, 1)
        .batch_size(batch_size)
    )

    batch: List[Dict] = []
    for document in cursor:
        batch.append(document)
        if len(batch) >= batch_size:
            yield batch
            batch = []

    if batch:
        yield batch


def fetch_latest_cursor_value(
    collection: Collection,
    cursor_field: str = "_id",
    extra_filters: Optional[Dict] = None,
):
    query = dict(extra_filters or {})
    latest = collection.find_one(query, sort=[(cursor_field, -1)])
    return latest.get(cursor_field) if latest else None
