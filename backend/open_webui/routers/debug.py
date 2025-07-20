from fastapi import APIRouter, Depends
import os
import psutil
import gc
import tracemalloc
from open_webui.utils.auth import get_current_user

router = APIRouter(tags=["debug"])

@router.get("/memory")
async def memory_usage(user = Depends(get_current_user)):
    """Get detailed memory usage (admin only)"""
    if user.role != "admin":
        return {"error": "Unauthorized"}
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    tracemalloc.start()
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    tracemalloc.stop()
    
    return {
        "rss": memory_info.rss / (1024 * 1024),  # RSS in MB
        "vms": memory_info.vms / (1024 * 1024),  # VMS in MB
        "top_memory_objects": [
            {
                "file": stat.traceback[0].filename,
                "line": stat.traceback[0].lineno,
                "size_mb": stat.size / (1024 * 1024)
            }
            for stat in top_stats[:10]
        ]
    }