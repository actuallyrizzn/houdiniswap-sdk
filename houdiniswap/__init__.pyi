"""Type stubs for houdiniswap package."""

from typing import Any
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
from .utils import deprecated, deprecated_parameter

__version__: str
__version_info__: tuple[int, int, int]

def get_version() -> str: ...
def get_version_info() -> tuple[int, int, int]: ...
def compare_version(other_version: str) -> int: ...
def is_compatible_with(min_version: str) -> bool: ...

__all__: list[str]

