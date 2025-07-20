from fastapi import APIRouter, Depends
import os
import psutil
import gc
import tracemalloc
import sys
from collections import defaultdict
from open_webui.utils.auth import get_current_user

router = APIRouter(tags=["debug"])


@router.get("/memory")
async def memory_usage(user=Depends(get_current_user)):
    """Get detailed memory usage (admin only)"""
    if user.role != "admin":
        return {"error": "Unauthorized"}

    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    # Get allocation tracking
    tracemalloc.start()
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("lineno")
    tracemalloc.stop()

    # Get object-level memory usage using garbage collector
    gc.collect()  # Force garbage collection to get accurate counts

    # Count objects by type
    object_counts = defaultdict(int)
    object_sizes = defaultdict(int)

    for obj in gc.get_objects():
        obj_type = type(obj).__name__
        object_counts[obj_type] += 1
        try:
            # Get object size
            obj_size = sys.getsizeof(obj)
            object_sizes[obj_type] += obj_size
        except (TypeError, AttributeError):
            # Some objects may not support getsizeof
            pass

    # Sort by memory usage and get top 10
    top_objects_by_memory = sorted(
        object_sizes.items(), key=lambda x: x[1], reverse=True
    )[:10]

    # Sort by count and get top 10
    top_objects_by_count = sorted(
        object_counts.items(), key=lambda x: x[1], reverse=True
    )[:10]

    return {
        "rss": memory_info.rss / (1024 * 1024),  # RSS in MB
        "vms": memory_info.vms / (1024 * 1024),  # VMS in MB
        "top_memory_allocations": [
            {
                "file": stat.traceback[0].filename,
                "line": stat.traceback[0].lineno,
                "size_mb": stat.size / (1024 * 1024),
            }
            for stat in top_stats[:10]
        ],
        "top_objects_by_memory": [
            {
                "object_type": obj_type,
                "total_size_mb": size / (1024 * 1024),
                "count": object_counts[obj_type],
                "avg_size_bytes": (
                    size / object_counts[obj_type] if object_counts[obj_type] > 0 else 0
                ),
            }
            for obj_type, size in top_objects_by_memory
        ],
        "top_objects_by_count": [
            {
                "object_type": obj_type,
                "count": count,
                "total_size_mb": object_sizes[obj_type] / (1024 * 1024),
                "avg_size_bytes": object_sizes[obj_type] / count if count > 0 else 0,
            }
            for obj_type, count in top_objects_by_count
        ],
        "total_objects": len(gc.get_objects()),
        "garbage_collected": gc.collect(),
    }
