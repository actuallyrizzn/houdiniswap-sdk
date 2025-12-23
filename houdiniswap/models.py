"""Data models for Houdini Swap API responses."""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import IntEnum


class TransactionStatus(IntEnum):
    """Transaction status codes."""
    NEW = -1
    WAITING = 0
    CONFIRMING = 1
    EXCHANGING = 2
    ANONYMIZING = 3
    FINISHED = 4
    EXPIRED = 5
    FAILED = 6
    REFUNDED = 7
    DELETED = 8


@dataclass(frozen=True)
class Network:
    """Network/blockchain information."""
    name: str
    short_name: str
    address_validation: str
    memo_needed: bool
    explorer_url: Optional[str] = None
    address_url: Optional[str] = None
    priority: Optional[int] = None
    kind: Optional[str] = None
    chain_id: Optional[int] = None
    icon: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Network":
        """Create Network from API response."""
        return cls(
            name=data.get("name", ""),
            short_name=data.get("shortName", ""),
            address_validation=data.get("addressValidation", ""),
            memo_needed=data.get("memoNeeded", False),
            explorer_url=data.get("explorerUrl"),
            address_url=data.get("addressUrl"),
            priority=data.get("priority"),
            kind=data.get("kind"),
            chain_id=data.get("chainId"),
            icon=data.get("icon"),
        )
    
    def __repr__(self) -> str:
        return f"Network(name='{self.name}', short_name='{self.short_name}')"


@dataclass(frozen=True)
class Token:
    """Token information."""
    id: str
    name: str
    symbol: str
    network: Network
    display_name: Optional[str] = None
    icon: Optional[str] = None
    keyword: Optional[str] = None
    color: Optional[str] = None
    chain: Optional[int] = None
    address: Optional[str] = None
    has_markup: Optional[bool] = None
    network_priority: Optional[int] = None
    has_fixed: Optional[bool] = None
    has_fixed_reverse: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Token":
        """Create Token from API response."""
        network_data = data.get("network", {})
        if network_data:
            network = Network.from_dict(network_data)
        else:
            # Create a minimal network if not provided
            network = Network(
                name="",
                short_name="",
                address_validation="",
                memo_needed=False,
            )
        
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            symbol=data.get("symbol", ""),
            network=network,
            display_name=data.get("displayName"),
            icon=data.get("icon"),
            keyword=data.get("keyword"),
            color=data.get("color"),
            chain=data.get("chain"),
            address=data.get("address"),
            has_markup=data.get("hasMarkup"),
            network_priority=data.get("networkPriority"),
            has_fixed=data.get("hasFixed"),
            has_fixed_reverse=data.get("hasFixedReverse"),
        )
    
    def __repr__(self) -> str:
        return f"Token(symbol='{self.symbol}', name='{self.name}', id='{self.id}')"


@dataclass(frozen=True)
class DEXToken:
    """DEX token information."""
    id: str
    address: str
    chain: str
    decimals: int
    symbol: str
    name: str
    created: Optional[str] = None
    modified: Optional[str] = None
    enabled: Optional[bool] = None
    has_dex: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: dict) -> "DEXToken":
        """Create DEXToken from API response."""
        return cls(
            id=data.get("id", ""),
            address=data.get("address", ""),
            chain=data.get("chain", ""),
            decimals=data.get("decimals", 0),
            symbol=data.get("symbol", ""),
            name=data.get("name", ""),
            created=data.get("created"),
            modified=data.get("modified"),
            enabled=data.get("enabled"),
            has_dex=data.get("hasDex"),
        )
    
    def __repr__(self) -> str:
        return f"DEXToken(symbol='{self.symbol}', name='{self.name}', chain='{self.chain}')"


@dataclass(frozen=True)
class Quote:
    """Quote information."""
    amount_in: float
    amount_out: float
    min: Optional[float] = None
    max: Optional[float] = None
    use_xmr: Optional[bool] = None
    duration: Optional[int] = None
    device_info: Optional[str] = None
    is_mobile: Optional[bool] = None
    client_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Quote":
        """Create Quote from API response."""
        return cls(
            amount_in=data.get("amountIn", 0.0),
            amount_out=data.get("amountOut", 0.0),
            min=data.get("min"),
            max=data.get("max"),
            use_xmr=data.get("useXmr"),
            duration=data.get("duration"),
            device_info=data.get("deviceInfo"),
            is_mobile=data.get("isMobile"),
            client_id=data.get("clientId"),
        )
    
    def __repr__(self) -> str:
        return f"Quote(amount_in={self.amount_in}, amount_out={self.amount_out})"


@dataclass(frozen=True)
class DEXQuote:
    """DEX quote information."""
    swap: str
    quote_id: str
    amount_out: float
    amount_out_usd: Optional[float] = None
    duration: Optional[int] = None
    gas: Optional[int] = None
    fee_usd: Optional[float] = None
    path: Optional[List[str]] = None
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: dict) -> "DEXQuote":
        """Create DEXQuote from API response."""
        return cls(
            swap=data.get("swap", ""),
            quote_id=data.get("quoteId", ""),
            amount_out=data.get("amountOut", 0.0),
            amount_out_usd=data.get("amountOutUsd"),
            duration=data.get("duration"),
            gas=data.get("gas"),
            fee_usd=data.get("feeUsd"),
            path=data.get("path"),
            raw=data.get("raw"),
        )
    
    def __repr__(self) -> str:
        return f"DEXQuote(quote_id='{self.quote_id}', amount_out={self.amount_out}, swap='{self.swap}')"


