"""Utility functions for the Houdini Swap SDK."""

import warnings
from typing import Callable, Any, Optional
from functools import wraps


def deprecated(
    reason: Optional[str] = None,
    version: Optional[str] = None,
    replacement: Optional[str] = None,
    removal_version: Optional[str] = None,
) -> Callable:
    """
    Mark a function or method as deprecated.
    
    Args:
        reason: Reason for deprecation
        version: Version when the function was deprecated
        replacement: Name of replacement function/method
        removal_version: Version when the function will be removed
        
    Returns:
        Decorator function
        
    Example:
        ```python
        @deprecated(reason="Use new_method() instead", version="0.2.0", replacement="new_method")
        def old_method(self):
            pass
        ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            message_parts = [f"{func.__name__} is deprecated"]
            
            if version:
                message_parts.append(f"(deprecated in version {version})")
            
            if reason:
                message_parts.append(f": {reason}")
            
            if replacement:
                message_parts.append(f". Use {replacement} instead.")
            
            if removal_version:
                message_parts.append(f" It will be removed in version {removal_version}.")
            
            message = " ".join(message_parts)
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def deprecated_parameter(
    param_name: str,
    reason: Optional[str] = None,
    version: Optional[str] = None,
    replacement: Optional[str] = None,
    removal_version: Optional[str] = None,
) -> Callable:
    """
    Mark a parameter as deprecated.
    
    Args:
        param_name: Name of the deprecated parameter
        reason: Reason for deprecation
        version: Version when the parameter was deprecated
        replacement: Name of replacement parameter
        removal_version: Version when the parameter will be removed
        
    Returns:
        Decorator function
        
    Example:
        ```python
        @deprecated_parameter("old_param", replacement="new_param", version="0.2.0")
        def my_function(new_param=None, old_param=None):
            if old_param is not None:
                # Handle deprecated parameter
                pass
        ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if param_name in kwargs and kwargs[param_name] is not None:
                message_parts = [f"Parameter '{param_name}' is deprecated"]
                
                if version:
                    message_parts.append(f"(deprecated in version {version})")
                
                if reason:
                    message_parts.append(f": {reason}")
                
                if replacement:
                    message_parts.append(f". Use '{replacement}' instead.")
                
                if removal_version:
                    message_parts.append(f" It will be removed in version {removal_version}.")
                
                message = " ".join(message_parts)
                warnings.warn(message, DeprecationWarning, stacklevel=2)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

