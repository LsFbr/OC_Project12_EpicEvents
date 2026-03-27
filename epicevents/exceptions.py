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