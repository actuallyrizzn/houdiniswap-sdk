"""Pytest configuration and shared fixtures."""

import pytest
import os
from unittest.mock import Mock, MagicMock
from typing import Dict, Any
from decimal import Decimal

from houdiniswap import HoudiniSwapClient
from houdiniswap.models import (
    Token,
    DEXToken,
    Network,
    Quote,
    DEXQuote,
    ExchangeResponse,
    DexApproveResponse,
    Status,
    MinMax,
    Volume,
    WeeklyVolume,
    TransactionStatus,
    RouteDTO,
    DEXTokensResponse,
)


@pytest.fixture
def api_key():
    """Sample API key for testing."""
    return "test_api_key_12345"


@pytest.fixture
def api_secret():
    """Sample API secret for testing."""
    return "test_api_secret_67890"


@pytest.fixture
def client(api_key, api_secret):
    """Create a HoudiniSwapClient instance for testing."""
    return HoudiniSwapClient(
        api_key=api_key,
        api_secret=api_secret,
        base_url="https://test-api.houdiniswap.com",
        timeout=5,
        max_retries=1,  # Faster tests
        cache_enabled=False,  # Disable caching for most tests
    )


@pytest.fixture
def mock_session():
    """Create a mock requests.Session."""
    session = MagicMock()
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {}
    response.text = "{}"
    session.request.return_value = response
    return session


@pytest.fixture
def sample_network_data():
    """Sample network data from API."""
    return {
        "name": "Ethereum",
        "shortName": "eth",
        "addressValidation": "^0x[a-fA-F0-9]{40}$",
        "memoNeeded": False,
        "explorerUrl": "https://etherscan.io",
        "addressUrl": "https://etherscan.io/address/{}",
        "priority": 1,
        "kind": "evm",
        "chainId": 1,
        "icon": "https://example.com/eth.png",
    }


@pytest.fixture
def sample_token_data(sample_network_data):
    """Sample token data from API."""
    return {
        "id": "ETH",
        "name": "Ethereum",
        "symbol": "ETH",
        "network": sample_network_data,
        "displayName": "Ethereum",
        "icon": "https://example.com/eth.png",
        "keyword": "ethereum",
        "color": "#627EEA",
        "chain": 1,
        "address": "0x0000000000000000000000000000000000000000",
        "hasMarkup": True,
        "networkPriority": 1,
        "hasFixed": False,
        "hasFixedReverse": False,
    }


@pytest.fixture
def sample_dex_token_data():
    """Sample DEX token data from API."""
    return {
        "id": "6689b73ec90e45f3b3e51553",
        "address": "0x1234567890123456789012345678901234567890",
        "chain": "base",
        "decimals": 18,
        "symbol": "USDC",
        "name": "USD Coin",
        "created": "2024-01-01T00:00:00Z",
        "modified": "2024-01-01T00:00:00Z",
        "enabled": True,
        "hasDex": True,
    }


@pytest.fixture
def sample_quote_data():
    """Sample quote data from API."""
    return {
        "amountIn": "1.0",
        "amountOut": "0.05",
        "min": "0.01",
        "max": "100.0",
        "useXmr": False,
        "duration": 30,
        "deviceInfo": "web",
        "isMobile": False,
        "clientId": "client123",
    }


@pytest.fixture
def sample_dex_quote_data():
    """Sample DEX quote data from API."""
    return {
        "swap": "sw",
        "quoteId": "quote_12345",
        "amountOut": "0.05",
        "amountOutUsd": "50.0",
        "duration": 300,
        "gas": 21000,
        "feeUsd": "0.5",
        "path": ["token1", "token2", "token3"],
        "raw": {"bridge": "stargate"},
    }


@pytest.fixture
def sample_exchange_response_data(sample_token_data, sample_quote_data):
    """Sample exchange response data from API."""
    return {
        "houdiniId": "h9NpKm75gRnX7GWaFATwYn",
        "created": "2024-01-01T00:00:00Z",
        "senderAddress": "0x1111111111111111111111111111111111111111",
        "receiverAddress": "0x2222222222222222222222222222222222222222",
        "anonymous": False,
        "expires": "2024-01-01T01:00:00Z",
        "status": 0,
        "inAmount": "1.0",
        "inSymbol": "ETH",
        "outAmount": "0.05",
        "outSymbol": "BNB",
        "senderTag": None,
        "receiverTag": None,
        "notified": False,
        "eta": 1800,
        "inAmountUsd": "2500.0",
        "inCreated": "2024-01-01T00:00:00Z",
        "quote": sample_quote_data,
        "outToken": sample_token_data,
        "inToken": sample_token_data,
        "metadata": {},
        "isDex": False,
    }


@pytest.fixture
def sample_status_data():
    """Sample status data from API."""
    return {
        "houdiniId": "h9NpKm75gRnX7GWaFATwYn",
        "status": 4,  # FINISHED
        "created": "2024-01-01T00:00:00Z",
        "senderAddress": "0x1111111111111111111111111111111111111111",
        "receiverAddress": "0x2222222222222222222222222222222222222222",
        "anonymous": False,
        "expires": "2024-01-01T01:00:00Z",
        "inAmount": 1.0,
        "inSymbol": "ETH",
        "outAmount": 0.05,
        "outSymbol": "BNB",
        "eta": 1800,
    }


@pytest.fixture
def sample_route_data():
    """Sample route data for DEX transactions."""
    return {
        "bridge": "stargate",
        "fromChain": "base",
        "toChain": "ethereum",
        "fee": "0.001",
        "slippage": "0.5",
    }


@pytest.fixture
def sample_dex_approve_response_data():
    """Sample DEX approve response data."""
    return {
        "data": "0x1234567890abcdef",
        "to": "0xcontract123456789012345678901234567890",
        "from": "0x1111111111111111111111111111111111111111",
        "fromChain": {"chainId": 8453, "name": "Base"},
    }


@pytest.fixture
def sample_volume_data():
    """Sample volume data from API."""
    return {
        "count": 1000,
        "totalTransactedUSD": "1000000.50",
    }


@pytest.fixture
def sample_weekly_volume_data():
    """Sample weekly volume data from API."""
    return {
        "count": 100,
        "anonymous": 20,
        "volume": "50000.25",
        "week": 1,
        "year": 2024,
        "commission": "500.00",
    }


@pytest.fixture
def sample_min_max_data():
    """Sample min-max data from API (as array)."""
    return [0.01, 100.0]


@pytest.fixture
def sample_dex_tokens_response_data(sample_dex_token_data):
    """Sample DEX tokens response data."""
    return {
        "count": 1,
        "tokens": [sample_dex_token_data],
    }
