# API Reference

Complete API reference for the Houdini Swap Python SDK.

## Table of Contents

- [HoudiniSwapClient](#houdiniswapclient)
- [Data Models](#data-models)
- [Exceptions](#exceptions)

## HoudiniSwapClient

Main client class for interacting with the Houdini Swap API.

### Constructor

```python
HoudiniSwapClient(
    api_key: str,
    api_secret: str,
    base_url: Optional[str] = None,
    timeout: int = 30
)
```

**Parameters:**
- `api_key` (str): Your Houdini Swap API key (required)
- `api_secret` (str): Your Houdini Swap API secret (required)
- `base_url` (Optional[str]): Custom base URL (defaults to production API)
- `timeout` (int): Request timeout in seconds (default: 30)

**Raises:**
- `ValidationError`: If api_key or api_secret is empty or None

**Example:**
```python
from houdiniswap import HoudiniSwapClient

client = HoudiniSwapClient(
    api_key="your_api_key",
    api_secret="your_api_secret",
    timeout=60
)
```

---

### Token Information Methods

#### get_cex_tokens

```python
get_cex_tokens() -> List[Token]
```

Get a list of tokens supported by Houdini Swap for CEX exchanges.

**Returns:**
- `List[Token]`: List of Token objects

**Raises:**
- `APIError`: If the API returns an error response
- `NetworkError`: If a network error occurs
- `AuthenticationError`: If authentication fails
- `HoudiniSwapError`: For unexpected errors

**Example:**
```python
tokens = client.get_cex_tokens()
for token in tokens:
    print(f"{token.symbol}: {token.name}")
```

---

#### get_dex_tokens

```python
get_dex_tokens(
    page: int = 1,
    page_size: int = 100,
    chain: Optional[str] = None
) -> Dict[str, Any]
```

Get a paginated list of tokens supported for DEX exchanges.

**Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Number of tokens per page (default: 100)
- `chain` (Optional[str]): Chain short name filter (e.g., "base")

**Returns:**
- `Dict[str, Any]`: Dictionary with:
  - `count` (int): Total number of tokens
  - `tokens` (List[DEXToken]): List of DEXToken objects

**Raises:**
- `APIError`: If the API returns an error response
- `NetworkError`: If a network error occurs
- `AuthenticationError`: If authentication fails
- `HoudiniSwapError`: For unexpected errors

**Example:**
```python
result = client.get_dex_tokens(page=1, page_size=50, chain="base")
print(f"Total tokens: {result['count']}")
for token in result['tokens']:
    print(f"{token.symbol}: {token.name}")
```

---

### Quote Methods

#### get_cex_quote

```python
get_cex_quote(
    amount: str,
    from_token: str,
    to_token: str,
    anonymous: bool = False,
    use_xmr: Optional[bool] = None
) -> Quote
```

Get a quote for a CEX exchange transaction.

**Parameters:**
- `amount` (str): The amount to transfer (as string)
- `from_token` (str): TokenID of source currency (e.g., "BNB")
- `to_token` (str): TokenID of destination currency (e.g., "ETH")
- `anonymous` (bool): Whether to use anonymous flow (default: False)
- `use_xmr` (Optional[bool]): Use XMR for anonymous transactions

**Returns:**
- `Quote`: Quote object with exchange rate and estimated output

**Raises:**
- `APIError`: If the API returns an error response
- `NetworkError`: If a network error occurs
- `AuthenticationError`: If authentication fails
- `HoudiniSwapError`: For unexpected errors

**Example:**
```python
quote = client.get_cex_quote(
    amount="1.0",
    from_token="ETH",
    to_token="BNB",
    anonymous=False
)
print(f"Exchange rate: {quote.amount_in} ETH -> {quote.amount_out} BNB")
```

---

#### get_dex_quote

```python
get_dex_quote(
    amount: str,
    token_id_from: str,
    token_id_to: str
) -> List[DEXQuote]
```

Get quotes for a DEX exchange transaction.

**Parameters:**
- `amount` (str): Amount to swap (as string)
- `token_id_from` (str): ID of the token from which the swap is initiated
- `token_id_to` (str): ID of the token to which the swap is directed

**Returns:**
- `List[DEXQuote]`: List of DEXQuote objects (may be empty if no routes available)

**Raises:**
- `APIError`: If the API returns an error response
- `NetworkError`: If a network error occurs
- `AuthenticationError`: If authentication fails
- `HoudiniSwapError`: For unexpected errors

**Example:**
```python
quotes = client.get_dex_quote(
    amount="100",
    token_id_from="6689b73ec90e45f3b3e51553",
    token_id_to="6689b73ec90e45f3b3e51558"
)
if quotes:
    quote = quotes[0]
    print(f"Quote ID: {quote.quote_id}")
    print(f"Amount out: {quote.amount_out}")
```

---

### Exchange Execution Methods

#### post_cex_exchange

```python
post_cex_exchange(
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
    use_xmr: Optional[bool] = None
) -> ExchangeResponse
```

Initiate a CEX exchange transaction.

**Parameters:**
- `amount` (float): Amount to be exchanged
- `from_token` (str): Symbol of the input token (e.g., "ETH")
- `to_token` (str): Symbol of the output token (e.g., "BNB")
- `address_to` (str): Destination address
- `anonymous` (bool): Whether the transaction is anonymous (default: False)
- `receiver_tag` (Optional[str]): Receiver tag (required for some networks like XRP)
- `wallet_id` (Optional[str]): User's wallet identifier
- `ip` (Optional[str]): User IP address for fraud prevention
- `user_agent` (Optional[str]): User browser user agent string
- `timezone` (Optional[str]): User browser timezone (e.g., "UTC")
- `use_xmr` (Optional[bool]): Use XMR for anonymous transactions

**Returns:**
- `ExchangeResponse`: ExchangeResponse object containing transaction details and houdini_id

**Raises:**
- `APIError`: If the API returns an error response
- `NetworkError`: If a network error occurs
- `AuthenticationError`: If authentication fails
- `HoudiniSwapError`: For unexpected errors

**Example:**
```python
exchange = client.post_cex_exchange(
    amount=1.0,
    from_token="ETH",
    to_token="BNB",
    address_to="0x000000000000000000000000000000000000dead",
    anonymous=False,
    timezone="UTC"
)
print(f"Transaction ID: {exchange.houdini_id}")
```

---

#### post_dex_exchange

```python
post_dex_exchange(
    amount: float,
    token_id_from: str,
    token_id_to: str,
    address_from: str,
    address_to: str,
    swap: str,
    quote_id: str,
    route: Dict[str, Any]
) -> ExchangeResponse
```

Initiate a DEX exchange transaction.

**Parameters:**
- `amount` (float): Amount to be exchanged
- `token_id_from` (str): ID of the input token
- `token_id_to` (str): ID of the output token
- `address_from` (str): Sender's address
- `address_to` (str): Destination address
- `swap` (str): Swap method (e.g., "sw")
- `quote_id` (str): Quote identifier from get_dex_quote (must be valid and not expired)
- `route` (Dict[str, Any]): Routing and fee details (RouteDTO object from quote)

**Returns:**
- `ExchangeResponse`: ExchangeResponse object containing transaction details and houdini_id

**Raises:**
- `APIError`: If the API returns an error response
- `NetworkError`: If a network error occurs
- `AuthenticationError`: If authentication fails
- `HoudiniSwapError`: For unexpected errors

**Example:**
```python
exchange = client.post_dex_exchange(
    amount=100.0,
    token_id_from="6689b73ec90e45f3b3e51553",
    token_id_to="6689b73ec90e45f3b3e51558",
    address_from="0x45CF73349a4895fabA18c0f51f06D79f0794898D",
    address_to="H1DiPSsBVBpDG57q5ZnxhZpRrsPQBvZfrbFQth6wyGyw",
    swap="sw",
    quote_id="66fa79723eccf00d849b48ed",
    route=quote.raw
)
```

---

### DEX Transaction Management Methods

#### post_dex_approve

```python
post_dex_approve(
    token_id_from: str,
    token_id_to: str,
    address_from: str,
    amount: float,
    swap: str,
    route: Dict[str, Any]
) -> List[DexApproveResponse]
```

Initiate a token approval transaction for DEX exchange.

**Parameters:**
- `token_id_from` (str): Token identifier from which the swap is initiated
- `token_id_to` (str): Token identifier to which the swap is directed
- `address_from` (str): Address from which the amount will be deducted
- `amount` (float): Amount to be approved
- `swap` (str): Swap identifier or type (e.g., "ch")
- `route` (Dict[str, Any]): Routing details (RouteDTO object from quote)

**Returns:**
- `List[DexApproveResponse]`: List of DexApproveResponse objects (typically contains transaction data to sign)

**Raises:**
- `APIError`: If the API returns an error response
- `NetworkError`: If a network error occurs
- `AuthenticationError`: If authentication fails
- `HoudiniSwapError`: For unexpected errors

**Example:**
```python
approve_responses = client.post_dex_approve(
    token_id_from="6689b73ec90e45f3b3e51553",
    token_id_to="6689b73ec90e45f3b3e51558",
    address_from="0x45CF73349a4895fabA18c0f51f06D79f0794898D",
    amount=100.0,
    swap="sw",
    route=quote.raw
)
print("Approval transaction data:", approve_responses[0].data)
```

---

#### post_dex_confirm_tx

```python
post_dex_confirm_tx(
    transaction_id: str,
    tx_hash: str
) -> bool
```

Confirm a DEX transaction.

**Parameters:**
- `transaction_id` (str): Transaction identifier (from DexApproveResponse)
- `tx_hash` (str): Transaction hash from blockchain (must be valid hex string)

**Returns:**
- `bool`: True if confirmed successfully, False otherwise

**Raises:**
- `APIError`: If the API returns an error response
- `NetworkError`: If a network error occurs
- `AuthenticationError`: If authentication fails
- `HoudiniSwapError`: For unexpected errors

**Example:**
```python
confirmed = client.post_dex_confirm_tx(
    transaction_id="6689b73ec90e45f3b3e51553",
    tx_hash="0x123456789abcdef..."
)
if confirmed:
    print("Transaction confirmed successfully")
```

---

### Status and Information Methods

#### get_status

```python
get_status(houdini_id: str) -> Status
```

Get the status of an exchange transaction.

**Parameters:**
- `houdini_id` (str): The Houdini transaction ID (from ExchangeResponse)

**Returns:**
- `Status`: Status object containing current transaction state and details

**Raises:**
- `APIError`: If the API returns an error response
- `NetworkError`: If a network error occurs
- `AuthenticationError`: If authentication fails
- `HoudiniSwapError`: For unexpected errors

**Example:**
```python
status = client.get_status("h9NpKm75gRnX7GWaFATwYn")
print(f"Status: {status.status.name}")
if status.status == TransactionStatus.FINISHED:
    print("Transaction completed!")
```

---

#### get_min_max

```python
get_min_max(
    from_token: str,
    to_token: str,
    anonymous: bool = False,
    cex_only: Optional[bool] = None
) -> MinMax
```

Get minimum and maximum exchange amounts for a token pair.

**Parameters:**
- `from_token` (str): Source token symbol (e.g., "ETH")
- `to_token` (str): Destination token symbol (e.g., "BNB")
- `anonymous` (bool): Whether to use anonymous flow (default: False)
- `cex_only` (Optional[bool]): Whether to use CEX only

**Returns:**
- `MinMax`: MinMax object with min and max amounts for the token pair

**Raises:**
- `APIError`: If the API returns an error response
- `NetworkError`: If a network error occurs
- `AuthenticationError`: If authentication fails
- `HoudiniSwapError`: For unexpected errors

**Example:**
```python
min_max = client.get_min_max(
    from_token="ETH",
    to_token="BNB",
    anonymous=False
)
print(f"Min: {min_max.min}, Max: {min_max.max}")
```

---

#### get_volume

```python
get_volume() -> Volume
```

Get total volume statistics.

**Returns:**
- `Volume`: Volume object containing total transaction volume in USD

**Raises:**
- `APIError`: If the API returns an error response
- `NetworkError`: If a network error occurs
- `AuthenticationError`: If authentication fails
- `HoudiniSwapError`: For unexpected errors

**Example:**
```python
volume = client.get_volume()
print(f"Total transactions: {volume.count}")
print(f"Total volume: ${volume.total_transacted_usd:,.2f}")
```

---

#### get_weekly_volume

```python
get_weekly_volume() -> List[WeeklyVolume]
```

Get weekly volume statistics.

**Returns:**
- `List[WeeklyVolume]`: List of WeeklyVolume objects (one per week, typically last 52 weeks)

**Raises:**
- `APIError`: If the API returns an error response
- `NetworkError`: If a network error occurs
- `AuthenticationError`: If authentication fails
- `HoudiniSwapError`: For unexpected errors

**Example:**
```python
weekly_volumes = client.get_weekly_volume()
for vol in weekly_volumes:
    print(f"Week {vol.week}/{vol.year}: {vol.volume} USD")
```

---

## Data Models

### Token

CEX token information.

**Fields:**
- `id` (str): Token identifier
- `name` (str): Token name
- `symbol` (str): Token symbol
- `network` (Network): Network information
- `display_name` (Optional[str]): Display name
- `icon` (Optional[str]): Icon URL
- `keyword` (Optional[str]): Search keyword
- `color` (Optional[str]): Token color
- `chain` (Optional[int]): Chain ID
- `address` (Optional[str]): Token contract address
- `has_markup` (Optional[bool]): Whether token has markup
- `network_priority` (Optional[int]): Network priority
- `has_fixed` (Optional[bool]): Whether token has fixed rate
- `has_fixed_reverse` (Optional[bool]): Whether token has fixed reverse rate

### DEXToken

DEX token information.

**Fields:**
- `id` (str): Token identifier
- `name` (str): Token name
- `symbol` (str): Token symbol
- `chain` (str): Chain identifier
- `address` (str): Token contract address
- `decimals` (int): Token decimals
- `icon` (Optional[str]): Icon URL

### Quote

CEX quote information.

**Fields:**
- `amount_in` (float): Input amount
- `amount_out` (float): Output amount
- `from_token` (str): Source token symbol
- `to_token` (str): Destination token symbol
- `rate` (float): Exchange rate
- `fee` (float): Transaction fee
- `network_fee` (Optional[float]): Network fee

### DEXQuote

DEX quote information.

**Fields:**
- `quote_id` (str): Quote identifier
- `amount_in` (float): Input amount
- `amount_out` (float): Output amount
- `swap` (str): Swap method
- `raw` (Dict[str, Any]): Raw route data

### ExchangeResponse

Exchange transaction response.

**Fields:**
- `houdini_id` (str): Houdini transaction ID
- `in_amount` (float): Input amount
- `out_amount` (float): Output amount
- `in_amount_usd` (float): Input amount in USD
- `from_token` (str): Source token
- `to_token` (str): Destination token
- `quote` (Optional[Dict[str, Any]]): Quote information

### Status

Transaction status information.

**Fields:**
- `houdini_id` (str): Houdini transaction ID
- `status` (TransactionStatus): Transaction status enum
- `in_amount` (Optional[float]): Input amount
- `out_amount` (Optional[float]): Output amount
- `from_token` (Optional[str]): Source token
- `to_token` (Optional[str]): Destination token

### TransactionStatus

Transaction status enum.

**Values:**
- `NEW = -1`: New transaction
- `WAITING = 0`: Waiting
- `CONFIRMING = 1`: Confirming
- `EXCHANGING = 2`: Exchanging
- `ANONYMIZING = 3`: Anonymizing
- `FINISHED = 4`: Finished
- `EXPIRED = 5`: Expired
- `FAILED = 6`: Failed
- `REFUNDED = 7`: Refunded
- `DELETED = 8`: Deleted

---

## Exceptions

### HoudiniSwapError

Base exception for all Houdini Swap SDK errors.

### AuthenticationError

Raised when authentication fails (401 status).

### APIError

Raised when the API returns an error response.

**Attributes:**
- `status_code` (int): HTTP status code
- `response` (Optional[dict]): API error response

### ValidationError

Raised when input validation fails.

### NetworkError

Raised when a network error occurs (connection timeout, DNS failure, etc.).

