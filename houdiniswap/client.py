"""Main client for Houdini Swap API."""

import logging
import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, List, Dict, Any, TypeGuard, Callable, Union
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal, InvalidOperation

from .constants import (
    BASE_URL_PRODUCTION,
    DEFAULT_TIMEOUT,
    DEFAULT_PAGE_SIZE,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_BACKOFF_FACTOR,
    DEFAULT_CACHE_TTL,
    ENV_VAR_API_URL,
    API_VERSION_DEFAULT,
    HEADER_API_VERSION,
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_UNAUTHORIZED,
    HTTP_STATUS_TOO_MANY_REQUESTS,
    HTTP_STATUS_INTERNAL_SERVER_ERROR,
    HTTP_STATUS_BAD_GATEWAY,
    HTTP_STATUS_SERVICE_UNAVAILABLE,
    HTTP_STATUS_GATEWAY_TIMEOUT,
    ENDPOINT_TOKENS,
    ENDPOINT_DEX_TOKENS,
    ENDPOINT_QUOTE,
    ENDPOINT_DEX_QUOTE,
    ENDPOINT_EXCHANGE,
    ENDPOINT_DEX_EXCHANGE,
    ENDPOINT_DEX_APPROVE,
    ENDPOINT_DEX_CONFIRM_TX,
    ENDPOINT_STATUS,
    ENDPOINT_MIN_MAX,
    ENDPOINT_VOLUME,
    ENDPOINT_WEEKLY_VOLUME,
    ERROR_INVALID_CREDENTIALS,
    ERROR_AUTHENTICATION_FAILED,
    ERROR_NETWORK,
    ERROR_UNEXPECTED,
)
from .exceptions import (
    HoudiniSwapError,
    AuthenticationError,
    APIError,
    ValidationError,
    NetworkError,
)
from .models import (
    Token,
    DEXToken,
    DEXTokensResponse,
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
)


def _is_list_response(response: Dict[str, Any]) -> TypeGuard[List[Dict[str, Any]]]:
    """Type guard to help type checkers understand list responses."""
    return isinstance(response, list)


def _is_dict_response(response: Dict[str, Any]) -> TypeGuard[Dict[str, Any]]:
    """Type guard to help type checkers understand dict responses."""
    return isinstance(response, dict)


