# Houdini Swap Python SDK

A comprehensive Python SDK for interacting with the Houdini Swap API. This SDK provides 100% endpoint coverage for all Houdini Swap API operations.

## Features

- ✅ **100% API Coverage** - All 12 endpoints implemented
- 🔐 **Authentication** - Built-in API key/secret authentication
- 📦 **Type Safety** - Full type hints and data models
- 🛡️ **Error Handling** - Comprehensive exception handling
- 📚 **Well Documented** - Complete documentation and examples

## Installation

### Using pip

```bash
pip install houdiniswap-sdk
```

### From source

```bash
git clone https://github.com/houdiniswap/houdiniswap-sdk-python.git
cd houdiniswap-sdk-python
pip install -e .
```

## Quick Start

```python
from houdiniswap import HoudiniSwapClient

# Initialize the client
client = HoudiniSwapClient(
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# Get available CEX tokens
tokens = client.get_cex_tokens()
for token in tokens:
    print(f"{token.symbol} - {token.name}")

# Get a quote for a swap
quote = client.get_cex_quote(
    amount="1.0",
    from_token="ETH",
    to_token="BNB",
    anonymous=False
)
print(f"You'll receive {quote.amount_out} {quote.to_token}")
```

## API Endpoints

### Token Information APIs

#### Get CEX Tokens
```python
tokens = client.get_cex_tokens()
# Returns: List[Token]
```

#### Get DEX Tokens
```python
result = client.get_dex_tokens(
    page=1,
    page_size=100,
    chain="base"  # Optional
)
# Returns: DEXTokensResponse with count and tokens fields
# Note: DEX methods use token IDs, while CEX methods use token symbols
```

### Quote APIs

#### Get CEX Quote
```python
quote = client.get_cex_quote(
    amount="2.0",
    from_token="ETH",
    to_token="BNB",
    anonymous=False,
    use_xmr=False  # Optional
)
# Returns: Quote
```

#### Get DEX Quote
```python
quotes = client.get_dex_quote(
    amount="100",
    token_id_from="6689b73ec90e45f3b3e51553",
    token_id_to="6689b73ec90e45f3b3e51558"
)
# Returns: List[DEXQuote]
```

### Exchange Execution APIs

#### Post CEX Exchange
```python
exchange = client.post_cex_exchange(
    amount=1.0,
    from_token="ETH",
    to_token="BNB",
    address_to="0x000000000000000000000000000000000000dead",
    anonymous=False,
    receiver_tag=None,  # Optional
    wallet_id=None,  # Optional
    ip="0.0.0.0",  # Optional
    user_agent="Mozilla/5.0...",  # Optional
    timezone="UTC",  # Optional
    use_xmr=False  # Optional
)
# Returns: ExchangeResponse
print(f"Transaction ID: {exchange.houdini_id}")
```

#### Post DEX Exchange
```python
exchange = client.post_dex_exchange(
    amount=0.2,
    token_id_from="6689b73ec90e45f3b3e51553",
    token_id_to="6689b73ec90e45f3b3e51558",
    address_from="0x45CF73349a4895fabA18c0f51f06D79f0794898D",
    address_to="H1DiPSsBVBpDG57q5ZnxhZpRrsPQBvZfrbFQth6wyGyw",
    swap="sw",
    quote_id="66fa79723eccf00d849b48ed",
    route={...}  # RouteDTO from quote
)
# Returns: ExchangeResponse
```

### DEX Transaction Management APIs

#### Post DEX Approve
```python
approve_responses = client.post_dex_approve(
    token_id_from="6689b73ec90e45f3b3e51553",
    token_id_to="6689b73ec90e45f3b3e51558",
    address_from="0x45CF73349a4895fabA18c0f51f06D79f0794898D",
    amount=1.0,
    swap="sw",
    route={...}  # RouteDTO from quote
)
# Returns: List[DexApproveResponse]
```

#### Post DEX Confirm Transaction
```python
confirmed = client.post_dex_confirm_tx(
    transaction_id="6689b73ec90e45f3b3e51553",
    tx_hash="0x123456789abcdef..."
)
# Returns: bool
```

### Status and Information APIs

#### Get Status
```python
status = client.get_status("h9NpKm75gRnX7GWaFATwYn")
# Returns: Status

# Check status
if status.status == TransactionStatus.FINISHED:
    print("Transaction completed!")
elif status.status == TransactionStatus.FAILED:
    print("Transaction failed!")
```

#### Get Min-Max
```python
min_max = client.get_min_max(
    from_token="ETH",
    to_token="BNB",
    anonymous=False,
    cex_only=False  # Optional
)
# Returns: MinMax
print(f"Min: {min_max.min}, Max: {min_max.max}")
```

