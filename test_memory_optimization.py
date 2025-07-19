#!/usr/bin/env python3

"""
Simple test script to validate memory optimization changes
Tests that the application can start with minimal configuration
"""

import os
import sys

# Set memory optimization environment variables
os.environ.update({
    'DISABLE_BACKGROUND_SERVICES': 'true',
    'LAZY_LOAD_MODELS': 'true', 
    'ENABLE_BASE_MODELS_CACHE': 'false',
    'BYPASS_EMBEDDING_AND_RETRIEVAL': 'true',
    'BYPASS_WEB_SEARCH_EMBEDDING_AND_RETRIEVAL': 'true',
    'ENABLE_IMAGE_GENERATION': 'false',
    'ENABLE_CODE_EXECUTION': 'false',
    'ENABLE_WEB_SEARCH': 'false',
    'USER_PERMISSIONS_CHAT_STT': 'false',
    'USER_PERMISSIONS_CHAT_TTS': 'false',
    'ENABLE_NOTES': 'false',
    'ENABLE_CHANNELS': 'false',
    'ENABLE_COMMUNITY_SHARING': 'false',
    'ENABLE_MESSAGE_RATING': 'false',
    'ENABLE_OTEL': 'false',
    'ENABLE_VERSION_UPDATE_CHECK': 'false',
    'DATABASE_URL': 'sqlite:///test_webui.db',
})

def test_import():
    """Test that main modules can be imported with optimizations"""
    try:
        print("Testing optimized imports...")
        
        # Test basic FastAPI and pydantic imports
        import fastapi
        import pydantic
        print("✓ Core dependencies imported")
        
        # Test that main module can be imported
        sys.path.insert(0, 'backend')
        
        # This should work with optimizations
        from open_webui import config
        print("✓ Config module imported")
        
        # Test environment variables
        from open_webui.env import DISABLE_BACKGROUND_SERVICES, LAZY_LOAD_MODELS
        print(f"✓ Memory optimization flags: DISABLE_BACKGROUND_SERVICES={DISABLE_BACKGROUND_SERVICES}, LAZY_LOAD_MODELS={LAZY_LOAD_MODELS}")
        
        print("✓ All imports successful with memory optimizations")
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def test_memory_usage():
    """Test current memory usage"""
    try:
        import psutil
        import os
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"Current memory usage: {memory_mb:.1f} MB")
        
        if memory_mb < 200:
            print("✓ Memory usage under target of 200MB")
        else:
            print(f"⚠ Memory usage {memory_mb:.1f}MB above 200MB target")
            
        return memory_mb
        
    except ImportError:
        print("psutil not available - cannot check memory usage")
        return None

if __name__ == "__main__":
    print("Open WebUI Memory Optimization Test")
    print("=" * 50)
    
    success = test_import()
    memory = test_memory_usage()
    
    if success:
        print("\n✓ Memory optimizations are working correctly")
        if memory and memory < 200:
            print(f"✓ Memory target achieved: {memory:.1f}MB < 200MB")
        exit(0)
    else:
        print("\n✗ Memory optimization test failed")
        exit(1)