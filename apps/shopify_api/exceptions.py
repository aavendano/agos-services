class ShopifyAPIError(Exception):
    """Base exception for all Shopify API operations."""
    pass

class ShopifyAuthenticationError(ShopifyAPIError):
    """Raised when authentication fails (missing or invalid credentials/token)."""
    pass

class ShopifyRateLimitError(ShopifyAPIError):
    """Raised when Shopify throttle/rate limit is reached."""
    def __init__(self, message: str, retry_after: float = 1.0):
        super().__init__(message)
        self.retry_after = retry_after

class ShopifyGraphQLError(ShopifyAPIError):
    """Raised when GraphQL response contains errors."""
    def __init__(self, errors: list):
        self.errors = errors
        message = "; ".join(e.get("message", "Unknown GraphQL error") for e in errors)
        super().__init__(f"GraphQL Error: {message}")

class ShopifyNotFoundError(ShopifyAPIError):
    """Raised when a requested resource is not found in Shopify."""
    pass