#### Get Volume
```python
volume = client.get_volume()
# Returns: Volume
print(f"Total transactions: {volume.count}")
print(f"Total volume: ${volume.total_transacted_usd:,.2f}")
```

#### Get Weekly Volume
```python
weekly_volumes = client.get_weekly_volume()
# Returns: List[WeeklyVolume]
for vol in weekly_volumes:
    print(f"Week {vol.week}/{vol.year}: {vol.volume} USD")
```

## Data Models

The SDK provides strongly-typed data models:

- `Token` - CEX token information
- `DEXToken` - DEX token information
- `Network` - Blockchain network information
- `Quote` - CEX quote information
- `DEXQuote` - DEX quote information
- `ExchangeResponse` - Exchange transaction response
- `DexApproveResponse` - DEX approval response
- `Status` - Transaction status
- `TransactionStatus` - Status enum (NEW, WAITING, CONFIRMING, etc.)
- `MinMax` - Min/Max exchange amounts
- `Volume` - Volume statistics
- `WeeklyVolume` - Weekly volume statistics

## Error Handling

The SDK provides comprehensive error handling with specific exception types for different error scenarios.

### Basic Error Handling

```python
from houdiniswap import HoudiniSwapClient
from houdiniswap.exceptions import (
    AuthenticationError,
    APIError,
    ValidationError,
    NetworkError,
    HoudiniSwapError,
)

try:
    client = HoudiniSwapClient(api_key="key", api_secret="secret")
    tokens = client.get_cex_tokens()
except AuthenticationError:
    print("Invalid API credentials")
except APIError as e:
    print(f"API error: {e.message} (Status: {e.status_code})")
except NetworkError:
    print("Network connection error")
except ValidationError:
    print("Invalid input parameters")
```

### Handling Rate Limits

The API may return a 429 status code when rate limits are exceeded. Handle this with exponential backoff:

```python
import time
from houdiniswap import HoudiniSwapClient
from houdiniswap.exceptions import APIError

client = HoudiniSwapClient(api_key="key", api_secret="secret")

def get_tokens_with_retry(max_retries=3, backoff_factor=2):
    """Get tokens with automatic retry on rate limit errors."""
    for attempt in range(max_retries):
        try:
            return client.get_cex_tokens()
        except APIError as e:
            if e.status_code == 429:  # Rate limit exceeded
                if attempt < max_retries - 1:
                    wait_time = backoff_factor ** attempt
                    print(f"Rate limited. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception("Rate limit exceeded after multiple retries")
            else:
                raise  # Re-raise non-rate-limit errors
    return None

tokens = get_tokens_with_retry()
```

### Retrying Failed Requests

For transient network errors, implement retry logic:

```python
import time
from houdiniswap import HoudiniSwapClient
from houdiniswap.exceptions import NetworkError, APIError

client = HoudiniSwapClient(api_key="key", api_secret="secret", timeout=30)

def retry_request(func, max_retries=3, retry_delay=1):
    """Retry a function call on network errors."""
    for attempt in range(max_retries):
        try:
            return func()
        except NetworkError as e:
            if attempt < max_retries - 1:
                print(f"Network error (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                continue
            else:
                raise
        except APIError as e:
            # Don't retry on API errors (4xx, 5xx) unless it's a server error (5xx)
            if e.status_code >= 500 and attempt < max_retries - 1:
                print(f"Server error (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(retry_delay * (attempt + 1))
                continue
            else:
                raise
    return None

# Usage
try:
    quote = retry_request(
        lambda: client.get_cex_quote(
            amount="1.0",
            from_token="ETH",
            to_token="BNB"
        )
    )
    print(f"Quote received: {quote.amount_out}")
except Exception as e:
    print(f"Failed after retries: {e}")
```

### Input Validation

Validate inputs before making API calls to provide better error messages:

```python
from houdiniswap import HoudiniSwapClient
from houdiniswap.exceptions import ValidationError, APIError

def validate_exchange_params(amount, from_token, to_token, address_to):
    """Validate exchange parameters before API call."""
    errors = []
    
    if not amount or amount <= 0:
        errors.append("Amount must be greater than 0")
    
    if not from_token or not isinstance(from_token, str):
        errors.append("from_token must be a non-empty string")
    
    if not to_token or not isinstance(to_token, str):
        errors.append("to_token must be a non-empty string")
    
    if not address_to or not isinstance(address_to, str):
        errors.append("address_to must be a non-empty string")
    
    if len(address_to) < 10:  # Basic address validation
        errors.append("address_to appears to be invalid (too short)")
    
    if errors:
        raise ValidationError(f"Validation failed: {', '.join(errors)}")
    
    return True

client = HoudiniSwapClient(api_key="key", api_secret="secret")

try:
    # Validate before API call
    validate_exchange_params(
        amount=1.0,
        from_token="ETH",
        to_token="BNB",
        address_to="0x000000000000000000000000000000000000dead"
    )
    
    # Proceed with exchange
    exchange = client.post_cex_exchange(
        amount=1.0,
        from_token="ETH",
        to_token="BNB",
        address_to="0x000000000000000000000000000000000000dead"
    )
    print(f"Exchange initiated: {exchange.houdini_id}")
    
except ValidationError as e:
    print(f"Input validation error: {e}")
except APIError as e:
    print(f"API error: {e.message} (Status: {e.status_code})")
    if e.response:
        print(f"API response: {e.response}")
```

