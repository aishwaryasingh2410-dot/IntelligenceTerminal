from datetime import datetime, timezone
from typing import Any, Dict, Optional

from backend.db.connection import processing_checkpoints_collection


def get_checkpoint(pipeline_name: str) -> Optional[Dict[str, Any]]:
    return processing_checkpoints_collection.find_one({"pipeline": pipeline_name})


def get_last_seen(pipeline_name: str, field: str = "last_seen"):
    checkpoint = get_checkpoint(pipeline_name)
    return checkpoint.get(field) if checkpoint else None


def save_checkpoint(
    pipeline_name: str,
    last_seen,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    payload = {
        "pipeline": pipeline_name,
        "last_seen": last_seen,
        "metadata": metadata or {},
        "updated_at": datetime.now(timezone.utc),
    }
    processing_checkpoints_collection.update_one(
        {"pipeline": pipeline_name},
        {"$set": payload},
        upsert=True,
    )
