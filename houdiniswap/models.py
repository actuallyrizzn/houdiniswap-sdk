"""Data models for Houdini Swap API responses."""

from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
from enum import IntEnum
from decimal import Decimal

from .exceptions import ValidationError


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
    def from_dict(cls, data: Dict[str, Any]) -> "Network":
        """Create Network from API response."""
        if not isinstance(data, dict):
            raise ValidationError(f"Expected dict for Network, got {type(data).__name__}")
        
        # Validate required fields
        required_fields = ["name", "shortName", "addressValidation"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValidationError(f"Missing required fields for Network: {', '.join(missing_fields)}")
        
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
    def from_dict(cls, data: Dict[str, Any]) -> "Token":
        """Create Token from API response."""
        if not isinstance(data, dict):
            raise ValidationError(f"Expected dict for Token, got {type(data).__name__}")
        
        # Validate required fields
        required_fields = ["id", "name", "symbol", "network"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValidationError(f"Missing required fields for Token: {', '.join(missing_fields)}")
        
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
    def from_dict(cls, data: Dict[str, Any]) -> "DEXToken":
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
class RouteDTO:
    """Route DTO for DEX transactions."""
    # Route structure is complex and may vary, so we store the raw dict
    # but provide typed access to common fields
    raw: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RouteDTO":
        """Create RouteDTO from API response."""
        if not isinstance(data, dict):
            raise ValidationError(f"Expected dict for RouteDTO, got {type(data).__name__}")
        return cls(raw=data)
    
    def __repr__(self) -> str:
        return f"RouteDTO(bridge={self.raw.get('bridge', 'unknown') if isinstance(self.raw, dict) else 'N/A'})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert RouteDTO back to dictionary for API requests."""
        return self.raw


@dataclass(frozen=True)
class Quote:
    """Quote information."""
    amount_in: Decimal
    amount_out: Decimal
    min: Optional[Decimal] = None
    max: Optional[Decimal] = None
    use_xmr: Optional[bool] = None
    duration: Optional[int] = None
    device_info: Optional[str] = None
    is_mobile: Optional[bool] = None
    client_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Quote":
        """Create Quote from API response."""
        if not isinstance(data, dict):
            raise ValidationError(f"Expected dict for Quote, got {type(data).__name__}")
        
        def to_decimal(value):
            """Convert value to Decimal, handling None."""
            if value is None:
                return None
            return Decimal(str(value))
        
        return cls(
            amount_in=to_decimal(data.get("amountIn", 0)),
            amount_out=to_decimal(data.get("amountOut", 0)),
            min=to_decimal(data.get("min")),
            max=to_decimal(data.get("max")),
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
    amount_out: Decimal
    amount_out_usd: Optional[Decimal] = None
    duration: Optional[int] = None
    gas: Optional[int] = None
    fee_usd: Optional[Decimal] = None
    path: Optional[List[str]] = None
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DEXQuote":
        """Create DEXQuote from API response."""
        def to_decimal(value):
            """Convert value to Decimal, handling None."""
            if value is None:
                return None
            return Decimal(str(value))
        
        return cls(
            swap=data.get("swap", ""),
            quote_id=data.get("quoteId", ""),
            amount_out=to_decimal(data.get("amountOut", 0)),
            amount_out_usd=to_decimal(data.get("amountOutUsd")),
            duration=data.get("duration"),
            gas=data.get("gas"),
            fee_usd=to_decimal(data.get("feeUsd")),
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
    in_amount: Decimal
    in_symbol: str
    out_amount: Decimal
    out_symbol: str
    sender_tag: Optional[str] = None
    receiver_tag: Optional[str] = None
    notified: Optional[bool] = None
    eta: Optional[int] = None
    in_amount_usd: Optional[Decimal] = None
    in_created: Optional[str] = None
    quote: Optional[Quote] = None
    out_token: Optional[Token] = None
    in_token: Optional[Token] = None
    metadata: Optional[Dict[str, Any]] = None
    is_dex: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExchangeResponse":
        """Create ExchangeResponse from API response."""
        if not isinstance(data, dict):
            raise ValidationError(f"Expected dict for ExchangeResponse, got {type(data).__name__}")
        
        # Validate required fields
        required_fields = ["houdiniId", "status"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValidationError(f"Missing required fields for ExchangeResponse: {', '.join(missing_fields)}")
        
        # Parse nested objects
        quote_data = data.get("quote")
        quote = Quote.from_dict(quote_data) if quote_data and isinstance(quote_data, dict) else None
        
        out_token_data = data.get("outToken")
        out_token = Token.from_dict(out_token_data) if out_token_data and isinstance(out_token_data, dict) else None
        
        in_token_data = data.get("inToken")
        in_token = Token.from_dict(in_token_data) if in_token_data and isinstance(in_token_data, dict) else None
        
        def to_decimal(value, default=Decimal('0')):
            """Convert value to Decimal."""
            if value is None:
                return default if default is not None else None
            return Decimal(str(value))
        
        return cls(
            houdini_id=data.get("houdiniId", ""),
            created=data.get("created", ""),
            sender_address=data.get("senderAddress", ""),
            receiver_address=data.get("receiverAddress", ""),
            anonymous=data.get("anonymous", False),
            expires=data.get("expires", ""),
            status=data.get("status", 0),
            in_amount=to_decimal(data.get("inAmount", 0)),
            in_symbol=data.get("inSymbol", ""),
            out_amount=to_decimal(data.get("outAmount", 0)),
            out_symbol=data.get("outSymbol", ""),
            sender_tag=data.get("senderTag"),
            receiver_tag=data.get("receiverTag"),
            notified=data.get("notified"),
            eta=data.get("eta"),
            in_amount_usd=to_decimal(data.get("inAmountUsd"), default=None),
            in_created=data.get("inCreated"),
            quote=quote,
            out_token=out_token,
            in_token=in_token,
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
    def from_dict(cls, data: Dict[str, Any]) -> "DexApproveResponse":
        """Create DexApproveResponse from API response."""
        if not isinstance(data, dict):
            raise ValidationError(f"Expected dict for DexApproveResponse, got {type(data).__name__}")
        
        # Validate required fields
        required_fields = ["data", "to", "from"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValidationError(f"Missing required fields for DexApproveResponse: {', '.join(missing_fields)}")
        
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
    def from_dict(cls, data: Dict[str, Any]) -> "Status":
        """Create Status from API response."""
        if not isinstance(data, dict):
            raise ValidationError(f"Expected dict for Status, got {type(data).__name__}")
        
        # Validate required fields
        required_fields = ["houdiniId", "status"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValidationError(f"Missing required fields for Status: {', '.join(missing_fields)}")
        
        status_code = data.get("status", 0)
        try:
            status_enum = TransactionStatus(status_code)
        except ValueError:
            raise ValidationError(f"Invalid transaction status code: {status_code}")
        
        return cls(
            houdini_id=data.get("houdiniId", ""),
            status=status_enum,
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
    min: Decimal
    max: Decimal

    @classmethod
    def from_list(cls, data: List[Union[float, str, Decimal, int]]) -> "MinMax":
        """Create MinMax from API response array."""
        if len(data) < 2:
            raise ValueError("MinMax requires at least 2 elements")
        return cls(
            min=Decimal(str(data[0])),
            max=Decimal(str(data[1]))
        )
    
    def __repr__(self) -> str:
        return f"MinMax(min={self.min}, max={self.max})"


@dataclass(frozen=True)
class Volume:
    """Volume information."""
    count: int
    total_transacted_usd: Decimal

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Volume":
        """Create Volume from API response."""
        return cls(
            count=data.get("count", 0),
            total_transacted_usd=Decimal(str(data.get("totalTransactedUSD", 0))),
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
    volume: Decimal
    week: int
    year: int
    commission: Decimal

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WeeklyVolume":
        """Create WeeklyVolume from API response."""
        return cls(
            count=data.get("count", 0),
            anonymous=data.get("anonymous", 0),
            volume=Decimal(str(data.get("volume", 0))),
            week=data.get("week", 0),
            year=data.get("year", 0),
            commission=Decimal(str(data.get("commission", 0))),
        )
    
    def __repr__(self) -> str:
        return f"WeeklyVolume(week={self.week}/{self.year}, volume={self.volume}, count={self.count})"