### Error Recovery and Transaction Status Monitoring

Monitor transaction status and handle failures gracefully:

```python
import time
from houdiniswap import HoudiniSwapClient
from houdiniswap.exceptions import APIError, NetworkError
from houdiniswap.models import TransactionStatus

client = HoudiniSwapClient(api_key="key", api_secret="secret")

def monitor_transaction(houdini_id, max_wait_time=300, check_interval=10):
    """Monitor transaction status with error recovery."""
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            status = client.get_status(houdini_id)
            
            if status.status == TransactionStatus.FINISHED:
                print(f"Transaction {houdini_id} completed successfully!")
                return status
            
            elif status.status == TransactionStatus.FAILED:
                print(f"Transaction {houdini_id} failed")
                # Check if there's error information in the status
                if hasattr(status, 'error') and status.error:
                    print(f"Error: {status.error}")
                return status
            
            elif status.status == TransactionStatus.EXPIRED:
                print(f"Transaction {houdini_id} expired")
                return status
            
            elif status.status == TransactionStatus.REFUNDED:
                print(f"Transaction {houdini_id} was refunded")
                return status
            
            else:
                print(f"Transaction {houdini_id} status: {status.status.name}")
                time.sleep(check_interval)
                
        except NetworkError as e:
            print(f"Network error while checking status: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)
            continue
            
        except APIError as e:
            if e.status_code == 404:
                print(f"Transaction {houdini_id} not found")
                return None
            else:
                print(f"API error: {e.message}")
                raise
    
    print(f"Transaction {houdini_id} monitoring timed out after {max_wait_time} seconds")
    return None

# Usage
try:
    exchange = client.post_cex_exchange(
        amount=1.0,
        from_token="ETH",
        to_token="BNB",
        address_to="0x000000000000000000000000000000000000dead"
    )
    
    final_status = monitor_transaction(exchange.houdini_id)
    
except Exception as e:
    print(f"Exchange failed: {e}")
```

### Comprehensive Error Handling Example

Combine all error handling patterns:

```python
from houdiniswap import HoudiniSwapClient
from houdiniswap.exceptions import (
    AuthenticationError,
    APIError,
    ValidationError,
    NetworkError,
    HoudiniSwapError,
)
import time

def safe_exchange(client, amount, from_token, to_token, address_to, max_retries=3):
    """Perform an exchange with comprehensive error handling."""
    
    # Step 1: Validate inputs
    try:
        if amount <= 0:
            raise ValidationError("Amount must be greater than 0")
        if not all([from_token, to_token, address_to]):
            raise ValidationError("All parameters are required")
    except ValidationError as e:
        print(f"Validation error: {e}")
        return None
    
    # Step 2: Get quote with retry
    quote = None
    for attempt in range(max_retries):
        try:
            quote = client.get_cex_quote(
                amount=str(amount),
                from_token=from_token,
                to_token=to_token
            )
            break
        except APIError as e:
            if e.status_code == 429:  # Rate limit
                wait = 2 ** attempt
                print(f"Rate limited. Waiting {wait}s...")
                time.sleep(wait)
                continue
            elif e.status_code >= 500:  # Server error
                if attempt < max_retries - 1:
                    print(f"Server error. Retrying...")
                    time.sleep(1)
                    continue
            print(f"API error getting quote: {e.message}")
            return None
        except NetworkError as e:
            if attempt < max_retries - 1:
                print(f"Network error. Retrying...")
                time.sleep(1)
                continue
            print(f"Network error: {e}")
            return None
    
    if not quote:
        print("Failed to get quote after retries")
        return None
    
    print(f"Quote: {quote.amount_in} {from_token} -> {quote.amount_out} {to_token}")
    
    # Step 3: Execute exchange
    try:
        exchange = client.post_cex_exchange(
            amount=amount,
            from_token=from_token,
            to_token=to_token,
            address_to=address_to
        )
        print(f"Exchange initiated: {exchange.houdini_id}")
        return exchange
    except APIError as e:
        print(f"Exchange failed: {e.message} (Status: {e.status_code})")
        if e.response:
            print(f"Details: {e.response}")
        return None
    except NetworkError as e:
        print(f"Network error during exchange: {e}")
        return None

# Usage
try:
    client = HoudiniSwapClient(api_key="key", api_secret="secret")
    exchange = safe_exchange(
        client=client,
        amount=1.0,
        from_token="ETH",
        to_token="BNB",
        address_to="0x000000000000000000000000000000000000dead"
    )
    
    if exchange:
        print(f"Success! Transaction ID: {exchange.houdini_id}")
    
except AuthenticationError:
    print("Invalid API credentials")
except HoudiniSwapError as e:
    print(f"Unexpected error: {e}")
```

