"""Unit tests for model classes."""

import pytest
from decimal import Decimal
from typing import Dict, Any

from houdiniswap.models import (
    Network,
    Token,
    DEXToken,
    RouteDTO,
    Quote,
    DEXQuote,
    ExchangeResponse,
    DexApproveResponse,
    Status,
    MinMax,
    Volume,
    WeeklyVolume,
    DEXTokensResponse,
    TransactionStatus,
)
from houdiniswap.exceptions import ValidationError


class TestNetwork:
    """Tests for Network model."""
    
    def test_from_dict_complete(self, sample_network_data):
        """Test creating Network from complete data."""
        network = Network.from_dict(sample_network_data)
        assert network.name == "Ethereum"
        assert network.short_name == "eth"
        assert network.address_validation == "^0x[a-fA-F0-9]{40}$"
        assert network.memo_needed is False
        assert network.explorer_url == "https://etherscan.io"
        assert network.chain_id == 1
    
    def test_from_dict_minimal(self):
        """Test creating Network from minimal data."""
        data = {
            "name": "Bitcoin",
            "shortName": "btc",
            "addressValidation": "^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$",
        }
        network = Network.from_dict(data)
        assert network.name == "Bitcoin"
        assert network.short_name == "btc"
        assert network.memo_needed is False
        assert network.explorer_url is None
    
    def test_from_dict_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        data = {"name": "Ethereum"}  # Missing shortName and addressValidation
        with pytest.raises(ValidationError, match="Missing required fields"):
            Network.from_dict(data)
    
    def test_from_dict_invalid_type(self):
        """Test that non-dict input raises ValidationError."""
        with pytest.raises(ValidationError, match="Expected dict"):
            Network.from_dict([])
    
    def test_repr(self, sample_network_data):
        """Test Network string representation."""
        network = Network.from_dict(sample_network_data)
        repr_str = repr(network)
        assert "Network" in repr_str
        assert "Ethereum" in repr_str
        assert "eth" in repr_str
    
    def test_frozen(self, sample_network_data):
        """Test that Network is immutable."""
        network = Network.from_dict(sample_network_data)
        with pytest.raises(Exception):  # dataclass frozen raises FrozenInstanceError
            network.name = "Modified"


class TestToken:
    """Tests for Token model."""
    
    def test_from_dict_complete(self, sample_token_data):
        """Test creating Token from complete data."""
        token = Token.from_dict(sample_token_data)
        assert token.id == "ETH"
        assert token.symbol == "ETH"
        assert token.name == "Ethereum"
        assert isinstance(token.network, Network)
        assert token.network.short_name == "eth"
        assert token.display_name == "Ethereum"
        assert token.has_markup is True
    
    def test_from_dict_minimal(self, sample_network_data):
        """Test creating Token from minimal data."""
        data = {
            "id": "BTC",
            "name": "Bitcoin",
            "symbol": "BTC",
            "network": sample_network_data,
        }
        token = Token.from_dict(data)
        assert token.id == "BTC"
        assert token.display_name is None
    
    def test_from_dict_missing_required_field(self, sample_network_data):
        """Test that missing required fields raise ValidationError."""
        data = {"id": "ETH", "network": sample_network_data}  # Missing name and symbol
        with pytest.raises(ValidationError, match="Missing required fields"):
            Token.from_dict(data)
    
    def test_from_dict_invalid_type(self):
        """Test that non-dict input raises ValidationError."""
        with pytest.raises(ValidationError, match="Expected dict"):
            Token.from_dict([])
    
    def test_from_dict_empty_network(self):
        """Test creating Token with empty network data."""
        data = {
            "id": "ETH",
            "name": "Ethereum",
            "symbol": "ETH",
            "network": {},
        }
        token = Token.from_dict(data)
        assert token.network.name == ""
        assert token.network.short_name == ""
    
    def test_repr(self, sample_token_data):
        """Test Token string representation."""
        token = Token.from_dict(sample_token_data)
        repr_str = repr(token)
        assert "Token" in repr_str
        assert "ETH" in repr_str
        assert "Ethereum" in repr_str


class TestDEXToken:
    """Tests for DEXToken model."""
    
    def test_from_dict_complete(self, sample_dex_token_data):
        """Test creating DEXToken from complete data."""
        token = DEXToken.from_dict(sample_dex_token_data)
        assert token.id == "6689b73ec90e45f3b3e51553"
        assert token.symbol == "USDC"
        assert token.name == "USD Coin"
        assert token.chain == "base"
        assert token.decimals == 18
        assert token.enabled is True
        assert token.has_dex is True
    
    def test_from_dict_minimal(self):
        """Test creating DEXToken from minimal data."""
        data = {
            "id": "token123",
            "address": "0x123",
            "chain": "ethereum",
            "decimals": 18,
            "symbol": "TKN",
            "name": "Token",
        }
        token = DEXToken.from_dict(data)
        assert token.id == "token123"
        assert token.created is None
        assert token.enabled is None
    
    def test_repr(self, sample_dex_token_data):
        """Test DEXToken string representation."""
        token = DEXToken.from_dict(sample_dex_token_data)
        repr_str = repr(token)
        assert "DEXToken" in repr_str
        assert "USDC" in repr_str
        assert "base" in repr_str


