"""Integration tests for client helper methods."""

import pytest
import time
from unittest.mock import patch

from houdiniswap import HoudiniSwapClient
from houdiniswap.models import TransactionStatus, DEXToken


class TestIterDexTokens:
    """Tests for iter_dex_tokens method."""
    
    def test_iter_dex_tokens_single_page(self, client, sample_dex_tokens_response_data):
        """Test iterating DEX tokens from single page."""
        from houdiniswap.models import DEXTokensResponse, DEXToken
        response = DEXTokensResponse(
            count=1,
            tokens=[DEXToken.from_dict(sample_dex_tokens_response_data['tokens'][0])]
        )
        with patch.object(client, 'get_dex_tokens', return_value=response):
            tokens = list(client.iter_dex_tokens())
            assert len(tokens) == 1
            assert tokens[0].symbol == "USDC"
    
    def test_iter_dex_tokens_multiple_pages(self, client, sample_dex_token_data):
        """Test iterating DEX tokens across multiple pages."""
        from houdiniswap.models import DEXTokensResponse, DEXToken
        # Mock responses for multiple pages
        page1 = DEXTokensResponse(
            count=250,
            tokens=[DEXToken.from_dict(sample_dex_token_data) for _ in range(100)]
        )
        page2 = DEXTokensResponse(
            count=250,
            tokens=[DEXToken.from_dict(sample_dex_token_data) for _ in range(100)]
        )
        page3 = DEXTokensResponse(
            count=250,
            tokens=[DEXToken.from_dict(sample_dex_token_data) for _ in range(50)]
        )
        
        with patch.object(client, 'get_dex_tokens', side_effect=[page1, page2, page3]):
            tokens = list(client.iter_dex_tokens(page_size=100))
            assert len(tokens) == 250
    
    def test_iter_dex_tokens_with_chain(self, client, sample_dex_tokens_response_data):
        """Test iterating DEX tokens with chain filter."""
        from houdiniswap.models import DEXTokensResponse, DEXToken
        response = DEXTokensResponse(
            count=1,
            tokens=[DEXToken.from_dict(sample_dex_tokens_response_data['tokens'][0])]
        )
        
        with patch.object(client, 'get_dex_tokens', return_value=response):
            tokens = list(client.iter_dex_tokens(chain="base"))
            assert len(tokens) == 1
            client.get_dex_tokens.assert_called_with(page=1, page_size=100, chain="base")
    
    def test_iter_dex_tokens_empty(self, client):
        """Test iterating when no tokens."""
        from houdiniswap.models import DEXTokensResponse
        empty_response = DEXTokensResponse(count=0, tokens=[])
        
        with patch.object(client, 'get_dex_tokens', return_value=empty_response):
            tokens = list(client.iter_dex_tokens())
            assert len(tokens) == 0


class TestGetAllDexTokens:
    """Tests for get_all_dex_tokens method."""
    
    def test_get_all_dex_tokens(self, client, sample_dex_token_data):
        """Test getting all DEX tokens."""
        from houdiniswap.models import DEXToken
        token = DEXToken.from_dict(sample_dex_token_data)
        
        with patch.object(client, 'iter_dex_tokens', return_value=iter([token])):
            tokens = client.get_all_dex_tokens()
            assert len(tokens) == 1
            assert tokens[0].symbol == "USDC"


class TestWaitForStatus:
    """Tests for wait_for_status method."""
    
    def test_wait_for_status_immediate(self, client, sample_status_data):
        """Test wait_for_status when status is already target."""
        from houdiniswap.models import Status
        status_data = {**sample_status_data, "status": TransactionStatus.FINISHED.value}
        status = Status.from_dict(status_data)
        
        with patch.object(client, 'get_status', return_value=status):
            result = client.wait_for_status("test123", TransactionStatus.FINISHED, timeout=10, poll_interval=0.1)
            assert result.status == TransactionStatus.FINISHED
    
    def test_wait_for_status_after_poll(self, client):
        """Test wait_for_status that requires polling."""
        from houdiniswap.models import Status
        statuses = [
            Status.from_dict({"houdiniId": "test123", "status": TransactionStatus.WAITING.value}),
            Status.from_dict({"houdiniId": "test123", "status": TransactionStatus.CONFIRMING.value}),
            Status.from_dict({"houdiniId": "test123", "status": TransactionStatus.FINISHED.value}),
        ]
        
        with patch.object(client, 'get_status', side_effect=statuses), \
             patch('time.sleep'):  # Speed up test
            result = client.wait_for_status("test123", TransactionStatus.FINISHED, timeout=10, poll_interval=0.1)
            assert result.status == TransactionStatus.FINISHED
    
    def test_wait_for_status_timeout(self, client):
        """Test wait_for_status timeout."""
        from houdiniswap.models import Status
        status = Status.from_dict({"houdiniId": "test123", "status": TransactionStatus.WAITING.value})
        
        with patch.object(client, 'get_status', return_value=status), \
             patch('time.sleep'), \
             patch('time.time', side_effect=[0, 11]):  # Simulate timeout
            with pytest.raises(TimeoutError, match="Timeout waiting for status"):
                client.wait_for_status("test123", TransactionStatus.FINISHED, timeout=10, poll_interval=0.1)