@dataclass(frozen=True)
class ExchangeResponse:
    """Exchange transaction response."""
    houdini_id: str
    created: str
    sender_address: str
    receiver_address: str
    anonymous: bool
    expires: str
    status: int
    in_amount: float
    in_symbol: str
    out_amount: float
    out_symbol: str
    sender_tag: Optional[str] = None
    receiver_tag: Optional[str] = None
    notified: Optional[bool] = None
    eta: Optional[int] = None
    in_amount_usd: Optional[float] = None
    in_created: Optional[str] = None
    quote: Optional[Dict[str, Any]] = None
    out_token: Optional[Dict[str, Any]] = None
    in_token: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_dex: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: dict) -> "ExchangeResponse":
        """Create ExchangeResponse from API response."""
        return cls(
            houdini_id=data.get("houdiniId", ""),
            created=data.get("created", ""),
            sender_address=data.get("senderAddress", ""),
            receiver_address=data.get("receiverAddress", ""),
            anonymous=data.get("anonymous", False),
            expires=data.get("expires", ""),
            status=data.get("status", 0),
            in_amount=data.get("inAmount", 0.0),
            in_symbol=data.get("inSymbol", ""),
            out_amount=data.get("outAmount", 0.0),
            out_symbol=data.get("outSymbol", ""),
            sender_tag=data.get("senderTag"),
            receiver_tag=data.get("receiverTag"),
            notified=data.get("notified"),
            eta=data.get("eta"),
            in_amount_usd=data.get("inAmountUsd"),
            in_created=data.get("inCreated"),
            quote=data.get("quote"),
            out_token=data.get("outToken"),
            in_token=data.get("inToken"),
            metadata=data.get("metadata"),
            is_dex=data.get("isDex"),
        )
    
    def __repr__(self) -> str:
        return f"ExchangeResponse(houdini_id='{self.houdini_id}', status={self.status}, in_amount={self.in_amount})"


@dataclass(frozen=True)
class DexApproveResponse:
    """DEX approve transaction response."""
    data: str
    to: str
    from_address: str
    from_chain: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: dict) -> "DexApproveResponse":
        """Create DexApproveResponse from API response."""
        return cls(
            data=data.get("data", ""),
            to=data.get("to", ""),
            from_address=data.get("from", ""),
            from_chain=data.get("fromChain"),
        )
    
    def __repr__(self) -> str:
        return f"DexApproveResponse(to='{self.to}', from_address='{self.from_address}')"


@dataclass(frozen=True)
class Status:
    """Transaction status information."""
    houdini_id: str
    status: TransactionStatus
    created: Optional[str] = None
    sender_address: Optional[str] = None
    receiver_address: Optional[str] = None
    anonymous: Optional[bool] = None
    expires: Optional[str] = None
    in_amount: Optional[float] = None
    in_symbol: Optional[str] = None
    out_amount: Optional[float] = None
    out_symbol: Optional[str] = None
    eta: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Status":
        """Create Status from API response."""
        status_code = data.get("status", 0)
        return cls(
            houdini_id=data.get("houdiniId", ""),
            status=TransactionStatus(status_code),
            created=data.get("created"),
            sender_address=data.get("senderAddress"),
            receiver_address=data.get("receiverAddress"),
            anonymous=data.get("anonymous"),
            expires=data.get("expires"),
            in_amount=data.get("inAmount"),
            in_symbol=data.get("inSymbol"),
            out_amount=data.get("outAmount"),
            out_symbol=data.get("outSymbol"),
            eta=data.get("eta"),
        )
    
    def __repr__(self) -> str:
        return f"Status(houdini_id='{self.houdini_id}', status={self.status.name})"


@dataclass(frozen=True)
class MinMax:
    """Min-Max exchange amounts."""
    min: float
    max: float

    @classmethod
    def from_list(cls, data: List[float]) -> "MinMax":
        """Create MinMax from API response array."""
        if len(data) < 2:
            raise ValueError("MinMax requires at least 2 elements")
        return cls(min=data[0], max=data[1])
    
    def __repr__(self) -> str:
        return f"MinMax(min={self.min}, max={self.max})"


@dataclass(frozen=True)
class Volume:
    """Volume information."""
    count: int
    total_transacted_usd: float

    @classmethod
    def from_dict(cls, data: dict) -> "Volume":
        """Create Volume from API response."""
        return cls(
            count=data.get("count", 0),
            total_transacted_usd=data.get("totalTransactedUSD", 0.0),
        )
    
    def __repr__(self) -> str:
        return f"Volume(count={self.count}, total_transacted_usd={self.total_transacted_usd})"


@dataclass(frozen=True)
class DEXTokensResponse:
    """Response from get_dex_tokens() containing paginated token list."""
    count: int
    tokens: List[DEXToken]
    
    def __repr__(self) -> str:
        return f"DEXTokensResponse(count={self.count}, tokens={len(self.tokens)})"


@dataclass(frozen=True)
class WeeklyVolume:
    """Weekly volume information."""
    count: int
    anonymous: int
    volume: float
    week: int
    year: int
    commission: float

    @classmethod
    def from_dict(cls, data: dict) -> "WeeklyVolume":
        """Create WeeklyVolume from API response."""
        return cls(
            count=data.get("count", 0),
            anonymous=data.get("anonymous", 0),
            volume=data.get("volume", 0.0),
            week=data.get("week", 0),
            year=data.get("year", 0),
            commission=data.get("commission", 0.0),
        )
    
    def __repr__(self) -> str:
        return f"WeeklyVolume(week={self.week}/{self.year}, volume={self.volume}, count={self.count})"

