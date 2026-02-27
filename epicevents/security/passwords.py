from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_ph = PasswordHasher()


def hash_password(plain_password: str) -> str:
    if not isinstance(plain_password, str) or not plain_password.strip():
        raise ValueError("Password must be a non-empty string.")
    return _ph.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return _ph.verify(password_hash, plain_password)
    except VerifyMismatchError:
        return False