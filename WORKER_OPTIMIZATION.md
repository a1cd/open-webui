# Gunicorn Worker Configuration Optimization

This implementation optimizes the worker configuration for Open WebUI by implementing a more conservative worker allocation strategy that reduces memory usage while maintaining reasonable performance.

## Changes Made

### 1. Created `backend/gunicorn_conf.py`
- Conservative worker formula: `max(2, int(cpu_count * 0.5))` instead of `(2*CPU+1)`
- Worker lifecycle management with `max_requests=1000` and `max_requests_jitter=50`
- Uses `uvicorn.workers.UvicornWorker` for async support
- Configurable via environment variables:
  - `WEB_CONCURRENCY`: Override calculated worker count
  - `THREADS`: Threads per worker (default: 1)
  - `HOST`, `PORT`: Bind configuration

### 2. Updated Dependencies
- Added `gunicorn==23.0.0` to both `requirements.txt` and `pyproject.toml`

### 3. Modified Startup Scripts
- Updated `backend/start.sh` to use gunicorn with the new configuration
- Enhanced `backend/open_webui/__init__.py` CLI to support gunicorn option

## Memory Optimization

On a 4-core system:
- **Traditional formula**: (2 × 4 + 1) = 9 workers
- **Conservative formula**: max(2, int(4 × 0.5)) = 2 workers
- **Memory savings**: 77.8% fewer workers

## Configuration Examples

### Environment Variables
```bash
# Use 4 workers regardless of CPU count
export WEB_CONCURRENCY=4

# Use 2 threads per worker
export THREADS=2

# Bind to specific host/port
export HOST=127.0.0.1
export PORT=3000
```

### Using the CLI
```bash
# Use gunicorn (default)
python -m open_webui serve

# Force uvicorn fallback
python -m open_webui serve --no-use-gunicorn
```

## Worker Lifecycle Management

The configuration includes automatic worker recycling to prevent memory leaks:
- Workers restart after processing 1000 requests (with ±50 jitter)
- Preload application for better memory efficiency
- Graceful shutdown with 120s timeout

## Environment-Specific Tuning

For memory-constrained environments, consider:
```bash
# Even more conservative (0.25 workers per core)
export WEB_CONCURRENCY=$(python3 -c "import multiprocessing; print(max(1, int(multiprocessing.cpu_count() * 0.25)))")
```

For high-performance environments:
```bash
# More workers but still conservative (0.75 workers per core)
export WEB_CONCURRENCY=$(python3 -c "import multiprocessing; print(max(2, int(multiprocessing.cpu_count() * 0.75)))")
export THREADS=2
```