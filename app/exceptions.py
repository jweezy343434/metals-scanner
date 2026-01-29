"""
Custom exception classes for the metals scanner
"""


class MetalsScannerException(Exception):
    """Base exception for all scanner-related errors"""
    pass


class APIRateLimitError(MetalsScannerException):
    """Raised when API rate limit is exceeded"""

    def __init__(self, api_name: str, limit: int, reset_at: str = None):
        self.api_name = api_name
        self.limit = limit
        self.reset_at = reset_at
        message = f"Rate limit exceeded for {api_name} (limit: {limit})"
        if reset_at:
            message += f". Resets at: {reset_at}"
        super().__init__(message)


class APIConnectionError(MetalsScannerException):
    """Raised when API connection fails"""

    def __init__(self, api_name: str, error: str, retries: int = 0):
        self.api_name = api_name
        self.error = error
        self.retries = retries
        message = f"Failed to connect to {api_name}: {error}"
        if retries > 0:
            message += f" (after {retries} retries)"
        super().__init__(message)


class WeightExtractionError(MetalsScannerException):
    """Raised when weight cannot be extracted from listing"""

    def __init__(self, title: str, reason: str = "No valid weight pattern found"):
        self.title = title
        self.reason = reason
        super().__init__(f"Cannot extract weight from '{title}': {reason}")


class DatabaseError(MetalsScannerException):
    """Raised when database operations fail"""

    def __init__(self, operation: str, error: str):
        self.operation = operation
        self.error = error
        super().__init__(f"Database {operation} failed: {error}")


class InvalidConfigurationError(MetalsScannerException):
    """Raised when configuration is invalid"""

    def __init__(self, setting: str, reason: str):
        self.setting = setting
        self.reason = reason
        super().__init__(f"Invalid configuration for {setting}: {reason}")
