import pytest

from epicevents.exceptions import BusinessValidationError
from epicevents.security.passwords import hash_password, validate_password_strength, verify_password


def test_hash_password_returns_a_string():
    h = hash_password("S3cret!")
    assert isinstance(h, str)
    assert h != "S3cret!"


def test_verify_password_success():
    h = hash_password("S3cret!")
    assert verify_password("S3cret!", h) is True


def test_verify_password_failure():
    h = hash_password("S3cret!")
    assert verify_password("wrong", h) is False


def test_hash_password_rejects_empty_string():
    with pytest.raises(BusinessValidationError, match="Password must be a non-empty string."):
        hash_password("")


def test_validate_password_strength_accepts_valid_password():
    validate_password_strength("ValidPass1!")


@pytest.mark.parametrize(
    "password",
    ["Sec1!ab", "nouppercase1!", "NoDigitsHere!!", "NoSpecialChar1"],
)
def test_validate_password_strength_rejects_weak_passwords(password):
    with pytest.raises(BusinessValidationError, match="password must be at least 8 characters"):
        validate_password_strength(password)
