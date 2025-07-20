# backend/gunicorn_conf.py
# Optimize the number of workers
import multiprocessing
import os

# Instead of default workers formula (2*CPU+1), use more conservative approach
workers_per_core = 0.5
default_web_concurrency = max(2, int(multiprocessing.cpu_count() * workers_per_core))
web_concurrency = int(os.getenv('WEB_CONCURRENCY', default_web_concurrency))

# Use the web_concurrency as the number of workers
workers = web_concurrency

# Threads per worker
threads = int(os.getenv('THREADS', '1'))

# Max requests before worker restart (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Worker class - use uvicorn workers for async support
worker_class = "uvicorn.workers.UvicornWorker"

# Bind configuration
host = os.getenv('HOST', '0.0.0.0')
port = os.getenv('PORT', '8080')
bind = f"{host}:{port}"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Graceful timeout
timeout = 120
keepalive = 5

# Preload the application for better memory usage
preload_app = True

# Worker processes will be restarted after they have processed this many requests
# This helps prevent memory leaks by recycling workers periodically
worker_connections = 1000

# Maximum number of simultaneous clients
max_worker_connections = 1000

# For development/debugging - can be overridden via environment variable
if os.getenv('GUNICORN_DEBUG', '').lower() == 'true':
    reload = True
    loglevel = "debug"