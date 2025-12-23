"""Unit tests for ExchangeBuilder."""

import pytest
from unittest.mock import MagicMock

from houdiniswap.builder import ExchangeBuilder
from houdiniswap.exceptions import ValidationError
from houdiniswap.models import RouteDTO


class TestExchangeBuilder:
    """Tests for ExchangeBuilder class."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock client."""
        client = MagicMock()
        client._sanitize_input = lambda x, y: x.strip() if isinstance(x, str) else x
        return client
    
    @pytest.fixture
    def builder(self, mock_client):
        """Create an ExchangeBuilder instance."""
        return ExchangeBuilder(mock_client)
    
    def test_init(self, builder, mock_client):
        """Test builder initialization."""
        assert builder.client == mock_client
        assert builder._exchange_type is None
        assert builder._amount is None
    
    def test_cex(self, builder):
        """Test setting exchange type to CEX."""
        result = builder.cex()
        assert result is builder  # Fluent interface
        assert builder._exchange_type == "cex"
    
    def test_dex(self, builder):
        """Test setting exchange type to DEX."""
        result = builder.dex()
        assert result is builder
        assert builder._exchange_type == "dex"
    
    def test_amount_valid(self, builder):
        """Test setting valid amount."""
        result = builder.amount(1.5)
        assert result is builder
        assert builder._amount == 1.5
    
    def test_amount_zero_raises(self, builder):
        """Test that zero amount raises ValidationError."""
        with pytest.raises(ValidationError, match="must be greater than 0"):
            builder.amount(0)
    
    def test_amount_negative_raises(self, builder):
        """Test that negative amount raises ValidationError."""
        with pytest.raises(ValidationError, match="must be greater than 0"):
            builder.amount(-1)
    
    def test_from_token(self, builder):
        """Test setting from token."""
        result = builder.from_token("ETH")
        assert result is builder
        assert builder._from_token == "ETH"
    
    def test_to_token(self, builder):
        """Test setting to token."""
        result = builder.to_token("BNB")
        assert result is builder
        assert builder._to_token == "BNB"
    
    def test_address_to(self, builder):
        """Test setting destination address."""
        result = builder.address_to("0x123")
        assert result is builder
        assert builder._address_to == "0x123"
    
    def test_address_from(self, builder):
        """Test setting source address."""
        result = builder.address_from("0x456")
        assert result is builder
        assert builder._address_from == "0x456"
    
    def test_anonymous(self, builder):
        """Test setting anonymous flag."""
        result = builder.anonymous(True)
        assert result is builder
        assert builder._anonymous is True
        
        builder.anonymous(False)
        assert builder._anonymous is False
    
    def test_receiver_tag(self, builder):
        """Test setting receiver tag."""
        result = builder.receiver_tag("tag123")
        assert result is builder
        assert builder._receiver_tag == "tag123"
    
    def test_wallet_id(self, builder):
        """Test setting wallet ID."""
        result = builder.wallet_id("wallet123")
        assert result is builder
        assert builder._wallet_id == "wallet123"
    
    def test_ip(self, builder):
        """Test setting IP address."""
        result = builder.ip("192.168.1.1")
        assert result is builder
        assert builder._ip == "192.168.1.1"
    
    def test_user_agent(self, builder):
        """Test setting user agent."""
        result = builder.user_agent("Mozilla/5.0")
        assert result is builder
        assert builder._user_agent == "Mozilla/5.0"
    
    def test_timezone(self, builder):
        """Test setting timezone."""
        result = builder.timezone("UTC")
        assert result is builder
        assert builder._timezone == "UTC"
    
    def test_use_xmr(self, builder):
        """Test setting use XMR flag."""
        result = builder.use_xmr(True)
        assert result is builder
        assert builder._use_xmr is True
    
    def test_swap(self, builder):
        """Test setting swap identifier."""
        result = builder.swap("sw")
        assert result is builder
        assert builder._swap == "sw"
    
    def test_quote_id(self, builder):
        """Test setting quote ID."""
        result = builder.quote_id("quote123")
        assert result is builder
        assert builder._quote_id == "quote123"
    
    def test_route(self, builder, sample_route_data):
        """Test setting route."""
        route = RouteDTO.from_dict(sample_route_data)
        result = builder.route(route)
        assert result is builder
        assert builder._route is route
    
    def test_route_invalid_type_raises(self, builder):
        """Test that non-RouteDTO route raises ValidationError."""
        with pytest.raises(ValidationError, match="RouteDTO instance"):
            builder.route({"invalid": "route"})
    
    def test_validate_cex_complete(self, builder):
        """Test validating complete CEX exchange."""
        builder.cex().amount(1.0).from_token("ETH").to_token("BNB").address_to("0x123")
        # Should not raise
        builder._validate_cex()
    
    def test_validate_cex_missing_amount(self, builder):
        """Test that missing amount raises ValidationError."""
        builder.cex().from_token("ETH").to_token("BNB").address_to("0x123")
        with pytest.raises(ValidationError, match="Amount is required"):
            builder._validate_cex()
    
    def test_validate_cex_missing_from_token(self, builder):
        """Test that missing from_token raises ValidationError."""
        builder.cex().amount(1.0).to_token("BNB").address_to("0x123")
        with pytest.raises(ValidationError, match="from_token is required"):
            builder._validate_cex()
    
    def test_validate_cex_missing_to_token(self, builder):
        """Test that missing to_token raises ValidationError."""
        builder.cex().amount(1.0).from_token("ETH").address_to("0x123")
        with pytest.raises(ValidationError, match="to_token is required"):
            builder._validate_cex()
    
    def test_validate_cex_missing_address_to(self, builder):
        """Test that missing address_to raises ValidationError."""
        builder.cex().amount(1.0).from_token("ETH").to_token("BNB")
        with pytest.raises(ValidationError, match="address_to is required"):
            builder._validate_cex()
    
    def test_validate_dex_complete(self, builder, sample_route_data):
        """Test validating complete DEX exchange."""
        route = RouteDTO.from_dict(sample_route_data)
        builder.dex().amount(1.0).from_token("token1").to_token("token2") \
            .address_from("0x123").address_to("0x456") \
            .swap("sw").quote_id("quote123").route(route)
        # Should not raise
        builder._validate_dex()
    
    def test_validate_dex_missing_amount(self, builder, sample_route_data):
        """Test that missing amount raises ValidationError."""
        route = RouteDTO.from_dict(sample_route_data)
        builder.dex().from_token("token1").to_token("token2") \
            .address_from("0x123").address_to("0x456") \
            .swap("sw").quote_id("quote123").route(route)
        with pytest.raises(ValidationError, match="Amount is required"):
            builder._validate_dex()
    
    def test_validate_dex_missing_swap(self, builder, sample_route_data):
        """Test that missing swap raises ValidationError."""
        route = RouteDTO.from_dict(sample_route_data)
        builder.dex().amount(1.0).from_token("token1").to_token("token2") \
            .address_from("0x123").address_to("0x456") \
            .quote_id("quote123").route(route)
        with pytest.raises(ValidationError, match="swap is required"):
            builder._validate_dex()
    
    def test_validate_dex_missing_route(self, builder):
        """Test that missing route raises ValidationError."""
        builder.dex().amount(1.0).from_token("token1").to_token("token2") \
            .address_from("0x123").address_to("0x456") \
            .swap("sw").quote_id("quote123")
        with pytest.raises(ValidationError, match="route is required"):
            builder._validate_dex()
    
    def test_execute_cex(self, builder, mock_client):
        """Test executing CEX exchange."""
        mock_response = MagicMock()
        mock_client.post_cex_exchange.return_value = mock_response
        
        builder.cex().amount(1.0).from_token("ETH").to_token("BNB") \
            .address_to("0x123").anonymous(True)
        
        result = builder.execute()
        assert result == mock_response
        mock_client.post_cex_exchange.assert_called_once()
        call_kwargs = mock_client.post_cex_exchange.call_args[1]
        assert call_kwargs["amount"] == 1.0
        assert call_kwargs["from_token"] == "ETH"
        assert call_kwargs["to_token"] == "BNB"
        assert call_kwargs["address_to"] == "0x123"
        assert call_kwargs["anonymous"] is True
    
    def test_execute_dex(self, builder, mock_client, sample_route_data):
        """Test executing DEX exchange."""
        route = RouteDTO.from_dict(sample_route_data)
        mock_response = MagicMock()
        mock_client.post_dex_exchange.return_value = mock_response
        
        builder.dex().amount(1.0).from_token("token1").to_token("token2") \
            .address_from("0x123").address_to("0x456") \
            .swap("sw").quote_id("quote123").route(route)
        
        result = builder.execute()
        assert result == mock_response
        mock_client.post_dex_exchange.assert_called_once()
        call_kwargs = mock_client.post_dex_exchange.call_args[1]
        assert call_kwargs["amount"] == 1.0
        assert call_kwargs["token_id_from"] == "token1"
        assert call_kwargs["token_id_to"] == "token2"
        assert call_kwargs["swap"] == "sw"
    
    def test_execute_no_exchange_type_raises(self, builder):
        """Test that execute without exchange type raises ValidationError."""
        builder.amount(1.0).from_token("ETH").to_token("BNB").address_to("0x123")
        with pytest.raises(ValidationError, match="Exchange type must be set"):
            builder.execute()
    
    def test_fluent_interface(self, builder):
        """Test that builder methods return self for fluent interface."""
        result = builder.cex().amount(1.0).from_token("ETH").to_token("BNB")
        assert result is builder
