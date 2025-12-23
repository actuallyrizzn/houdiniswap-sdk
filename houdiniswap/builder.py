"""Builder pattern for constructing exchange requests."""

from typing import Optional, Dict, Any
from .client import HoudiniSwapClient
from .models import ExchangeResponse, RouteDTO
from .exceptions import ValidationError


class ExchangeBuilder:
    """Builder for constructing exchange requests."""
    
    def __init__(self, client: HoudiniSwapClient):
        """Initialize the builder with a client instance."""
        self.client = client
        self._exchange_type: Optional[str] = None  # "cex" or "dex"
        self._amount: Optional[float] = None
        self._from_token: Optional[str] = None
        self._to_token: Optional[str] = None
        self._address_to: Optional[str] = None
        self._address_from: Optional[str] = None
        self._anonymous: bool = False
        self._receiver_tag: Optional[str] = None
        self._wallet_id: Optional[str] = None
        self._ip: Optional[str] = None
        self._user_agent: Optional[str] = None
        self._timezone: Optional[str] = None
        self._use_xmr: Optional[bool] = None
        # DEX-specific
        self._swap: Optional[str] = None
        self._quote_id: Optional[str] = None
        self._route: Optional[RouteDTO] = None
    
    def cex(self) -> "ExchangeBuilder":
        """Set exchange type to CEX."""
        self._exchange_type = "cex"
        return self
    
    def dex(self) -> "ExchangeBuilder":
        """Set exchange type to DEX."""
        self._exchange_type = "dex"
        return self
    
    def amount(self, amount: float) -> "ExchangeBuilder":
        """Set exchange amount."""
        if amount <= 0:
            raise ValidationError("Amount must be greater than 0")
        self._amount = amount
        return self
    
    def from_token(self, token: str) -> "ExchangeBuilder":
        """Set source token (symbol for CEX, ID for DEX)."""
        self._from_token = self.client._sanitize_input(token, "from_token")
        return self
    
    def to_token(self, token: str) -> "ExchangeBuilder":
        """Set destination token (symbol for CEX, ID for DEX)."""
        self._to_token = self.client._sanitize_input(token, "to_token")
        return self
    
    def address_to(self, address: str) -> "ExchangeBuilder":
        """Set destination address."""
        self._address_to = self.client._sanitize_input(address, "address_to")
        return self
    
    def address_from(self, address: str) -> "ExchangeBuilder":
        """Set source address (DEX only)."""
        self._address_from = self.client._sanitize_input(address, "address_from")
        return self
    
    def anonymous(self, anonymous: bool = True) -> "ExchangeBuilder":
        """Set anonymous flag."""
        self._anonymous = anonymous
        return self
    
    def receiver_tag(self, tag: str) -> "ExchangeBuilder":
        """Set receiver tag."""
        self._receiver_tag = self.client._sanitize_input(tag, "receiver_tag")
        return self
    
    def wallet_id(self, wallet_id: str) -> "ExchangeBuilder":
        """Set wallet ID."""
        self._wallet_id = self.client._sanitize_input(wallet_id, "wallet_id")
        return self
    
    def ip(self, ip: str) -> "ExchangeBuilder":
        """Set IP address."""
        self._ip = self.client._sanitize_input(ip, "ip")
        return self
    
    def user_agent(self, user_agent: str) -> "ExchangeBuilder":
        """Set user agent."""
        self._user_agent = self.client._sanitize_input(user_agent, "user_agent")
        return self
    
    def timezone(self, timezone: str) -> "ExchangeBuilder":
        """Set timezone."""
        self._timezone = self.client._sanitize_input(timezone, "timezone")
        return self
    
    def use_xmr(self, use_xmr: bool = True) -> "ExchangeBuilder":
        """Set use XMR flag."""
        self._use_xmr = use_xmr
        return self
    
    def swap(self, swap: str) -> "ExchangeBuilder":
        """Set swap identifier (DEX only)."""
        self._swap = self.client._sanitize_input(swap, "swap")
        return self
    
    def quote_id(self, quote_id: str) -> "ExchangeBuilder":
        """Set quote ID (DEX only)."""
        self._quote_id = self.client._sanitize_input(quote_id, "quote_id")
        return self
    
    def route(self, route: RouteDTO) -> "ExchangeBuilder":
        """Set route (DEX only)."""
        if not isinstance(route, RouteDTO):
            raise ValidationError("Route must be a RouteDTO instance")
        self._route = route
        return self
    
    def _validate_cex(self) -> None:
        """Validate CEX exchange parameters."""
        if self._amount is None:
            raise ValidationError("Amount is required")
        if not self._from_token:
            raise ValidationError("from_token is required")
        if not self._to_token:
            raise ValidationError("to_token is required")
        if not self._address_to:
            raise ValidationError("address_to is required")
    
    def _validate_dex(self) -> None:
        """Validate DEX exchange parameters."""
        if self._amount is None:
            raise ValidationError("Amount is required")
        if not self._from_token:
            raise ValidationError("token_id_from is required")
        if not self._to_token:
            raise ValidationError("token_id_to is required")
        if not self._address_from:
            raise ValidationError("address_from is required")
        if not self._address_to:
            raise ValidationError("address_to is required")
        if not self._swap:
            raise ValidationError("swap is required")
        if not self._quote_id:
            raise ValidationError("quote_id is required")
        if not self._route:
            raise ValidationError("route is required")
    
    def execute(self) -> ExchangeResponse:
        """
        Execute the exchange request.
        
        Returns:
            ExchangeResponse object
            
        Raises:
            ValidationError: If required parameters are missing
            APIError: If the API returns an error
        """
        if not self._exchange_type:
            raise ValidationError("Exchange type must be set (use .cex() or .dex())")
        
        if self._exchange_type == "cex":
            self._validate_cex()
            return self.client.post_cex_exchange(
                amount=self._amount,
                from_token=self._from_token,
                to_token=self._to_token,
                address_to=self._address_to,
                anonymous=self._anonymous,
                receiver_tag=self._receiver_tag,
                wallet_id=self._wallet_id,
                ip=self._ip,
                user_agent=self._user_agent,
                timezone=self._timezone,
                use_xmr=self._use_xmr,
            )
        else:  # dex
            self._validate_dex()
            return self.client.post_dex_exchange(
                amount=self._amount,
                token_id_from=self._from_token,
                token_id_to=self._to_token,
                address_from=self._address_from,
                address_to=self._address_to,
                swap=self._swap,
                quote_id=self._quote_id,
                route=self._route,
            )

