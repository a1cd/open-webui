"""
Optimized loading utility for lazy importing of heavy modules.

This module provides utilities to reduce memory usage at startup by only
importing modules when they are actually needed.
"""

import importlib
import logging
from functools import lru_cache
from typing import Any, Dict, Optional

log = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def get_module(module_name: str) -> Any:
    """
    Lazily import modules only when needed.
    
    Uses LRU cache to ensure modules are only imported once and then reused.
    
    Args:
        module_name (str): The name of the module to import
        
    Returns:
        Any: The imported module
        
    Example:
        # Instead of: from heavy_module import heavy_function
        # Use: heavy_function = get_module('heavy_module').heavy_function
    """
    try:
        log.debug(f"Lazy loading module: {module_name}")
        return importlib.import_module(module_name)
    except ImportError as e:
        log.error(f"Failed to import module '{module_name}': {e}")
        raise


@lru_cache(maxsize=None)
def get_module_attr(module_name: str, attr_name: str) -> Any:
    """
    Lazily import a specific attribute from a module.
    
    Args:
        module_name (str): The name of the module to import
        attr_name (str): The name of the attribute to get from the module
        
    Returns:
        Any: The requested attribute from the module
        
    Example:
        # Instead of: from heavy_module import heavy_function
        # Use: heavy_function = get_module_attr('heavy_module', 'heavy_function')
    """
    try:
        module = get_module(module_name)
        return getattr(module, attr_name)
    except AttributeError as e:
        log.error(f"Module '{module_name}' has no attribute '{attr_name}': {e}")
        raise


class LazyImport:
    """
    A lazy import wrapper that only imports modules when they are accessed.
    
    Example:
        # Instead of: import heavy_module
        # Use: heavy_module = LazyImport('heavy_module')
        
        # The module will only be imported when you access it:
        # result = heavy_module.some_function()
    """
    
    def __init__(self, module_name: str):
        self._module_name = module_name
        self._module: Optional[Any] = None
    
    def __getattr__(self, name: str) -> Any:
        if self._module is None:
            self._module = get_module(self._module_name)
        return getattr(self._module, name)
    
    def __call__(self, *args, **kwargs) -> Any:
        """Allow the lazy import to be called as a function if the module is callable."""
        if self._module is None:
            self._module = get_module(self._module_name)
        return self._module(*args, **kwargs)


class LazyAttribute:
    """
    A lazy attribute wrapper that only imports and accesses an attribute when needed.
    
    Example:
        # Instead of: from heavy_module import heavy_function
        # Use: heavy_function = LazyAttribute('heavy_module', 'heavy_function')
        
        # The module and attribute will only be loaded when called:
        # result = heavy_function(*args, **kwargs)
    """
    
    def __init__(self, module_name: str, attr_name: str):
        self._module_name = module_name
        self._attr_name = attr_name
        self._attr: Optional[Any] = None
    
    def __call__(self, *args, **kwargs) -> Any:
        if self._attr is None:
            self._attr = get_module_attr(self._module_name, self._attr_name)
        return self._attr(*args, **kwargs)
    
    def __getattr__(self, name: str) -> Any:
        if self._attr is None:
            self._attr = get_module_attr(self._module_name, self._attr_name)
        return getattr(self._attr, name)


def clear_module_cache() -> None:
    """
    Clear the module cache. Useful for testing or when you want to reload modules.
    """
    get_module.cache_clear()
    get_module_attr.cache_clear()
    log.debug("Module cache cleared")


def get_cached_modules() -> Dict[str, Any]:
    """
    Get information about currently cached modules.
    
    Returns:
        Dict[str, Any]: Information about cached modules including cache stats
    """
    return {
        "get_module_cache_info": get_module.cache_info(),
        "get_module_attr_cache_info": get_module_attr.cache_info(),
    }