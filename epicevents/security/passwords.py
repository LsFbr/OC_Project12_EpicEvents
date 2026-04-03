import re

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from epicevents.exceptions import BusinessValidationError

_ph = PasswordHasher()

# At least 8 chars, uppercase, digit, non-alphanumeric non-space ("special").
_PASSWORD_POLICY = re.compile(
    r"(?=.{8,})(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9\s]).+"
)
_PASSWORD_POLICY_ERROR = (
    "password must be at least 8 characters long and contain at least one uppercase letter, "
    "one digit, and one special character"
)


def validate_password_strength(plain_password: str) -> None:
    pwd = plain_password if isinstance(plain_password, str) else ""
    if not _PASSWORD_POLICY.fullmatch(pwd):
        raise BusinessValidationError(_PASSWORD_POLICY_ERROR)


def hash_password(plain_password: str) -> str:
    if not isinstance(plain_password, str) or not plain_password.strip():
        raise BusinessValidationError("Password must be a non-empty string.")
    return _ph.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return _ph.verify(password_hash, plain_password)
    except VerifyMismatchError:
        return False
