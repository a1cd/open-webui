# Memory Optimization Guide for Open WebUI

This guide provides comprehensive instructions for reducing Open WebUI's memory usage from the default ~500MB to under 200MB, making it suitable for resource-constrained environments.

## Quick Start - Memory Optimized Mode

### Option 1: Using the provided script
```bash
./run-memory-optimized.sh
```

### Option 2: Using environment variables
```bash
# Load memory optimization settings
export $(grep -v '^#' memory-optimized.env | xargs)

# Start the backend
cd backend
python -m uvicorn open_webui.main:app --host 0.0.0.0 --port 8080 --workers 1
```

### Option 3: Using Docker Compose
```bash
docker-compose -f docker-compose.memory-optimized.yaml up
```

## Memory Optimization Strategies

### 1. Core Memory Optimizations

#### Lazy Loading (Enabled by default)
- **LAZY_LOAD_MODELS=true**: Models are loaded only when first accessed
- **DISABLE_BACKGROUND_SERVICES=true**: Disables periodic cleanup and maintenance tasks
- **ENABLE_BASE_MODELS_CACHE=false**: Prevents eager loading of model lists at startup

#### Conditional Component Loading
Heavy components (audio, image processing, retrieval) are only imported when needed:
- Audio processing router: Only loaded if background services are enabled
- Image generation router: Only loaded if background services are enabled  
- Retrieval router: Only loaded if embedding/retrieval is not bypassed

### 2. Feature Disabling

#### Heavy Feature Bypassing
```bash
# Disable the most memory-intensive features
BYPASS_EMBEDDING_AND_RETRIEVAL=true
BYPASS_WEB_SEARCH_EMBEDDING_AND_RETRIEVAL=true

# Disable optional heavy components
ENABLE_IMAGE_GENERATION=false
ENABLE_CODE_EXECUTION=false
ENABLE_WEB_SEARCH=false
```

#### Audio/Video Processing
```bash
# Disable audio features if not needed
USER_PERMISSIONS_CHAT_STT=false
USER_PERMISSIONS_CHAT_TTS=false
```

#### Non-Essential Features
```bash
# Disable social and collaborative features
ENABLE_NOTES=false
ENABLE_CHANNELS=false
ENABLE_COMMUNITY_SHARING=false
ENABLE_MESSAGE_RATING=false
```

### 3. Database Optimizations

#### Use Lightweight Database
```bash
# Use SQLite instead of PostgreSQL for minimal setups
DATABASE_URL=sqlite:///data/webui.db

# If using vector database, use Chroma (lightweight)
VECTOR_DB=chroma
```

### 4. Resource Limits

#### Conservative Processing Limits
```bash
# Reduce text processing chunk sizes
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Limit retrieval results
RAG_TOP_K=3

# Limit file upload size/count
RAG_FILE_MAX_SIZE=2097152  # 2MB
RAG_FILE_MAX_COUNT=5
```

#### Disable Telemetry and Monitoring
```bash
ENABLE_OTEL=false
ENABLE_VERSION_UPDATE_CHECK=false
```

## Memory Usage Comparison

| Configuration | Estimated RAM Usage | Features Available |
|---------------|-------------------|-------------------|
| Default | ~500MB | All features enabled |
| Minimal (this guide) | <200MB | Core chat functionality |
| Ultra-minimal | <128MB | Basic chat only, no file uploads |

## Implementation Details

### Lazy Loading Mechanism

The optimization introduces lazy loading for the heaviest components:

1. **Embedding Functions**: Only loaded when first RAG/retrieval operation is requested
2. **Vector Database Clients**: Instantiated on first use rather than at startup
3. **Heavy Router Imports**: Audio, image, and retrieval routers are conditionally imported

### Code Changes Summary

- **main.py**: Added lazy initialization functions and conditional router inclusion
- **env.py**: Added memory optimization environment variables
- **memories.py**: Updated to use lazy embedding function initialization
- **retrieval/vector/factory.py**: Added lazy loading for vector database clients

### Backwards Compatibility

All optimizations are backwards compatible:
- Default behavior remains unchanged when optimization flags are not set
- Existing installations continue to work without modification
- Progressive optimization allows enabling features as needed

## Advanced Configuration

### Ultra-Minimal Mode (targeting <128MB)
```bash
# In addition to the above, also disable:
ENABLE_OAUTH_SIGNUP=false
ENABLE_LOGIN_FORM=false
WEBUI_AUTH=false
ENABLE_API_KEY=false

# Use minimal middleware
ENABLE_COMPRESSION_MIDDLEWARE=false

# Disable all optional routers
# (This would require additional code modifications)
```

### Docker Memory Limits
```yaml
deploy:
  resources:
    limits:
      memory: 256M
    reservations:
      memory: 128M
```

## Monitoring Memory Usage

### Check Current Usage
```bash
# During runtime, check memory usage
ps aux | grep uvicorn
# or with docker
docker stats open-webui-minimal
```

### Python Memory Profiling
```python
import psutil
import os
process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

## Troubleshooting

### Common Issues

1. **Features not working**: Check if related environment variables are properly set
2. **Import errors**: Ensure dependencies are installed for enabled features
3. **Performance issues**: Some operations may be slower due to lazy loading

### Re-enabling Features

To re-enable specific features, set the corresponding environment variables:
```bash
# Re-enable image generation
ENABLE_IMAGE_GENERATION=true

# Re-enable retrieval/RAG
BYPASS_EMBEDDING_AND_RETRIEVAL=false

# Re-enable background services  
DISABLE_BACKGROUND_SERVICES=false
```

## Contributing

When adding new features, please consider:
- Making heavy imports conditional
- Adding environment variables for optional components
- Documenting memory impact of new features
- Testing with memory optimization flags enabled

## Performance Notes

- First-time feature access may be slower due to lazy loading
- Subsequent operations should perform normally
- Overall responsiveness improves due to reduced memory pressure
- Some advanced features may be unavailable in minimal mode

This optimization makes Open WebUI suitable for:
- Raspberry Pi and similar single-board computers
- Docker containers with memory limits
- Shared hosting environments
- Development and testing with limited resources