class HoudiniSwapClient:
    """
    Client for interacting with the Houdini Swap API.
    
    All requests require authentication using API key and secret.
    
    Thread Safety:
        This client is not thread-safe. Each thread should use its own instance
        or external synchronization must be used when sharing an instance.
    
    Performance:
        Uses a persistent HTTP session for connection pooling. Network requests
        are synchronous and will block until a response is received or timeout occurs.
    
    Side Effects:
        Creates and maintains an HTTP session. Credentials are stored securely
        in private attributes to prevent direct access.
    """
    
    __slots__ = (
        '_api_key',
        '_api_secret',
        'base_url',
        'timeout',
        'api_version',
        'session',
        'verify_ssl',
        'max_retries',
        'retry_backoff_factor',
        'logger',
        'cache_enabled',
        'cache_ttl',
        '_token_cache',
        '_closed',
    )
    
    BASE_URL = "https://api-partner.houdiniswap.com"
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        api_version: Optional[str] = None,
        verify_ssl: bool = True,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_backoff_factor: float = DEFAULT_RETRY_BACKOFF_FACTOR,
        cache_enabled: bool = False,
        cache_ttl: int = DEFAULT_CACHE_TTL,
        log_level: Optional[int] = None,
    ):
        """
        Initialize the Houdini Swap client.
        
        Args:
            api_key: Your Houdini Swap API key
            api_secret: Your Houdini Swap API secret
            base_url: Optional custom base URL. If not provided, checks HOUDINI_SWAP_API_URL
                     environment variable, then defaults to production URL.
            timeout: Request timeout in seconds (default: 30, see DEFAULT_TIMEOUT constant)
            api_version: API version to use (default: "v1"). Sent as X-API-Version header.
            verify_ssl: Whether to verify SSL certificates (default: True). Set to False only for testing.
            max_retries: Maximum number of retry attempts for failed requests (default: 3)
            retry_backoff_factor: Multiplier for exponential backoff (default: 1.0)
            cache_enabled: Enable caching for token lists (default: False)
            cache_ttl: Cache time-to-live in seconds (default: 300 = 5 minutes)
            log_level: Logging level (logging.DEBUG, INFO, WARNING, ERROR). Default: WARNING.
        
        Raises:
            ValidationError: If api_key or api_secret is empty or None
        
        Edge Cases:
            - Empty strings are treated as invalid credentials
            - None values for api_key or api_secret will raise ValidationError
            - Base URL can be set via environment variable HOUDINI_SWAP_API_URL
        
        Side Effects:
            Creates a requests.Session() object and stores credentials securely in private attributes.
            Sets up logging if log_level is provided.
        """
        if not api_key or not api_secret:
            raise ValidationError(ERROR_INVALID_CREDENTIALS)
        
        # Validate credentials format
        self._validate_credentials(api_key, api_secret)
        
        # Store credentials in private attributes to prevent direct access
        object.__setattr__(self, '_api_key', api_key)
        object.__setattr__(self, '_api_secret', api_secret)
        
        # Base URL resolution: parameter > environment variable > default
        if base_url:
            object.__setattr__(self, 'base_url', base_url)
        else:
            object.__setattr__(self, 'base_url', os.getenv(ENV_VAR_API_URL, BASE_URL_PRODUCTION))
        
        object.__setattr__(self, 'timeout', timeout or DEFAULT_TIMEOUT)
        object.__setattr__(self, 'api_version', api_version or API_VERSION_DEFAULT)
        object.__setattr__(self, 'verify_ssl', verify_ssl)
        object.__setattr__(self, 'max_retries', max_retries)
        object.__setattr__(self, 'retry_backoff_factor', retry_backoff_factor)
        
        # Caching configuration
        object.__setattr__(self, 'cache_enabled', cache_enabled)
        object.__setattr__(self, 'cache_ttl', cache_ttl)
        object.__setattr__(self, '_token_cache', {})  # key -> (data, timestamp)
        
        # Setup logging
        self.logger = logging.getLogger("houdiniswap")
        if log_level is not None:
            self.logger.setLevel(log_level)
            # Add handler if none exists
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                ))
                self.logger.addHandler(handler)
        
        # Create session with connection pooling configuration
        session = requests.Session()
        # Add closed property to session for testing
        session.closed = False
        
        # Configure connection pooling with HTTPAdapter
        # pool_connections: number of connection pools to cache
        # pool_maxsize: maximum number of connections to save in the pool
        adapter = HTTPAdapter(
            pool_connections=10,  # Number of connection pools to cache
            pool_maxsize=20,      # Maximum number of connections to save in the pool
            max_retries=0,        # We handle retries in _request method
            pool_block=False,     # Don't block if pool is full
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        object.__setattr__(self, 'session', session)
        # Use private attributes for credentials in header
        self.session.headers.update({
            "Authorization": f"{self._api_key}:{self._api_secret}",
            "Content-Type": "application/json",
            HEADER_API_VERSION: self.api_version,
        })
        # Explicitly set SSL verification
        self.session.verify = verify_ssl
    
    def __getattribute__(self, name: str):
        """Prevent direct access to credentials."""
        if name in ('api_key', 'api_secret'):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'. "
                "Credentials are stored securely and cannot be accessed directly. "
                "Use the client methods to interact with the API."
            )
        return object.__getattribute__(self, name)
    
    def __repr__(self) -> str:
        """String representation that doesn't expose credentials."""
        return f"<{self.__class__.__name__}(base_url='{self.base_url}')>"
    
    def _validate_credentials(self, api_key: str, api_secret: str) -> None:
        """
        Validate API credentials format.
        
        Args:
            api_key: API key to validate
            api_secret: API secret to validate
            
        Raises:
            ValidationError: If credentials are invalid
        """
        # Check for colon character (would break Authorization header format)
        if ":" in api_key or ":" in api_secret:
            raise ValidationError("API key and secret cannot contain ':' character")
        
        # Validate length (HTTP headers typically have 8KB limit, be conservative)
        MAX_CREDENTIAL_LENGTH = 1000
        if len(api_key) > MAX_CREDENTIAL_LENGTH or len(api_secret) > MAX_CREDENTIAL_LENGTH:
            raise ValidationError(f"API credentials exceed maximum length of {MAX_CREDENTIAL_LENGTH} characters")
        
        # Check for empty strings (already checked above, but double-check)
        if not api_key.strip() or not api_secret.strip():
            raise ValidationError(ERROR_INVALID_CREDENTIALS)
    
    def _redact_credentials(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact credentials from data for logging."""
        redacted = dict(data)
        if "Authorization" in redacted:
            redacted["Authorization"] = "***REDACTED***"
        return redacted
    
    def _sanitize_input(self, value: str, field_name: str = "input") -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            value: Input string to sanitize
            field_name: Name of the field for error messages
            
        Returns:
            Sanitized string (stripped of whitespace)
            
        Raises:
            ValidationError: If input is invalid
        """
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string, got {type(value).__name__}")
        
        sanitized = value.strip()
        if not sanitized:
            raise ValidationError(f"{field_name} cannot be empty")
        
        # Check for potentially dangerous characters
        dangerous_chars = ['\n', '\r', '\t', '\x00']
        for char in dangerous_chars:
            if char in sanitized:
                raise ValidationError(f"{field_name} contains invalid characters")
        
        return sanitized
    
    def _validate_amount(self, amount: Union[float, Decimal, int, str], field_name: str = "amount") -> None:
        """Validate that amount is positive."""
        # First check if it's a valid type
        if not isinstance(amount, (int, float, Decimal, str)):
            raise ValidationError(f"{field_name} must be a number, got {type(amount).__name__}")
        # For strings, validate they can be converted to a number and are positive
        if isinstance(amount, str):
            try:
                amount_decimal = Decimal(amount)
                if amount_decimal <= 0:
                    raise ValidationError(f"{field_name} must be greater than 0, got {amount}")
            except (ValueError, InvalidOperation, TypeError):
                raise ValidationError(f"{field_name} must be a valid number, got {amount!r}")
        # For numeric types, check if positive
        elif isinstance(amount, (int, float, Decimal)):
            if amount <= 0:
                raise ValidationError(f"{field_name} must be greater than 0, got {amount}")
    
    def _normalize_amount(self, amount: Union[str, Decimal, float]) -> str:
        """Normalize amount to string for API requests."""
        if isinstance(amount, Decimal):
            return str(amount)
        if isinstance(amount, (int, float)):
            # Convert to Decimal first to avoid precision issues, then to string
            return str(Decimal(str(amount)))
        if isinstance(amount, str):
            # Validate it's a valid number
            try:
                Decimal(amount)
                return amount
            except (ValueError, TypeError, InvalidOperation):
                raise ValidationError(f"amount must be a valid number, got {amount!r}")
        raise ValidationError(f"amount must be str, Decimal, or number, got {type(amount).__name__}")
    
    def _normalize_amount_to_decimal(self, amount: Union[str, Decimal, float]) -> Decimal:
        """Normalize amount to Decimal for internal use."""
        if isinstance(amount, Decimal):
            return amount
        if isinstance(amount, (int, float)):
            return Decimal(str(amount))
        if isinstance(amount, str):
            try:
                return Decimal(amount)
            except (ValueError, TypeError, InvalidOperation):
                raise ValidationError(f"amount must be a valid number, got {amount!r}")
        raise ValidationError(f"amount must be str, Decimal, or number, got {type(amount).__name__}")
    
    def _validate_token_id(self, token_id: str, field_name: str = "token_id") -> None:
        """Validate that token ID is non-empty."""
        self._sanitize_input(token_id, field_name)
    
    def _validate_page(self, page: int, field_name: str = "page") -> None:
        """Validate that page number is positive."""
        if not isinstance(page, int):
            raise ValidationError(f"{field_name} must be an integer, got {type(page).__name__}")
        if page < 1:
            raise ValidationError(f"{field_name} must be >= 1, got {page}")
    
    def _validate_page_size(self, page_size: int, field_name: str = "page_size") -> None:
        """Validate that page size is positive."""
        if not isinstance(page_size, int):
            raise ValidationError(f"{field_name} must be an integer, got {type(page_size).__name__}")
        if page_size < 1:
            raise ValidationError(f"{field_name} must be >= 1, got {page_size}")
    
    def _validate_hex_string(self, value: str, field_name: str = "hex_string") -> None:
        """Validate that value is a valid hex string."""
        sanitized = self._sanitize_input(value, field_name)
        try:
            int(sanitized, 16)
        except ValueError:
            raise ValidationError(f"{field_name} must be a valid hexadecimal string")
    
    def _validate_houdini_id(self, houdini_id: str) -> None:
        """Validate houdini ID format."""
        sanitized = self._sanitize_input(houdini_id, "houdini_id")
        # Houdini IDs are typically alphanumeric, 20-30 chars
        if not sanitized.replace('_', '').replace('-', '').isalnum():
            raise ValidationError("houdini_id must be alphanumeric (may include _ or -)")
        if len(sanitized) < 10 or len(sanitized) > 50:
            raise ValidationError(f"houdini_id must be between 10 and 50 characters, got {len(sanitized)}")
    
    def _validate_address(self, address: str, network: Optional["Network"] = None, field_name: str = "address") -> None:
        """
        Validate address format.
        
        Args:
            address: Address to validate
            network: Optional Network object with address_validation regex
            field_name: Name of field for error messages
        """
        import re
        sanitized = self._sanitize_input(address, field_name)
        
        # If network provided, use its validation regex
        if network and network.address_validation:
            try:
                pattern = re.compile(network.address_validation)
                if not pattern.match(sanitized):
                    raise ValidationError(
                        f"{field_name} does not match expected format for network {network.name}: {network.address_validation}"
                    )
            except re.error:
                # Invalid regex in network data - skip regex validation
                pass
        
        # Basic validation: addresses should be reasonable length
        if len(sanitized) < 10 or len(sanitized) > 200:
            raise ValidationError(f"{field_name} length must be between 10 and 200 characters")
    
    def _sign_request(self, method: str, url: str, params: Optional[Dict[str, Any]] = None, 
                     json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Sign request for authentication (extensible for future signing requirements).
        
        Currently a no-op as the API only requires basic auth.
        Can be extended if API adds request signing requirements.
        
        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            json_data: JSON body
            
        Returns:
            Dictionary of headers/parameters to add to request
        """
        # Placeholder for future request signing
        # If API adds signing requirements, implement here
        return {}
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API with automatic retries.
        
        Note: params and json_data are defensively copied to prevent mutation
        of caller's dictionaries. This ensures safe concurrent usage.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON body for POST requests
            
        Returns:
            JSON response as dictionary
            
        Raises:
            APIError: If the API returns an error
            NetworkError: If a network error occurs after all retries
            AuthenticationError: If authentication fails
        """
        url = urljoin(self.base_url, endpoint.lstrip("/"))
        
        # Defensive copy of params to prevent mutation of caller's dict
        # This ensures safe concurrent usage and prevents accidental side effects
        safe_params = dict(params) if params else None
        safe_json_data = dict(json_data) if json_data else None
        
        # Status codes that should trigger retries
        retryable_statuses = [
            HTTP_STATUS_TOO_MANY_REQUESTS,
            HTTP_STATUS_INTERNAL_SERVER_ERROR,
            HTTP_STATUS_BAD_GATEWAY,
            HTTP_STATUS_SERVICE_UNAVAILABLE,
            HTTP_STATUS_GATEWAY_TIMEOUT,
        ]
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Log request (redact credentials)
                if self.logger.isEnabledFor(logging.DEBUG):
                    log_data = {
                        "method": method,
                        "url": url,
                        "params": safe_params,
                        "json": safe_json_data,
                    }
                    self.logger.debug(f"Request: {self._redact_credentials(log_data)}")
                
                start_time = time.time()
                response = self.session.request(
                    method=method,
                    url=url,
                    params=safe_params,
                    json=safe_json_data,
                    timeout=self.timeout,
                )
                duration = time.time() - start_time
                
                # Log response
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug(f"Response: {response.status_code} ({duration:.2f}s)")
                
                # Handle authentication errors (don't retry)
                if response.status_code == HTTP_STATUS_UNAUTHORIZED:
                    self.logger.warning("Authentication failed")
                    raise AuthenticationError(ERROR_AUTHENTICATION_FAILED)
                
                # Handle rate limiting (429) with special backoff
                if response.status_code == HTTP_STATUS_TOO_MANY_REQUESTS:
                    if attempt < self.max_retries:
                        # Check for Retry-After header (seconds to wait)
                        retry_after = response.headers.get("Retry-After")
                        if retry_after:
                            try:
                                wait_time = float(retry_after)
                            except (ValueError, TypeError):
                                # If Retry-After is invalid, use exponential backoff
                                wait_time = self.retry_backoff_factor * (2 ** attempt) * 2  # Longer backoff for rate limits
                        else:
                            # No Retry-After header, use longer exponential backoff
                            wait_time = self.retry_backoff_factor * (2 ** attempt) * 2  # 2x longer for rate limits
                        
                        self.logger.warning(
                            f"Rate limit exceeded (429) (attempt {attempt + 1}/{self.max_retries + 1}). "
                            f"Retrying in {wait_time:.2f}s..."
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        # Max retries reached for rate limit
                        error_data = None
                        try:
                            error_data = response.json()
                            error_message = error_data.get("message", "Rate limit exceeded")
                        except ValueError:
                            error_message = "Rate limit exceeded"
                        
                        self.logger.error(f"Rate limit exceeded after {self.max_retries + 1} attempts")
                        raise APIError(
                            f"{error_message}. Please wait before retrying.",
                            status_code=response.status_code,
                            response=error_data,
                        )
                
                # Handle other retryable HTTP errors
                if response.status_code in retryable_statuses:
                    if attempt < self.max_retries:
                        wait_time = self.retry_backoff_factor * (2 ** attempt)
                        self.logger.warning(
                            f"Retryable error {response.status_code} (attempt {attempt + 1}/{self.max_retries + 1}). "
                            f"Retrying in {wait_time:.2f}s..."
                        )
                        time.sleep(wait_time)
                        continue
                
                # Handle other HTTP errors (don't retry)
                if response.status_code >= HTTP_STATUS_BAD_REQUEST:
                    error_data = None
                    try:
                        error_data = response.json()
                        error_message = error_data.get("message", f"API error: {response.status_code}")
                    except ValueError:
                        # JSON parsing failed - include raw response text (limit length)
                        error_message = f"API error: {response.status_code} - {response.text[:500]}"
                    
                    self.logger.error(f"API error: {error_message}")
                    raise APIError(
                        error_message,
                        status_code=response.status_code,
                        response=error_data,
                    )
                
                # Parse JSON response
                try:
                    result = response.json()
                    if self.logger.isEnabledFor(logging.DEBUG):
                        self.logger.debug(f"Request successful: {method} {endpoint}")
                    return result
                except ValueError:
                    # Some endpoints return non-JSON (e.g., boolean true)
                    return {"response": response.text}
                    
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = self.retry_backoff_factor * (2 ** attempt)
                    self.logger.warning(
                        f"Network error (attempt {attempt + 1}/{self.max_retries + 1}): {str(e)}. "
                        f"Retrying in {wait_time:.2f}s..."
                    )
                    time.sleep(wait_time)
                    continue
                # Last attempt failed
                self.logger.error(f"Network error after {self.max_retries + 1} attempts: {str(e)}")
                raise NetworkError(ERROR_NETWORK.format(str(e))) from e
            except (APIError, AuthenticationError):
                # Don't retry these
                raise
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = self.retry_backoff_factor * (2 ** attempt)
                    self.logger.warning(
                        f"Unexpected error (attempt {attempt + 1}/{self.max_retries + 1}): {str(e)}. "
                        f"Retrying in {wait_time:.2f}s..."
                    )
                    time.sleep(wait_time)
                    continue
                # Last attempt failed
                self.logger.error(f"Unexpected error after {self.max_retries + 1} attempts: {str(e)}")
                raise HoudiniSwapError(ERROR_UNEXPECTED.format(str(e))) from e
        
        # Should never reach here, but just in case
        if last_exception:
            raise HoudiniSwapError(ERROR_UNEXPECTED.format(str(last_exception))) from last_exception
        raise HoudiniSwapError("Request failed after all retries")
    
    def __enter__(self) -> "HoudiniSwapClient":
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager and close session."""
        self.close()
    
    def close(self) -> None:
        """Close the HTTP session and release resources."""
        if hasattr(self, 'session') and self.session:
            try:
                closed = object.__getattribute__(self, '_closed')
            except AttributeError:
                closed = False
            if not closed:
                self.session.close()
                self.session.closed = True
                object.__setattr__(self, '_closed', True)
    
    # ==================== Token Information APIs ====================
    
    def clear_cache(self) -> None:
        """Clear the token cache."""
        self._token_cache.clear()
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("Token cache cleared")
    
    def get_cex_tokens(self) -> List[Token]:
        """
        Get a list of tokens supported by Houdini Swap for CEX exchanges.
        
        Results are cached if caching is enabled (default: True) with TTL
        (default: 5 minutes). Use clear_cache() to manually invalidate.
        
        Returns:
            List of Token objects
        
        Raises:
            APIError: If the API returns an error response (status >= 400)
            NetworkError: If a network error occurs (connection timeout, DNS failure, etc.)
            AuthenticationError: If authentication fails (401 status)
            HoudiniSwapError: For unexpected errors
        
        Edge Cases:
            - Returns empty list if API returns empty array
            - May raise APIError if API structure changes unexpectedly
            - Cached results are returned if cache is enabled and not expired
        
        Performance:
            Single HTTP GET request (or cached result). Response time depends on API latency.
            Typically completes in < 1 second under normal conditions.
            Cached results return immediately.
        
        Side Effects:
            Makes a network request if cache is disabled or expired. Updates cache if enabled.
        """
        cache_key = "cex_tokens"
        current_time = time.time()
        
        # Check cache
        if self.cache_enabled and cache_key in self._token_cache:
            cached_data, cached_time = self._token_cache[cache_key]
            if current_time - cached_time < self.cache_ttl:
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug(f"Returning cached CEX tokens (age: {current_time - cached_time:.1f}s)")
                return cached_data
        
        # Fetch from API
        response = self._request("GET", ENDPOINT_TOKENS)
        
        # Validate response is a list before list comprehension
        if not isinstance(response, list):
            raise APIError(
                f"Unexpected response type from tokens endpoint: expected list, got {type(response).__name__}",
                status_code=None,
                response=response,
            )
        
        tokens = [Token.from_dict(token_data) for token_data in response]
        
        # Update cache
        if self.cache_enabled:
            self._token_cache[cache_key] = (tokens, current_time)
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug("Cached CEX tokens")
        
        return tokens
    
    def get_dex_tokens(
        self,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
        chain: Optional[str] = None,
    ) -> DEXTokensResponse:
        """
        Get a list of tokens supported for DEX exchanges.
        
        Args:
            page: Page number (default: 1)
            page_size: Number of tokens per page (default: 100, see DEFAULT_PAGE_SIZE constant)
            chain: Chain short name (e.g., "base") - optional
            
        Returns:
            DEXTokensResponse object with count and tokens fields
        
        Note:
            CEX methods use token symbols (e.g., "ETH", "BNB") while DEX methods
            use token IDs (e.g., "6689b73ec90e45f3b3e51553"). This reflects the
            underlying API differences.
        
        Raises:
            APIError: If the API returns an error response (status >= 400)
            NetworkError: If a network error occurs (connection timeout, DNS failure, etc.)
            AuthenticationError: If authentication fails (401 status)
            HoudiniSwapError: For unexpected errors
        
        Edge Cases:
            - Returns {'count': 0, 'tokens': []} if no tokens found or page out of range
            - page < 1 may return empty results (API behavior)
            - page_size > 100 may be limited by API
        
        Performance:
            Single HTTP GET request with pagination. Response time depends on API latency
            and page size. Typically completes in < 1 second under normal conditions.
        
        Side Effects:
            Makes a network request. No local state is modified.
        """
        # Validate parameters
        self._validate_page(page)
        self._validate_page_size(page_size)
        
        # Create cache key from parameters
        cache_key = f"dex_tokens_{page}_{page_size}_{chain or 'all'}"
        current_time = time.time()
        
        # Check cache
        if self.cache_enabled and cache_key in self._token_cache:
            cached_data, cached_time = self._token_cache[cache_key]
            if current_time - cached_time < self.cache_ttl:
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug(f"Returning cached DEX tokens (age: {current_time - cached_time:.1f}s)")
                return cached_data
        
        # Create fresh params dict for each call (no mutable defaults)
        # This pattern ensures thread-safety and prevents accidental mutations
        params = {
            "page": page,
            "pageSize": page_size,
        }
        if chain:
            params["chain"] = chain
        
        # Fetch from API
        response = self._request("GET", ENDPOINT_DEX_TOKENS, params=params)
        result = DEXTokensResponse(
            count=response.get("count", 0),
            tokens=[DEXToken.from_dict(token_data) for token_data in response.get("tokens", [])],
        )
        
        # Update cache
        if self.cache_enabled:
            self._token_cache[cache_key] = (result, current_time)
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"Cached DEX tokens (key: {cache_key})")
        
        return result
    
    # ==================== Quote APIs ====================
    
    def get_cex_quote(
        self,
        amount: str,
        from_token: str,
        to_token: str,
        anonymous: bool = False,
        use_xmr: Optional[bool] = None,
    ) -> Quote:
        """
        Get a quote for a CEX exchange transaction.
        
        Args:
            amount: The amount to transfer (as string)
            from_token: TokenID of source currency (e.g., "BNB")
            to_token: TokenID of destination currency (e.g., "ETH")
            anonymous: Whether to use anonymous flow (default: False)
            use_xmr: Use XMR for anonymous transactions (optional)
            
        Returns:
            Quote object with exchange rate and estimated output amount
        
        Raises:
            APIError: If the API returns an error response (status >= 400)
            NetworkError: If a network error occurs (connection timeout, DNS failure, etc.)
            AuthenticationError: If authentication fails (401 status)
            HoudiniSwapError: For unexpected errors
        
        Edge Cases:
            - Invalid token IDs will result in APIError
            - Amounts below minimum or above maximum will result in APIError
            - Quotes may expire after a certain time period (check quote validity)
            - Network issues may cause timeouts
        
        Performance:
            Single HTTP GET request. Response time depends on API latency.
            Typically completes in < 1 second under normal conditions.
        
        Side Effects:
            Makes a network request. No local state is modified.
            Note: Boolean values are converted to lowercase strings for API compatibility.
        """
        # Create fresh params dict for each call (no mutable defaults)
        params = {
            "amount": amount,
            "from": from_token,
            "to": to_token,
            "anonymous": anonymous,  # Send boolean directly, not string
        }
        if use_xmr is not None:
            params["useXmr"] = use_xmr  # Send boolean directly, not string
        
        response = self._request("GET", ENDPOINT_QUOTE, params=params)
        return Quote.from_dict(response)
    
    def get_dex_quote(
        self,
        amount: Union[str, Decimal, float],
        token_id_from: str,
        token_id_to: str,
    ) -> List[DEXQuote]:
        """
        Get a quote for a DEX exchange transaction.
        
        Args:
            amount: Amount to swap (as string)
            token_id_from: ID of the token from which the swap is initiated
            token_id_to: ID of the token to which the swap is directed
            
        Returns:
            List of DEXQuote objects (may be empty if no routes available)
        
        Raises:
            APIError: If the API returns an error response (status >= 400)
            NetworkError: If a network error occurs (connection timeout, DNS failure, etc.)
            AuthenticationError: If authentication fails (401 status)
            HoudiniSwapError: For unexpected errors
        
        Edge Cases:
            - Returns empty list if no swap routes are available
            - Invalid token IDs will result in APIError
            - Amounts below minimum or above maximum will result in APIError
            - May return multiple quotes for different swap routes
        
        Performance:
            Single HTTP GET request. Response time depends on API latency and route calculation.
            Typically completes in < 2 seconds under normal conditions.
        
        Side Effects:
            Makes a network request. No local state is modified.
        """
        # Validate and convert amount
        amount_str = self._normalize_amount(amount)
        self._validate_token_id(token_id_from, "token_id_from")
        self._validate_token_id(token_id_to, "token_id_to")
        
        # Create fresh params dict for each call (no mutable defaults)
        params = {
            "amount": amount_str,
            "tokenIdFrom": token_id_from,
            "tokenIdTo": token_id_to,
        }
        
        response = self._request("GET", ENDPOINT_DEX_QUOTE, params=params)
        
        # Validate response is a list
        if not isinstance(response, list):
            raise APIError(
                f"Unexpected response type from DEX quote endpoint: expected list, got {type(response).__name__}",
                status_code=None,
                response=response,
            )
        
        # Handle empty lists gracefully
        if len(response) == 0:
            return []
        
        # Response already validated as list above
        return [DEXQuote.from_dict(quote_data) for quote_data in response]
    
    # ==================== Exchange Execution APIs ====================
    
    def post_cex_exchange(
        self,
        amount: Union[str, Decimal, float],
        from_token: str,
        to_token: str,
        address_to: str,
        anonymous: bool = False,
        receiver_tag: Optional[str] = None,
        wallet_id: Optional[str] = None,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        timezone: Optional[str] = None,
        use_xmr: Optional[bool] = None,
    ) -> ExchangeResponse:
        """
        Initiate a CEX exchange transaction.
        
        Args:
            amount: Amount to be exchanged
            from_token: Symbol of the input token (e.g., "ETH")
            to_token: Symbol of the output token (e.g., "BNB")
            address_to: Destination address
            anonymous: Whether the transaction is anonymous (default: False)
            receiver_tag: Optional receiver tag (required for some networks like XRP)
            wallet_id: User's wallet identifier (optional)
            ip: User IP address for fraud prevention (optional)
            user_agent: User browser user agent string (optional)
            timezone: User browser timezone (optional, e.g., "UTC")
            use_xmr: Use XMR for anonymous transactions (optional)
            
        Returns:
            ExchangeResponse object containing transaction details and houdini_id
        
        Raises:
            APIError: If the API returns an error response (status >= 400)
            NetworkError: If a network error occurs (connection timeout, DNS failure, etc.)
            AuthenticationError: If authentication fails (401 status)
            HoudiniSwapError: For unexpected errors
        
        Edge Cases:
            - Invalid addresses will result in APIError
            - Amounts below minimum or above maximum will result in APIError
            - Invalid token pairs will result in APIError
            - Network congestion may cause timeouts
            - Transaction may fail after submission (check status separately)
        
        Performance:
            Single HTTP POST request. Response time depends on API latency.
            Typically completes in < 2 seconds under normal conditions.
        
        Side Effects:
            Creates a transaction on the Houdini Swap platform. This is a state-changing operation.
            The transaction will be processed asynchronously. Use get_status() to check progress.
        """
        # Validate inputs
        self._validate_amount(amount, "amount")
        self._sanitize_input(from_token, "from_token")
        self._sanitize_input(to_token, "to_token")
        self._sanitize_input(address_to, "address_to")
        
        # Validate and convert amount
        amount_decimal = self._normalize_amount_to_decimal(amount)
        self._validate_amount(float(amount_decimal), "amount")
        self._sanitize_input(from_token, "from_token")
        self._sanitize_input(to_token, "to_token")
        self._sanitize_input(address_to, "address_to")
        
        json_data = {
            "amount": float(amount_decimal),  # API expects number
            "from": from_token,
            "to": to_token,
            "addressTo": address_to,
            "anonymous": anonymous,
        }
        
        if receiver_tag is not None:
            json_data["receiverTag"] = receiver_tag
        if wallet_id is not None:
            json_data["walletId"] = wallet_id
        if ip is not None:
            json_data["ip"] = ip
        if user_agent is not None:
            json_data["userAgent"] = user_agent
        if timezone is not None:
            json_data["timezone"] = timezone
        if use_xmr is not None:
            json_data["useXmr"] = use_xmr
        
        response = self._request("POST", ENDPOINT_EXCHANGE, json_data=json_data)
        return ExchangeResponse.from_dict(response)
    
    def post_dex_exchange(
        self,
        amount: Union[str, Decimal, float],
        token_id_from: str,
        token_id_to: str,
        address_from: str,
        address_to: str,
        swap: str,
        quote_id: str,
        route: RouteDTO,
    ) -> ExchangeResponse:
        """
        Initiate a DEX exchange transaction.
        
        Args:
            amount: Amount to be exchanged
            token_id_from: ID of the input token
            token_id_to: ID of the output token
            address_from: Sender's address
            address_to: Destination address
            swap: Swap method (e.g., "sw")
            quote_id: Quote identifier from get_dex_quote (must be valid and not expired)
            route: Routing and fee details (RouteDTO object from quote)
            
        Returns:
            ExchangeResponse object containing transaction details and houdini_id
        
        Raises:
            APIError: If the API returns an error response (status >= 400)
            NetworkError: If a network error occurs (connection timeout, DNS failure, etc.)
            AuthenticationError: If authentication fails (401 status)
            HoudiniSwapError: For unexpected errors
        
        Edge Cases:
            - Expired quote_id will result in APIError
            - Invalid addresses will result in APIError
            - Mismatched route/quote_id will result in APIError
            - Network congestion may cause timeouts
            - Transaction may fail after submission (check status separately)
        
        Performance:
            Single HTTP POST request. Response time depends on API latency.
            Typically completes in < 2 seconds under normal conditions.
        
        Side Effects:
            Creates a transaction on the Houdini Swap platform. This is a state-changing operation.
            The transaction will be processed asynchronously. Use get_status() to check progress.
            May require token approval first (use post_dex_approve).
        """
        # Validate and convert amount
        amount_decimal = self._normalize_amount_to_decimal(amount)
        self._validate_amount(float(amount_decimal), "amount")
        self._validate_token_id(token_id_from, "token_id_from")
        self._validate_token_id(token_id_to, "token_id_to")
        self._sanitize_input(address_from, "address_from")
        self._sanitize_input(address_to, "address_to")
        self._sanitize_input(swap, "swap")
        self._sanitize_input(quote_id, "quote_id")
        
        json_data = {
            "amount": float(amount_decimal),  # API expects number
            "tokenIdFrom": token_id_from,
            "tokenIdTo": token_id_to,
            "addressFrom": address_from,
            "addressTo": address_to,
            "swap": swap,
            "quoteId": quote_id,
            "route": route.to_dict() if isinstance(route, RouteDTO) else route,
        }
        
        response = self._request("POST", ENDPOINT_DEX_EXCHANGE, json_data=json_data)
        return ExchangeResponse.from_dict(response)
    
    # ==================== DEX Transaction Management APIs ====================
    
    def post_dex_approve(
        self,
        token_id_from: str,
        token_id_to: str,
        address_from: str,
        amount: Union[str, Decimal, float],
        swap: str,
        route: RouteDTO,
    ) -> List[DexApproveResponse]:
        """
        Initiate a token approval transaction for DEX exchange.
        
        Args:
            token_id_from: Token identifier from which the swap is initiated
            token_id_to: Token identifier to which the swap is directed
            address_from: Address from which the amount will be deducted
            amount: Amount to be approved
            swap: Swap identifier or type (e.g., "ch")
            route: Routing details (RouteDTO object from quote)
            
        Returns:
            List of DexApproveResponse objects (typically contains transaction data to sign)
        
        Raises:
            APIError: If the API returns an error response (status >= 400)
            NetworkError: If a network error occurs (connection timeout, DNS failure, etc.)
            AuthenticationError: If authentication fails (401 status)
            HoudiniSwapError: For unexpected errors
        
        Edge Cases:
            - Returns empty list if approval not needed
            - Invalid addresses will result in APIError
            - Insufficient balance will result in APIError
            - May return multiple approval transactions for complex routes
        
        Performance:
            Single HTTP POST request. Response time depends on API latency.
            Typically completes in < 2 seconds under normal conditions.
        
        Side Effects:
            Prepares approval transaction data. User must sign and broadcast the transaction
            on the blockchain. This does not automatically approve tokens.
        """
        # Validate and convert amount
        amount_decimal = self._normalize_amount_to_decimal(amount)
        self._validate_amount(float(amount_decimal), "amount")
        self._validate_token_id(token_id_from, "token_id_from")
        self._validate_token_id(token_id_to, "token_id_to")
        self._sanitize_input(address_from, "address_from")
        self._sanitize_input(swap, "swap")
        
        json_data = {
            "tokenIdFrom": token_id_from,
            "tokenIdTo": token_id_to,
            "addressFrom": address_from,
            "amount": float(amount_decimal),  # API expects number
            "swap": swap,
            "route": route.to_dict() if isinstance(route, RouteDTO) else route,
        }
        
        response = self._request("POST", ENDPOINT_DEX_APPROVE, json_data=json_data)
        
        # Validate response is a list
        if not isinstance(response, list):
            raise APIError(
                f"Unexpected response type from DEX approve endpoint: expected list, got {type(response).__name__}",
                status_code=None,
                response=response,
            )
        
        # Handle empty lists gracefully (approval not needed)
        if len(response) == 0:
            return []
        
        # Response already validated as list in _request error handling
        return [DexApproveResponse.from_dict(item) for item in response]
    
    def post_dex_confirm_tx(
        self,
        transaction_id: str,
        tx_hash: str,
    ) -> bool:
        """
        Confirm a DEX transaction.
        
        Args:
            transaction_id: Internal ID of the transaction
            tx_hash: Blockchain transaction hash
            
        Returns:
            True if confirmation was successful
        """
        # Validate inputs
        self._sanitize_input(transaction_id, "transaction_id")
        self._validate_hex_string(tx_hash, "tx_hash")
        
        json_data = {
            "id": transaction_id,
            "txHash": tx_hash,
        }
        
        response = self._request("POST", ENDPOINT_DEX_CONFIRM_TX, json_data=json_data)
        # API returns boolean true/false
        if _is_dict_response(response) and "response" in response:
            return response["response"].lower() == "true"
        return bool(response)
    
    # ==================== Status and Information APIs ====================
    
    def get_status(self, houdini_id: str) -> Status:
        """
        Get the status of an exchange transaction.
        
        Args:
            houdini_id: Unique ID of the transaction
            
        Returns:
            Status object
        """
        # Validate inputs
        self._validate_houdini_id(houdini_id)
        
        # Create fresh params dict for each call (no mutable defaults)
        params = {"id": houdini_id}
        response = self._request("GET", ENDPOINT_STATUS, params=params)
        # Add houdini_id to response if not present
        if "houdiniId" not in response:
            response["houdiniId"] = houdini_id
        return Status.from_dict(response)
    
    def get_min_max(
        self,
        from_token: str,
        to_token: str,
        anonymous: bool = False,
        cex_only: Optional[bool] = None,
    ) -> MinMax:
        """
        Get minimum and maximum exchange amounts for token pairs.
        
        Args:
            from_token: Symbol of the source token (e.g., "ETH")
            to_token: Symbol of the destination token (e.g., "BNB")
            anonymous: Whether the transaction should be anonymous (default: False)
            cex_only: Whether to limit results to centralized exchanges (optional)
            
        Returns:
            MinMax object with min and max amounts
        """
        # Validate inputs
        self._sanitize_input(from_token, "from_token")
        self._sanitize_input(to_token, "to_token")
        
        # Create fresh params dict for each call (no mutable defaults)
        params = {
            "from": from_token,
            "to": to_token,
            "anonymous": anonymous,  # Send boolean directly
        }
        if cex_only is not None:
            params["cexOnly"] = cex_only  # Send boolean directly, not string
        
        response = self._request("GET", ENDPOINT_MIN_MAX, params=params)
        return MinMax.from_list(response)
    
    def get_volume(self) -> Volume:
        """
        Get the total swap volume for HoudiniSwap.
        
        Returns:
            Volume object
        """
        response = self._request("GET", ENDPOINT_VOLUME)
        # API returns array, get first element
        if _is_list_response(response) and len(response) > 0:
            return Volume.from_dict(response[0])
        if _is_dict_response(response):
            return Volume.from_dict(response)
        raise APIError(
            f"Unexpected response type from volume endpoint: expected list or dict, got {type(response).__name__}",
            status_code=None,
            response=response,
        )
    
    def get_weekly_volume(self) -> List[WeeklyVolume]:
        """
        Get the weekly swap volume data for HoudiniSwap.
        
        Returns:
            List of WeeklyVolume objects
        """
        response = self._request("GET", ENDPOINT_WEEKLY_VOLUME)
        if _is_list_response(response):
            return [WeeklyVolume.from_dict(item) for item in response]
        if _is_dict_response(response):
            return [WeeklyVolume.from_dict(response)]
        raise APIError(
            f"Unexpected response type from weekly volume endpoint: expected list or dict, got {type(response).__name__}",
            status_code=None,
            response=response,
        )
    
    # ==================== Helper Methods ====================
    
    def iter_dex_tokens(
        self,
        chain: Optional[str] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ):
        """
        Iterator for all DEX tokens across all pages.
        
        Args:
            chain: Optional chain filter (e.g., "base")
            page_size: Number of tokens per page (default: 100)
            
        Yields:
            DEXToken objects from all pages
            
        Example:
            ```python
            for token in client.iter_dex_tokens():
                print(token.name)
            ```
        """
        page = 1
        while True:
            response = self.get_dex_tokens(page=page, page_size=page_size, chain=chain)
            if not response.tokens:
                break
            for token in response.tokens:
                yield token
            # Check if there are more pages
            total_pages = (response.count + page_size - 1) // page_size
            if page >= total_pages:
                break
            page += 1
    
    def get_all_dex_tokens(
        self,
        chain: Optional[str] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> List[DEXToken]:
        """
        Get all DEX tokens across all pages (convenience method).
        
        Args:
            chain: Optional chain filter (e.g., "base")
            page_size: Number of tokens per page (default: 100)
            
        Returns:
            List of all DEXToken objects
            
        Note:
            This loads all tokens into memory. For large token lists, use
            `iter_dex_tokens()` instead for memory efficiency.
        """
        return list(self.iter_dex_tokens(chain=chain, page_size=page_size))
    
    def wait_for_status(
        self,
        houdini_id: str,
        target_status: TransactionStatus,
        timeout: int = 300,
        poll_interval: int = 5,
    ) -> Status:
        """
        Poll until transaction reaches target status.
        
        Args:
            houdini_id: Unique ID of the transaction
            target_status: Status to wait for
            timeout: Maximum time to wait in seconds (default: 300 = 5 minutes)
            poll_interval: Time between polls in seconds (default: 5)
            
        Returns:
            Status object when target status is reached
            
        Raises:
            TimeoutError: If timeout is reached before target status
            APIError: If API returns an error
        """
        import time
        start_time = time.time()
        
        while True:
            status = self.get_status(houdini_id)
            if status.status == target_status:
                return status
            
            if time.time() - start_time > timeout:
                raise TimeoutError(
                    f"Timeout waiting for status {target_status.name}. "
                    f"Current status: {status.status.name}"
                )
            
            time.sleep(poll_interval)
    
    def poll_until_finished(
        self,
        houdini_id: str,
        timeout: int = 600,
        poll_interval: int = 5,
    ) -> Status:
        """
        Poll until transaction is finished (FINISHED, FAILED, EXPIRED, or REFUNDED).
        
        Args:
            houdini_id: Unique ID of the transaction
            timeout: Maximum time to wait in seconds (default: 600 = 10 minutes)
            poll_interval: Time between polls in seconds (default: 5)
            
        Returns:
            Final Status object
            
        Raises:
            TimeoutError: If timeout is reached
            APIError: If API returns an error
        """
        import time
        start_time = time.time()
        
        final_statuses = {
            TransactionStatus.FINISHED,
            TransactionStatus.FAILED,
            TransactionStatus.EXPIRED,
            TransactionStatus.REFUNDED,
        }
        
        while True:
            status = self.get_status(houdini_id)
            if status.status in final_statuses:
                return status
            
            if time.time() - start_time > timeout:
                raise TimeoutError(
                    f"Timeout waiting for transaction to finish. "
                    f"Current status: {status.status.name}"
                )
            
            time.sleep(poll_interval)
    
    def execute_parallel(
        self,
        requests: List[Callable[[], Any]],
        max_workers: int = 5,
    ) -> List[Any]:
        """
        Execute multiple API requests in parallel.
        
        Args:
            requests: List of callables that return API results
            max_workers: Maximum number of parallel workers (default: 5)
            
        Returns:
            List of results in the same order as requests
            
        Example:
            ```python
            results = client.execute_parallel([
                lambda: client.get_cex_tokens(),
                lambda: client.get_status("id1"),
                lambda: client.get_status("id2"),
            ])
            ```
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        results = [None] * len(requests)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(req): i for i, req in enumerate(requests)
            }
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    results[index] = e
        return results
    
    def exchange_builder(self) -> "ExchangeBuilder":
        """
        Create a new exchange builder for constructing exchange requests.
        
        Returns:
            ExchangeBuilder instance
            
        Example:
            ```python
            exchange = client.exchange_builder() \
                .cex() \
                .amount(1.0) \
                .from_token("ETH") \
                .to_token("BNB") \
                .address_to("0x...") \
                .anonymous(True) \
                .execute()
            ```
        """
        from .builder import ExchangeBuilder
        return ExchangeBuilder(self)