class TestRouteDTO:
    """Tests for RouteDTO model."""
    
    def test_from_dict(self, sample_route_data):
        """Test creating RouteDTO from dict."""
        route = RouteDTO.from_dict(sample_route_data)
        assert route.raw == sample_route_data
        assert route.raw["bridge"] == "stargate"
    
    def test_from_dict_invalid_type(self):
        """Test that non-dict input raises ValidationError."""
        with pytest.raises(ValidationError, match="Expected dict"):
            RouteDTO.from_dict([])
    
    def test_to_dict(self, sample_route_data):
        """Test converting RouteDTO back to dict."""
        route = RouteDTO.from_dict(sample_route_data)
        result = route.to_dict()
        assert result == sample_route_data
    
    def test_repr(self, sample_route_data):
        """Test RouteDTO string representation."""
        route = RouteDTO.from_dict(sample_route_data)
        repr_str = repr(route)
        assert "RouteDTO" in repr_str
        assert "stargate" in repr_str


class TestQuote:
    """Tests for Quote model."""
    
    def test_from_dict_complete(self, sample_quote_data):
        """Test creating Quote from complete data."""
        quote = Quote.from_dict(sample_quote_data)
        assert quote.amount_in == Decimal("1.0")
        assert quote.amount_out == Decimal("0.05")
        assert quote.min == Decimal("0.01")
        assert quote.max == Decimal("100.0")
        assert quote.use_xmr is False
        assert quote.duration == 30
        assert quote.client_id == "client123"
    
    def test_from_dict_minimal(self):
        """Test creating Quote from minimal data."""
        data = {
            "amountIn": "1.0",
            "amountOut": "0.05",
        }
        quote = Quote.from_dict(data)
        assert quote.amount_in == Decimal("1.0")
        assert quote.amount_out == Decimal("0.05")
        assert quote.min is None
        assert quote.max is None
    
    def test_from_dict_with_none_values(self):
        """Test Quote handles None values correctly."""
        data = {
            "amountIn": "1.0",
            "amountOut": "0.05",
            "min": None,
            "max": None,
        }
        quote = Quote.from_dict(data)
        assert quote.min is None
        assert quote.max is None
    
    def test_from_dict_invalid_type(self):
        """Test that non-dict input raises ValidationError."""
        with pytest.raises(ValidationError, match="Expected dict"):
            Quote.from_dict([])
    
    def test_repr(self, sample_quote_data):
        """Test Quote string representation."""
        quote = Quote.from_dict(sample_quote_data)
        repr_str = repr(quote)
        assert "Quote" in repr_str
        assert "1.0" in repr_str
        assert "0.05" in repr_str


class TestDEXQuote:
    """Tests for DEXQuote model."""
    
    def test_from_dict_complete(self, sample_dex_quote_data):
        """Test creating DEXQuote from complete data."""
        quote = DEXQuote.from_dict(sample_dex_quote_data)
        assert quote.swap == "sw"
        assert quote.quote_id == "quote_12345"
        assert quote.amount_out == Decimal("0.05")
        assert quote.amount_out_usd == Decimal("50.0")
        assert quote.duration == 300
        assert quote.gas == 21000
        assert quote.fee_usd == Decimal("0.5")
        assert quote.path == ["token1", "token2", "token3"]
    
    def test_from_dict_minimal(self):
        """Test creating DEXQuote from minimal data."""
        data = {
            "swap": "sw",
            "quoteId": "quote123",
            "amountOut": "0.05",
        }
        quote = DEXQuote.from_dict(data)
        assert quote.swap == "sw"
        assert quote.amount_out_usd is None
        assert quote.path is None
    
    def test_repr(self, sample_dex_quote_data):
        """Test DEXQuote string representation."""
        quote = DEXQuote.from_dict(sample_dex_quote_data)
        repr_str = repr(quote)
        assert "DEXQuote" in repr_str
        assert "quote_12345" in repr_str


