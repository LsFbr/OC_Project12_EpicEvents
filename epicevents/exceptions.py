class ConfigurationError(RuntimeError):
    """Raised when a configuration error occurs."""
    pass


class BusinessValidationError(ValueError):
    """Raised for expected business validation errors."""
    pass


class BusinessAuthorizationError(PermissionError):
    """Raised for expected business authorization errors."""
    pass


class AuthenticationError(ValueError):
    """Raised when authentication fails."""
    pass


class NotLoggedInError(AuthenticationError):
    """Raised when no token is available."""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when email/password is invalid."""
    pass


class TokenExpiredError(AuthenticationError):
    """Raised when JWT token is expired."""
    pass


class InvalidAuthTokenError(AuthenticationError):
    """Raised when JWT token is invalid."""
    pass


class UserNotFoundError(AuthenticationError):
    """Raised when token points to a deleted user."""
    pass