class TestPollUntilFinished:
    """Tests for poll_until_finished method."""
    
    def test_poll_until_finished_success(self, client):
        """Test poll_until_finished with FINISHED status."""
        from houdiniswap.models import Status
        statuses = [
            Status.from_dict({"houdiniId": "test123", "status": TransactionStatus.WAITING.value}),
            Status.from_dict({"houdiniId": "test123", "status": TransactionStatus.FINISHED.value}),
        ]
        
        with patch.object(client, 'get_status', side_effect=statuses), \
             patch('time.sleep'):  # Speed up test
            result = client.poll_until_finished("test123", timeout=10, poll_interval=0.1)
            assert result.status == TransactionStatus.FINISHED
    
    def test_poll_until_finished_failed(self, client):
        """Test poll_until_finished with FAILED status."""
        from houdiniswap.models import Status
        status = Status.from_dict({"houdiniId": "test123", "status": TransactionStatus.FAILED.value})
        
        with patch.object(client, 'get_status', return_value=status), \
             patch('time.sleep'):
            result = client.poll_until_finished("test123", timeout=10, poll_interval=0.1)
            assert result.status == TransactionStatus.FAILED
    
    def test_poll_until_finished_timeout(self, client):
        """Test poll_until_finished timeout."""
        from houdiniswap.models import Status
        status = Status.from_dict({"houdiniId": "test123", "status": TransactionStatus.WAITING.value})
        
        with patch.object(client, 'get_status', return_value=status), \
             patch('time.sleep'), \
             patch('time.time', side_effect=[0, 11]):  # Simulate timeout
            with pytest.raises(TimeoutError, match="Timeout waiting for transaction"):
                client.poll_until_finished("test123", timeout=10, poll_interval=0.1)


class TestExecuteParallel:
    """Tests for execute_parallel method."""
    
    def test_execute_parallel_success(self, client):
        """Test executing parallel requests."""
        def request1():
            return "result1"
        
        def request2():
            return "result2"
        
        def request3():
            return "result3"
        
        results = client.execute_parallel([request1, request2, request3], max_workers=2)
        assert results == ["result1", "result2", "result3"]
    
    def test_execute_parallel_with_errors(self, client):
        """Test executing parallel requests with errors."""
        def request1():
            return "result1"
        
        def request2():
            raise ValueError("Error in request2")
        
        def request3():
            return "result3"
        
        results = client.execute_parallel([request1, request2, request3], max_workers=2)
        assert results[0] == "result1"
        assert isinstance(results[1], ValueError)
        assert results[2] == "result3"
    
    def test_execute_parallel_empty_list(self, client):
        """Test executing parallel with empty list."""
        results = client.execute_parallel([], max_workers=2)
        assert results == []


class TestClearCache:
    """Tests for clear_cache method."""
    
    def test_clear_cache(self, client, sample_token_data):
        """Test clearing the token cache."""
        client.cache_enabled = True
        mock_response = [sample_token_data]
        
        with patch.object(client, '_request', return_value=mock_response):
            # Populate cache
            client.get_cex_tokens()
            assert len(client._token_cache) > 0
            
            # Clear cache
            client.clear_cache()
            assert len(client._token_cache) == 0


class TestExchangeBuilder:
    """Tests for exchange_builder method."""
    
    def test_exchange_builder(self, client):
        """Test creating exchange builder."""
        from houdiniswap.builder import ExchangeBuilder
        builder = client.exchange_builder()
        assert isinstance(builder, ExchangeBuilder)
        assert builder.client == client