class TestExchangeResponse:
    """Tests for ExchangeResponse model."""
    
    def test_from_dict_complete(self, sample_exchange_response_data):
        """Test creating ExchangeResponse from complete data."""
        response = ExchangeResponse.from_dict(sample_exchange_response_data)
        assert response.houdini_id == "h9NpKm75gRnX7GWaFATwYn"
        assert response.status == 0
        assert response.in_amount == Decimal("1.0")
        assert response.out_amount == Decimal("0.05")
        assert response.in_symbol == "ETH"
        assert response.out_symbol == "BNB"
        assert response.anonymous is False
        assert isinstance(response.quote, Quote)
        assert isinstance(response.in_token, Token)
    
    def test_from_dict_minimal(self):
        """Test creating ExchangeResponse from minimal data."""
        data = {
            "houdiniId": "test123",
            "status": 0,
        }
        response = ExchangeResponse.from_dict(data)
        assert response.houdini_id == "test123"
        assert response.status == 0
        assert response.quote is None
        assert response.in_token is None
    
    def test_from_dict_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        data = {"status": 0}  # Missing houdiniId
        with pytest.raises(ValidationError, match="Missing required fields"):
            ExchangeResponse.from_dict(data)
    
    def test_from_dict_invalid_type(self):
        """Test that non-dict input raises ValidationError."""
        with pytest.raises(ValidationError, match="Expected dict"):
            ExchangeResponse.from_dict([])
    
    def test_repr(self, sample_exchange_response_data):
        """Test ExchangeResponse string representation."""
        response = ExchangeResponse.from_dict(sample_exchange_response_data)
        repr_str = repr(response)
        assert "ExchangeResponse" in repr_str
        assert "h9NpKm75gRnX7GWaFATwYn" in repr_str


class TestDexApproveResponse:
    """Tests for DexApproveResponse model."""
    
    def test_from_dict_complete(self, sample_dex_approve_response_data):
        """Test creating DexApproveResponse from complete data."""
        response = DexApproveResponse.from_dict(sample_dex_approve_response_data)
        assert response.data == "0x1234567890abcdef"
        assert response.to == "0xcontract123456789012345678901234567890"
        assert response.from_address == "0x1111111111111111111111111111111111111111"
        assert response.from_chain is not None
        assert response.from_chain["chainId"] == 8453
    
    def test_from_dict_minimal(self):
        """Test creating DexApproveResponse from minimal data."""
        data = {
            "data": "0x123",
            "to": "0xto",
            "from": "0xfrom",
        }
        response = DexApproveResponse.from_dict(data)
        assert response.data == "0x123"
        assert response.from_chain is None
    
    def test_from_dict_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        data = {"data": "0x123"}  # Missing to and from
        with pytest.raises(ValidationError, match="Missing required fields"):
            DexApproveResponse.from_dict(data)
    
    def test_from_dict_invalid_type(self):
        """Test that non-dict input raises ValidationError."""
        with pytest.raises(ValidationError, match="Expected dict"):
            DexApproveResponse.from_dict([])
    
    def test_repr(self, sample_dex_approve_response_data):
        """Test DexApproveResponse string representation."""
        response = DexApproveResponse.from_dict(sample_dex_approve_response_data)
        repr_str = repr(response)
        assert "DexApproveResponse" in repr_str


class TestStatus:
    """Tests for Status model."""
    
    def test_from_dict_complete(self, sample_status_data):
        """Test creating Status from complete data."""
        status = Status.from_dict(sample_status_data)
        assert status.houdini_id == "h9NpKm75gRnX7GWaFATwYn"
        assert status.status == TransactionStatus.FINISHED
        assert status.in_amount == 1.0
        assert status.out_amount == 0.05
        assert status.in_symbol == "ETH"
        assert status.out_symbol == "BNB"
    
    def test_from_dict_minimal(self):
        """Test creating Status from minimal data."""
        data = {
            "houdiniId": "test123",
            "status": 0,  # WAITING
        }
        status = Status.from_dict(data)
        assert status.houdini_id == "test123"
        assert status.status == TransactionStatus.WAITING
        assert status.in_amount is None
    
    def test_from_dict_all_status_codes(self):
        """Test all transaction status codes."""
        status_codes = {
            -1: TransactionStatus.NEW,
            0: TransactionStatus.WAITING,
            1: TransactionStatus.CONFIRMING,
            2: TransactionStatus.EXCHANGING,
            3: TransactionStatus.ANONYMIZING,
            4: TransactionStatus.FINISHED,
            5: TransactionStatus.EXPIRED,
            6: TransactionStatus.FAILED,
            7: TransactionStatus.REFUNDED,
            8: TransactionStatus.DELETED,
        }
        for code, expected_status in status_codes.items():
            data = {"houdiniId": "test", "status": code}
            status = Status.from_dict(data)
            assert status.status == expected_status
    
    def test_from_dict_invalid_status_code(self):
        """Test that invalid status code raises ValidationError."""
        data = {"houdiniId": "test", "status": 999}
        with pytest.raises(ValidationError, match="Invalid transaction status code"):
            Status.from_dict(data)
    
    def test_from_dict_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        data = {"status": 0}  # Missing houdiniId
        with pytest.raises(ValidationError, match="Missing required fields"):
            Status.from_dict(data)
    
    def test_from_dict_invalid_type(self):
        """Test that non-dict input raises ValidationError."""
        with pytest.raises(ValidationError, match="Expected dict"):
            Status.from_dict([])
    
    def test_repr(self, sample_status_data):
        """Test Status string representation."""
        status = Status.from_dict(sample_status_data)
        repr_str = repr(status)
        assert "Status" in repr_str
        assert "FINISHED" in repr_str


