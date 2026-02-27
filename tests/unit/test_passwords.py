from epicevents.security.passwords import hash_password, verify_password


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
    import pytest
    with pytest.raises(ValueError):
        hash_password("")