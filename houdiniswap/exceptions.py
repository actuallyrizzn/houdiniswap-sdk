"""Custom exceptions for the Houdini Swap SDK."""


class HoudiniSwapError(Exception):
    """Base exception for all Houdini Swap SDK errors."""
    pass


class AuthenticationError(HoudiniSwapError):
    """Raised when authentication fails."""
    pass


class APIError(HoudiniSwapError):
    """Raised when the API returns an error response."""
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ValidationError(HoudiniSwapError):
    """Raised when input validation fails."""
    pass


class NetworkError(HoudiniSwapError):
    """Raised when a network error occurs."""
    pass

