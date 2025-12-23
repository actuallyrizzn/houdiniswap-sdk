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
# Returns: Dict with 'count' and 'tokens' (List[DEXToken])
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

The SDK provides comprehensive error handling:

```python
from houdiniswap import HoudiniSwapClient
from houdiniswap.exceptions import (
    AuthenticationError,
    APIError,
    ValidationError,
    NetworkError,
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

MIT License

## Support

For API documentation, visit: https://docs.houdiniswap.com

For issues and contributions, please visit the GitHub repository.
