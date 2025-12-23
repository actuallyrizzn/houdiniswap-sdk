"""
Houdini Swap Python SDK

A comprehensive Python SDK for interacting with the Houdini Swap API.
"""

from .client import HoudiniSwapClient
from .models import (
    Token,
    DEXToken,
    DEXTokensResponse,
    Network,
    Quote,
    DEXQuote,
    ExchangeResponse,
    DexApproveResponse,
    Status,
    Volume,
    WeeklyVolume,
    MinMax,
    TransactionStatus,
    RouteDTO,
)
from .exceptions import (
    HoudiniSwapError,
    AuthenticationError,
    APIError,
    ValidationError,
    NetworkError,
)

__version__ = "0.1.0"

# Version info tuple for structured access (major, minor, patch)
def _parse_version(version_str: str) -> tuple:
    """Parse version string into tuple."""
    parts = version_str.split('.')
    return tuple(int(part) for part in parts[:3])

__version_info__ = _parse_version(__version__)

def get_version() -> str:
    """Get the SDK version string."""
    return __version__

def get_version_info() -> tuple:
    """Get the SDK version as a tuple (major, minor, patch)."""
    return __version_info__

def compare_version(other_version: str) -> int:
    """
    Compare this SDK version with another version string.
    
    Args:
        other_version: Version string to compare (e.g., "0.1.0")
        
    Returns:
        -1 if this version is older, 0 if equal, 1 if newer
    """
    try:
        other_info = _parse_version(other_version)
        this_info = __version_info__
        if this_info < other_info:
            return -1
        elif this_info > other_info:
            return 1
        else:
            return 0
    except (ValueError, AttributeError):
        raise ValueError(f"Invalid version format: {other_version}")

def is_compatible_with(min_version: str) -> bool:
    """
    Check if current SDK version is compatible with minimum required version.
    
    Args:
        min_version: Minimum required version string (e.g., "0.1.0")
        
    Returns:
        True if current version >= min_version, False otherwise
    """
    return compare_version(min_version) >= 0

__all__ = [
    "HoudiniSwapClient",
    "Token",
    "DEXToken",
    "DEXTokensResponse",
    "Network",
    "Quote",
    "DEXQuote",
    "ExchangeResponse",
    "DexApproveResponse",
    "Status",
    "Volume",
    "WeeklyVolume",
    "MinMax",
    "TransactionStatus",
    "RouteDTO",
    "HoudiniSwapError",
    "AuthenticationError",
    "APIError",
    "ValidationError",
    "NetworkError",
]

