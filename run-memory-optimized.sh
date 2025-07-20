#!/bin/bash

# Open WebUI Memory-Optimized Startup Script
# This script starts Open WebUI with optimizations to reduce memory usage

echo "Starting Open WebUI in memory-optimized mode..."
echo "Target: Optimize memory usage for resource-constrained environments"

# Load memory optimization environment variables
if [ -f "memory-optimized.env" ]; then
    echo "Loading memory optimization configuration..."
    export $(grep -v '^#' memory-optimized.env | xargs)
else
    echo "Warning: memory-optimized.env not found, using default minimal settings"
    
    # Core memory optimizations
    export DISABLE_BACKGROUND_SERVICES=true
    export LAZY_LOAD_MODELS=true
    export ENABLE_BASE_MODELS_CACHE=false
    
    # Disable heavy features
    export BYPASS_EMBEDDING_AND_RETRIEVAL=true
    export BYPASS_WEB_SEARCH_EMBEDDING_AND_RETRIEVAL=true
    
    # Disable optional components
    export ENABLE_IMAGE_GENERATION=false
    export ENABLE_CODE_EXECUTION=false
    export ENABLE_WEB_SEARCH=false
    
    # Minimal permissions
    export USER_PERMISSIONS_CHAT_STT=false
    export USER_PERMISSIONS_CHAT_TTS=false
    
    # Disable non-essential features
    export ENABLE_NOTES=false
    export ENABLE_CHANNELS=false
    export ENABLE_COMMUNITY_SHARING=false
    export ENABLE_MESSAGE_RATING=false
    
    # Disable telemetry
    export ENABLE_OTEL=false
    export ENABLE_VERSION_UPDATE_CHECK=false
    
    # Use lightweight database
    export DATABASE_URL=sqlite:///data/webui.db
fi

echo "Memory optimization settings applied:"
echo "- Background services: $([ "$DISABLE_BACKGROUND_SERVICES" = "true" ] && echo "DISABLED" || echo "enabled")"
echo "- Model caching: $([ "$ENABLE_BASE_MODELS_CACHE" = "false" ] && echo "DISABLED" || echo "enabled")"
echo "- Embedding/Retrieval: $([ "$BYPASS_EMBEDDING_AND_RETRIEVAL" = "true" ] && echo "BYPASSED" || echo "enabled")"
echo "- Image generation: $([ "$ENABLE_IMAGE_GENERATION" = "false" ] && echo "DISABLED" || echo "enabled")"
echo "- Web search: $([ "$ENABLE_WEB_SEARCH" = "false" ] && echo "DISABLED" || echo "enabled")"

echo ""
echo "Starting Open WebUI backend..."

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install minimal requirements if needed
if ! pip show fastapi > /dev/null 2>&1; then
    echo "Installing minimal requirements..."
    pip install fastapi uvicorn pydantic python-multipart sqlalchemy alembic
fi

# Start the backend with memory optimizations
echo "Starting server with minimal resource usage..."
python -m uvicorn open_webui.main:app --host 0.0.0.0 --port 8080 --workers 1

echo "Open WebUI started in memory-optimized mode!"
echo "Visit http://localhost:8080 to access the interface"