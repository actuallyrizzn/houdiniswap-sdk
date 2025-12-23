"""Main client for Houdini Swap API."""

import requests
from typing import Optional, List, Dict, Any, TypeGuard
from urllib.parse import urljoin

from .constants import (
    DEFAULT_TIMEOUT,
    DEFAULT_PAGE_SIZE,
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_UNAUTHORIZED,
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
        Creates and maintains an HTTP session. Credentials are stored in instance
        attributes (consider security implications).
    """
    
    BASE_URL = "https://api-partner.houdiniswap.com"
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        """
        Initialize the Houdini Swap client.
        
        Args:
            api_key: Your Houdini Swap API key
            api_secret: Your Houdini Swap API secret
            base_url: Optional custom base URL (defaults to production)
            timeout: Request timeout in seconds (default: 30, see DEFAULT_TIMEOUT constant)
        
        Raises:
            ValidationError: If api_key or api_secret is empty or None
        
        Edge Cases:
            - Empty strings are treated as invalid credentials
            - None values for api_key or api_secret will raise ValidationError
        
        Side Effects:
            Creates a requests.Session() object and stores credentials as instance attributes
        """
        if not api_key or not api_secret:
            raise ValidationError(ERROR_INVALID_CREDENTIALS)
        
        # Validate credentials format
        self._validate_credentials(api_key, api_secret)
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout or DEFAULT_TIMEOUT
        
        # Create session with authentication
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"{api_key}:{api_secret}",
            "Content-Type": "application/json",
        })
    
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
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
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
            NetworkError: If a network error occurs
            AuthenticationError: If authentication fails
        """
        url = urljoin(self.base_url, endpoint.lstrip("/"))
        
        # Defensive copy of params to prevent mutation of caller's dict
        # This ensures safe concurrent usage and prevents accidental side effects
        safe_params = dict(params) if params else None
        safe_json_data = dict(json_data) if json_data else None
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=safe_params,
                json=safe_json_data,
                timeout=self.timeout,
            )
            
            # Handle authentication errors
            if response.status_code == HTTP_STATUS_UNAUTHORIZED:
                raise AuthenticationError(ERROR_AUTHENTICATION_FAILED)
            
            # Handle other HTTP errors
            if response.status_code >= HTTP_STATUS_BAD_REQUEST:
                error_data = None
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", f"API error: {response.status_code}")
                except ValueError:
                    # JSON parsing failed - include raw response text (limit length)
                    error_message = f"API error: {response.status_code} - {response.text[:500]}"
                
                raise APIError(
                    error_message,
                    status_code=response.status_code,
                    response=error_data,
                )
            
            # Parse JSON response
            try:
                return response.json()
            except ValueError:
                # Some endpoints return non-JSON (e.g., boolean true)
                return {"response": response.text}
                
        except requests.exceptions.RequestException as e:
            raise NetworkError(ERROR_NETWORK.format(str(e))) from e
        except (APIError, AuthenticationError):
            raise
        except Exception as e:
            raise HoudiniSwapError(ERROR_UNEXPECTED.format(str(e))) from e
    
    def __enter__(self) -> "HoudiniSwapClient":
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager and close session."""
        self.close()
    
    def close(self) -> None:
        """Close the HTTP session and release resources."""
        if hasattr(self, 'session') and self.session:
            self.session.close()
    
    # ==================== Token Information APIs ====================
    
    def get_cex_tokens(self) -> List[Token]:
        """
        Get a list of tokens supported by Houdini Swap for CEX exchanges.
        
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
        
        Performance:
            Single HTTP GET request. Response time depends on API latency.
            Typically completes in < 1 second under normal conditions.
        
        Side Effects:
            Makes a network request. No local state is modified.
        """
        response = self._request("GET", ENDPOINT_TOKENS)
        return [Token.from_dict(token_data) for token_data in response]
    
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
        # Create fresh params dict for each call (no mutable defaults)
        # This pattern ensures thread-safety and prevents accidental mutations
        params = {
            "page": page,
            "pageSize": page_size,
        }
        if chain:
            params["chain"] = chain
        
        response = self._request("GET", ENDPOINT_DEX_TOKENS, params=params)
        return DEXTokensResponse(
            count=response.get("count", 0),
            tokens=[DEXToken.from_dict(token_data) for token_data in response.get("tokens", [])],
        )
    
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
            "anonymous": str(anonymous).lower(),
        }
        if use_xmr is not None:
            params["useXmr"] = str(use_xmr).lower()
        
        response = self._request("GET", ENDPOINT_QUOTE, params=params)
        return Quote.from_dict(response)
    
    def get_dex_quote(
        self,
        amount: str,
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
        # Create fresh params dict for each call (no mutable defaults)
        params = {
            "amount": amount,
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
        
        return [DEXQuote.from_dict(quote_data) for quote_data in response]
    
    # ==================== Exchange Execution APIs ====================
    
    def post_cex_exchange(
        self,
        amount: float,
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
        json_data = {
            "amount": amount,
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
        amount: float,
        token_id_from: str,
        token_id_to: str,
        address_from: str,
        address_to: str,
        swap: str,
        quote_id: str,
        route: Dict[str, Any],
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
        json_data = {
            "amount": amount,
            "tokenIdFrom": token_id_from,
            "tokenIdTo": token_id_to,
            "addressFrom": address_from,
            "addressTo": address_to,
            "swap": swap,
            "quoteId": quote_id,
            "route": route,
        }
        
        response = self._request("POST", ENDPOINT_DEX_EXCHANGE, json_data=json_data)
        return ExchangeResponse.from_dict(response)
    
    # ==================== DEX Transaction Management APIs ====================
    
    def post_dex_approve(
        self,
        token_id_from: str,
        token_id_to: str,
        address_from: str,
        amount: float,
        swap: str,
        route: Dict[str, Any],
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
        json_data = {
            "tokenIdFrom": token_id_from,
            "tokenIdTo": token_id_to,
            "addressFrom": address_from,
            "amount": amount,
            "swap": swap,
            "route": route,
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
        # Create fresh params dict for each call (no mutable defaults)
        params = {
            "from": from_token,
            "to": to_token,
            "anonymous": self._bool_to_str(anonymous),
        }
        if cex_only is not None:
            params["cexOnly"] = self._bool_to_str(cex_only)
        
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