class TestMinMax:
    """Tests for MinMax model."""
    
    def test_from_list(self, sample_min_max_data):
        """Test creating MinMax from list."""
        min_max = MinMax.from_list(sample_min_max_data)
        assert min_max.min == Decimal("0.01")
        assert min_max.max == Decimal("100.0")
    
    def test_from_list_with_strings(self):
        """Test MinMax with string values."""
        data = ["0.01", "100.0"]
        min_max = MinMax.from_list(data)
        assert min_max.min == Decimal("0.01")
        assert min_max.max == Decimal("100.0")
    
    def test_from_list_with_floats(self):
        """Test MinMax with float values."""
        data = [0.01, 100.0]
        min_max = MinMax.from_list(data)
        assert min_max.min == Decimal("0.01")
        assert min_max.max == Decimal("100.0")
    
    def test_from_list_insufficient_elements(self):
        """Test that insufficient elements raise ValueError."""
        with pytest.raises(ValueError, match="requires at least 2 elements"):
            MinMax.from_list([0.01])
    
    def test_repr(self, sample_min_max_data):
        """Test MinMax string representation."""
        min_max = MinMax.from_list(sample_min_max_data)
        repr_str = repr(min_max)
        assert "MinMax" in repr_str
        assert "0.01" in repr_str
        assert "100.0" in repr_str


class TestVolume:
    """Tests for Volume model."""
    
    def test_from_dict(self, sample_volume_data):
        """Test creating Volume from dict."""
        volume = Volume.from_dict(sample_volume_data)
        assert volume.count == 1000
        assert volume.total_transacted_usd == Decimal("1000000.50")
    
    def test_from_dict_minimal(self):
        """Test creating Volume from minimal data."""
        data = {}
        volume = Volume.from_dict(data)
        assert volume.count == 0
        assert volume.total_transacted_usd == Decimal("0")
    
    def test_repr(self, sample_volume_data):
        """Test Volume string representation."""
        volume = Volume.from_dict(sample_volume_data)
        repr_str = repr(volume)
        assert "Volume" in repr_str
        assert "1000" in repr_str


class TestWeeklyVolume:
    """Tests for WeeklyVolume model."""
    
    def test_from_dict(self, sample_weekly_volume_data):
        """Test creating WeeklyVolume from dict."""
        volume = WeeklyVolume.from_dict(sample_weekly_volume_data)
        assert volume.count == 100
        assert volume.anonymous == 20
        assert volume.volume == Decimal("50000.25")
        assert volume.week == 1
        assert volume.year == 2024
        assert volume.commission == Decimal("500.00")
    
    def test_from_dict_minimal(self):
        """Test creating WeeklyVolume from minimal data."""
        data = {}
        volume = WeeklyVolume.from_dict(data)
        assert volume.count == 0
        assert volume.volume == Decimal("0")
        assert volume.commission == Decimal("0")
    
    def test_repr(self, sample_weekly_volume_data):
        """Test WeeklyVolume string representation."""
        volume = WeeklyVolume.from_dict(sample_weekly_volume_data)
        repr_str = repr(volume)
        assert "WeeklyVolume" in repr_str
        assert "1" in repr_str
        assert "2024" in repr_str


class TestDEXTokensResponse:
    """Tests for DEXTokensResponse model."""
    
    def test_creation(self, sample_dex_token_data):
        """Test creating DEXTokensResponse."""
        tokens = [DEXToken.from_dict(sample_dex_token_data)]
        response = DEXTokensResponse(count=1, tokens=tokens)
        assert response.count == 1
        assert len(response.tokens) == 1
        assert response.tokens[0].symbol == "USDC"
    
    def test_repr(self, sample_dex_token_data):
        """Test DEXTokensResponse string representation."""
        tokens = [DEXToken.from_dict(sample_dex_token_data)]
        response = DEXTokensResponse(count=1, tokens=tokens)
        repr_str = repr(response)
        assert "DEXTokensResponse" in repr_str
        assert "1" in repr_str