## Complete Example: CEX Exchange Flow

```python
from houdiniswap import HoudiniSwapClient
from houdiniswap.models import TransactionStatus

# Initialize client
client = HoudiniSwapClient(
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# 1. Get available tokens
tokens = client.get_cex_tokens()
print(f"Available tokens: {len(tokens)}")

# 2. Get min/max limits
min_max = client.get_min_max(
    from_token="ETH",
    to_token="BNB",
    anonymous=False
)
print(f"Exchange limits: {min_max.min} - {min_max.max}")

# 3. Get a quote
quote = client.get_cex_quote(
    amount="1.0",
    from_token="ETH",
    to_token="BNB",
    anonymous=False
)
print(f"Quote: {quote.amount_in} ETH -> {quote.amount_out} BNB")

# 4. Execute the exchange
exchange = client.post_cex_exchange(
    amount=1.0,
    from_token="ETH",
    to_token="BNB",
    address_to="0x000000000000000000000000000000000000dead",
    anonymous=False,
    timezone="UTC"
)
print(f"Transaction ID: {exchange.houdini_id}")

# 5. Check status
import time
while True:
    status = client.get_status(exchange.houdini_id)
    print(f"Status: {status.status.name}")
    
    if status.status == TransactionStatus.FINISHED:
        print("Exchange completed!")
        break
    elif status.status in [TransactionStatus.FAILED, TransactionStatus.EXPIRED]:
        print("Exchange failed or expired")
        break
    
    time.sleep(10)  # Wait 10 seconds before checking again
```

## Complete Example: DEX Exchange Flow

```python
from houdiniswap import HoudiniSwapClient

client = HoudiniSwapClient(
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# 1. Get DEX tokens
dex_tokens = client.get_dex_tokens(chain="base")
print(f"Available DEX tokens: {dex_tokens['count']}")

# 2. Get DEX quote
quotes = client.get_dex_quote(
    amount="100",
    token_id_from="6689b73ec90e45f3b3e51553",
    token_id_to="6689b73ec90e45f3b3e51558"
)
quote = quotes[0]  # Use first quote
print(f"Quote ID: {quote.quote_id}")
print(f"Amount out: {quote.amount_out}")

# 3. Approve token spending
approve_responses = client.post_dex_approve(
    token_id_from="6689b73ec90e45f3b3e51553",
    token_id_to="6689b73ec90e45f3b3e51558",
    address_from="0x45CF73349a4895fabA18c0f51f06D79f0794898D",
    amount=100.0,
    swap=quote.swap,
    route=quote.raw  # Use route from quote
)
print("Approval transaction data:", approve_responses[0].data)

# 4. Execute DEX exchange (after approval transaction is confirmed)
exchange = client.post_dex_exchange(
    amount=100.0,
    token_id_from="6689b73ec90e45f3b3e51553",
    token_id_to="6689b73ec90e45f3b3e51558",
    address_from="0x45CF73349a4895fabA18c0f51f06D79f0794898D",
    address_to="H1DiPSsBVBpDG57q5ZnxhZpRrsPQBvZfrbFQth6wyGyw",
    swap=quote.swap,
    quote_id=quote.quote_id,
    route=quote.raw
)
print(f"Transaction ID: {exchange.houdini_id}")

# 5. Confirm transaction (after blockchain confirmation)
confirmed = client.post_dex_confirm_tx(
    transaction_id=exchange.houdini_id,
    tx_hash="0x123456789abcdef..."
)
print(f"Transaction confirmed: {confirmed}")
```

## Configuration

### Custom Base URL

```python
client = HoudiniSwapClient(
    api_key="your_api_key",
    api_secret="your_api_secret",
    base_url="https://custom-api-url.com"  # Optional
)
```

### Request Timeout

```python
client = HoudiniSwapClient(
    api_key="your_api_key",
    api_secret="your_api_secret",
    timeout=60  # 60 seconds (default: 30)
)
```

## Requirements

- Python 3.8+
- requests >= 2.31.0

## License

**Code:** This project is licensed under the GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later). See [LICENSE](LICENSE) for details.

**Documentation:** All documentation and non-code content is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License (CC-BY-SA 4.0). See [LICENSE-DOCS](LICENSE-DOCS) for details.

## Support

For API documentation, visit: https://docs.houdiniswap.com

For issues and contributions, please visit the GitHub repository.
