"""Basic usage examples for Houdini Swap SDK."""

from houdiniswap import HoudiniSwapClient
from houdiniswap.models import TransactionStatus

# Initialize the client
# Replace with your actual API credentials
client = HoudiniSwapClient(
    api_key="your_api_key_here",
    api_secret="your_api_secret_here"
)


def example_get_tokens():
    """Example: Get available CEX tokens."""
    print("=== Getting CEX Tokens ===")
    tokens = client.get_cex_tokens()
    print(f"Found {len(tokens)} tokens")
    for token in tokens[:5]:  # Show first 5
        print(f"  - {token.symbol}: {token.name} ({token.network.short_name})")


def example_get_dex_tokens():
    """Example: Get DEX tokens."""
    print("\n=== Getting DEX Tokens ===")
    result = client.get_dex_tokens(page=1, page_size=10, chain="base")
    print(f"Total: {result['count']} tokens")
    for token in result['tokens'][:5]:  # Show first 5
        print(f"  - {token.symbol}: {token.name} on {token.chain}")


def example_get_quote():
    """Example: Get a quote for a swap."""
    print("\n=== Getting CEX Quote ===")
    quote = client.get_cex_quote(
        amount="1.0",
        from_token="ETH",
        to_token="BNB",
        anonymous=False
    )
    print(f"Quote: {quote.amount_in} ETH -> {quote.amount_out} BNB")
    print(f"Min: {quote.min}, Max: {quote.max}")
    print(f"Duration: {quote.duration} minutes")


def example_get_min_max():
    """Example: Get min/max exchange amounts."""
    print("\n=== Getting Min-Max ===")
    min_max = client.get_min_max(
        from_token="ETH",
        to_token="BNB",
        anonymous=False
    )
    print(f"Min: {min_max.min}")
    print(f"Max: {min_max.max}")


def example_get_volume():
    """Example: Get volume statistics."""
    print("\n=== Getting Volume ===")
    volume = client.get_volume()
    print(f"Total transactions: {volume.count}")
    print(f"Total volume: ${volume.total_transacted_usd:,.2f}")


def example_get_weekly_volume():
    """Example: Get weekly volume."""
    print("\n=== Getting Weekly Volume ===")
    weekly_volumes = client.get_weekly_volume()
    for vol in weekly_volumes[:5]:  # Show first 5 weeks
        print(f"Week {vol.week}/{vol.year}: ${vol.volume:,.2f} ({vol.count} transactions)")


def example_check_status():
    """Example: Check transaction status."""
    print("\n=== Checking Transaction Status ===")
    # Replace with an actual transaction ID
    houdini_id = "h9NpKm75gRnX7GWaFATwYn"
    try:
        status = client.get_status(houdini_id)
        print(f"Transaction: {status.houdini_id}")
        print(f"Status: {status.status.name} ({status.status.value})")
        if status.in_amount:
            print(f"Amount: {status.in_amount} {status.in_symbol}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("Houdini Swap SDK - Basic Usage Examples\n")
    print("Note: Replace API credentials in the code before running\n")
    
    try:
        example_get_tokens()
        example_get_dex_tokens()
        example_get_quote()
        example_get_min_max()
        example_get_volume()
        example_get_weekly_volume()
        example_check_status()
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure you have valid API credentials configured.")

